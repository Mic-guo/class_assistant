from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from ics import Calendar, Event
from ics.grammar.parse import ContentLine
from course import Course
import re
import json
import arrow
import os
import time


# TODO: check if Schedule Builder is offline for scheduled maintenance. It will return online at 7:30 AM.

def document_initialised(driver):
    return driver.execute_script("return initialised")


def login(driver, uniqname, password):
    # TODO: prevent usage inside maintenence hours
    login_button = WebDriverWait(driver, timeout=10).until(
        lambda d: d.find_element(by=By.LINK_TEXT, value="Log in"))
    if (login_button):
        print("Log in button found.")
        login_button.click()

        uniqname_field = WebDriverWait(driver, timeout=3).until(
            lambda d: d.find_element(by=By.ID, value="username"))
        password_field = WebDriverWait(driver, timeout=3).until(
            lambda d: d.find_element(by=By.ID, value="password"))
        weblogin_button = WebDriverWait(driver, timeout=3).until(
            lambda d: d.find_element(by=By.ID, value="loginSubmit"))

        uniqname_field.send_keys(uniqname)
        password_field.send_keys(password)
        weblogin_button.click()

        # <button tabindex="2" type="submit" class="positive auth-button"><!-- -->Send Me a Push </button>
        # <div class="example class with spaces">This is the element with spaces</div>

        driver.switch_to.frame('duo_iframe')
        duo_button = WebDriverWait(driver, timeout=3).until(
            lambda d: d.find_element(by=By.CLASS_NAME, value="auth-button"))
        duo_button = driver.find_element(By.CLASS_NAME, "auth-button")
        duo_button.click()
        print("Duo push sent to phone.")

        time.sleep(15)
        # try: 
        driver.get("https://atlas.ai.umich.edu/my-dashboard/")
        WebDriverWait(driver, timeout=100).until(
            lambda d: d.find_element(by=By.CLASS_NAME, value="nav-bar-links"))
        print("Login successful.")

    else:
        print("Log in button not found.")


def get_courses(driver, schedule_name):
    # navigate to Schedule Builder
    # get Academic Term from user
    term_select = WebDriverWait(driver, timeout=3).until(
        lambda d: d.find_element(by=By.CSS_SELECTOR, value=".dropdown"))

    # Select Academic Term form dropdown
    term_select.click()
    # Check if dropdown item is present
    WebDriverWait(driver, timeout=3).until(
        EC.presence_of_element_located((By.XPATH, "(/html/body/div[1]/div/div/div/div[2]/div[1]/div/select/option)[2]")))
    term_select.send_keys(Keys.ARROW_DOWN, Keys.ENTER)
    # Get specified schedule
    schedules = WebDriverWait(driver, timeout=3).until(
        lambda d: d.find_elements(by=By.CSS_SELECTOR, value=".text-xsmall .pill-btn-tertiary"))
    for schedule in schedules:
        if schedule_name in schedule.get_attribute("innerHTML"):
            schedule.click()
            break
    print(f"Schedule \"{schedule_name}\" found.")

    # TODO wait for all courses to load with data

    # build list of courses
    courses = []
    course_cards_list = WebDriverWait(driver, timeout=3).until(
        lambda d: d.find_elements(by=By.CSS_SELECTOR, value=".sb-course-card-container"))
    for course in course_cards_list:
        title = course.find_element(
            by=By.CSS_SELECTOR, value=".course-code-and-filter .text-xsmall").get_attribute("innerHTML").strip()
        # iterate through sections
        section_lists = WebDriverWait(course, timeout=120).until(
            lambda d: d.find_elements(by=By.CSS_SELECTOR, value=".course-section-details"))
        for section in section_lists:
            # skip if date == "Days TBA" or section title contains "MID"
            section_type_raw = section.find_element(
                by=By.CSS_SELECTOR, value=".course-section-details .row .row .regular").get_attribute("innerHTML")

            # get type
            name_reg = r'\(([A-Z]+)\)'
            name_match = re.search(name_reg, section_type_raw)
            section_type = name_match.group(1)
            if section_type == "MID":
                continue
            section_name = section.find_element(
                by=By.CSS_SELECTOR, value=".dropdown-label").get_attribute("innerHTML")
            section_reg = r'\W(\d{3})\W'
            section_match = re.search(section_reg, section_name)
            section_num = section_match.group(1)

            try:
                section_time = section.find_element(
                    by=By.CSS_SELECTOR, value=".section-time").get_attribute("innerHTML")
            except:
                print(
                    f"Program crashed. No section selected for {section_name}-{section_type}.")
                quit()

            # get time start
            # get time end
            # get days
            time_reg = r'([\d]+:[\d]+\W[\w]+) - ([\d]+:[\d]+\W[\w]+) \| ([\w]+[ \w]*)'
            time_match = re.search(time_reg, section_time)
            start_time = time_match.group(1)
            end_time = time_match.group(2)
            days = time_match.group(3)
            if "Days TBA" in days:
                continue
            else:
                days_reg = r'[A-Z][a-z]{0,1}'
                days_list = re.findall(days_reg, days)

            # get location
            location = section.find_element(
                by=By.CSS_SELECTOR, value=".section-time+ .text-xsmall").get_attribute("innerText").strip()

            course = Course(title, section_type, section_num,
                            days_list, start_time, end_time, location)
            courses.append(course)
    print("Finished scraping courses.")
    return courses


def create_calendar(courses, uniqname, term_start_date_string):
    term_start_date_notz = arrow.get(term_start_date_string, "MM-DD-YYYY")
    c = Calendar()
    for course in courses:
        # print(course.timeStart)
        e = Event()
        event_name = f"{course.name}-{course.secNum}: {course.type}"
        e.name = event_name
        e.location = course.location

        # create list of weekdays as num
        # get days to repeat
        weekdays_num = []
        days = []
        for day in course.days:
            match day:
                case "M":
                    weekdays_num.append(0)
                    days.append("MO")
                case "T":
                    weekdays_num.append(1)
                    days.append("TU")
                case "W":
                    weekdays_num.append(2)
                    days.append("WE")
                case "Th":
                    weekdays_num.append(3)
                    days.append("TH")
                case "F":
                    weekdays_num.append(4)
                    days.append("FR")

        days_csv = ",".join(days)
        e.extra.append(ContentLine(
            name="RRULE", value=f"FREQ=WEEKLY;COUNT={15*len(course.days)};WKST=SU;BYDAY={days_csv}"))
        # find min "largest" weekday
        course_first_weekday = weekdays_num[0]
        for n in reversed(weekdays_num):
            if n - term_start_date_notz.weekday() >= 0:
                course_first_weekday = n

        # shift course_begin and course_end
        course_begin_time = arrow.Arrow.strptime(course.timeStart, "%I:%M %p")
        course_end_time = arrow.Arrow.strptime(course.timeEnd, "%I:%M %p")

        course_begin = arrow.Arrow(year=term_start_date_notz.year,
                                   month=term_start_date_notz.month,
                                   day=term_start_date_notz.day,
                                   hour=course_begin_time.time().hour,
                                   minute=course_begin_time.time().minute,
                                   tzinfo='US/Eastern')
        if course_first_weekday - term_start_date_notz.weekday() < 0:
            course_begin = course_begin.shift(
                days=(7+course_first_weekday - term_start_date_notz.weekday()))
        else:
            course_begin = course_begin.shift(
                days=(course_first_weekday - term_start_date_notz.weekday()))

        course_end = arrow.Arrow(year=course_begin.year,
                                 month=course_begin.month,
                                 day=course_begin.day,
                                 hour=course_end_time.time().hour,
                                 minute=course_end_time.time().minute,
                                 tzinfo='US/Eastern')
        e.begin = course_begin
        e.end = course_end

        c.events.add(e)

    filename = f"UM Classes - {uniqname}.ics"
    with open("temp_cal.txt", 'w') as f:
        f.writelines(c.serialize_iter())
    with open("temp_cal.txt", "r") as f, open(filename, "w") as outfile:
        for i in f.readlines():
            if not i.strip():
                continue
            if i:
                outfile.write(i)
    print(f"\"{filename}\" exported")
    os.remove("temp_cal.txt")

#    id="v-0-vue-combo-blocks-input"
def get_course_statistics(driver, course):
    search_bar = WebDriverWait(driver, timeout=10).until(
        lambda d: d.find_element(by=By.ID, value="v-0-vue-combo-blocks-input"))
    if (search_bar):
        print("Search bar found")
        search_bar.send_keys(course)
        search_bar.send_keys(Keys.RETURN)

        time.sleep(3)

        # Course Evaluations 
        print("### Course Evaluations #############################")
        desireToTake = WebDriverWait(driver, timeout=3).until(
            lambda d: d.find_element(By.CSS_SELECTOR, ".text-smed.eval-stat.desire-highlight")).text
        understanding = WebDriverWait(driver, timeout=3).until(
            lambda d: d.find_element(By.CSS_SELECTOR, ".text-smed.eval-stat.understanding-highlight")).text
        workload = WebDriverWait(driver, timeout=3).until(
            lambda d: d.find_element(By.CSS_SELECTOR, ".text-smed.eval-stat.workload-highlight")).text
        expectations = WebDriverWait(driver, timeout=3).until(
            lambda d: d.find_element(By.CSS_SELECTOR, ".text-smed.eval-stat.expectations-highlight")).text
        increasedInterest = WebDriverWait(driver, timeout=3).until(
            lambda d: d.find_element(By.CSS_SELECTOR, ".text-smed.eval-stat.increased-interest-highlight")).text
        print("Desire to Take: " + desireToTake + "\n" + 
              "Understanding: " + understanding + "\n" + 
              "Workload: " + workload + "\n" + 
              "Expectations: " + expectations + "\n" + 
              "Increased Interest: " + increasedInterest)
        
        # Median Grade
        print("### Median Grade ###################################")
        medianGrade = driver.find_element(By.CLASS_NAME, "grade-median.text-smed.bold") \
                            .find_element(By.CLASS_NAME, "blue-highlight-text").text
        print (medianGrade)

        # Incoming Student level
        print("###  Incoming Student Level  #######################")
        islElement = driver.find_element(By.ID, "student-level")

        level_text = islElement.find_element(By.CLASS_NAME, 'yaxislayer-above') \
                               .find_elements(By.CLASS_NAME, 'ytick')
        text_contents = [element.text for element in level_text]

        level_percents = islElement.find_element(By.CLASS_NAME, 'points') \
                             .find_elements(By.CLASS_NAME, 'point')
        num_contents = [element.text for element in level_percents]

        islOutput = []
        for level, percent in zip(text_contents[::-1], num_contents[::-1]):
            islOutput.append(level)
            islOutput.append(percent)

        print(islOutput)

        # Enrollment Sequence 
        escElement = driver.find_element(By.CLASS_NAME, 'enrollment-sequence-container')

        print("###  Classes Taken Before  #########################")
        ctbElt = escElement.find_element(By.CSS_SELECTOR, '.pre.enrollment-container') \
                           .find_elements(By.CLASS_NAME, 'text-small')
                            #.find_element(By.CLASS_NAME, 'course-bookmark-container') \
        weird_ctbText = [element.text for element in ctbElt]
        ctbText = [s for s in weird_ctbText if s.strip() != ""]
        print(ctbText[:-2])

        print("###  Classes Taken With  ###########################")
        ctwElt = escElement.find_element(By.CSS_SELECTOR, '.co.enrollment-container')\
                           .find_elements(By.CLASS_NAME, 'text-small')
        weird_ctwText = [element.text for element in ctwElt]
        ctwText = [s for s in weird_ctwText if s.strip() != ""]
        print(ctwText[:-2])

        print("###  Classes Taken After  ##########################")
        ctaElt = escElement.find_element(By.CSS_SELECTOR, '.post.enrollment-container')\
                           .find_elements(By.CLASS_NAME, 'text-small')
        weird_ctaText = [element.text for element in ctaElt]
        ctaText = [s for s in weird_ctaText if s.strip() != ""]
        print(ctaText[:-2])

    #TODO: 
        # print("###  School/College Affiliation  ###################")
        # print("###  Declared Degrees ##############################")


    else:
        print("Search bar not found")
    return None

f = open('secret.json')
data = json.load(f)
uniqname = data["uniqname"]
password = data["password"]
schedule_name = data["schedule_name"]
term_start_date = data["term_start_date"]


chrome_options = Options()
chrome_options.add_experimental_option("detach", True)
chrome_options.add_experimental_option(
    'excludeSwitches', ['enable-logging'])
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument('--ignore-certificate-errors')
chrome_options.add_argument('--allow-running-insecure-content')
chrome_options.add_argument("--enable-javascript")
#chrome_options.add_argument('--headless')

service = Service(executable_path='/usr/bin/chromedriver')

driver = webdriver.Chrome(service = service, options=chrome_options)

driver.get("https://atlas.ai.umich.edu/")
login(driver, uniqname, password)
get_course_statistics(driver, "EECS 485")

# isProductionMode = 1
# if (isProductionMode):
#     driver.get("https://atlas.ai.umich.edu/")
#     login(driver, uniqname, password)

#     driver.get("https://atlas.ai.umich.edu/schedule-builder/")
# else:
#     driver.get(
#         r"C:\Users\k3vnx\Documents\GitHub\atlas-to-ics\testing\Atlas-schedule-builder-winter2023.html")
# courses = get_courses(driver, schedule_name)
# create_calendar(courses, uniqname, term_start_date)

driver.quit()

