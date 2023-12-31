from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import re
from pymongo import MongoClient
from config import CONNECTION_STRING

url = "https://bulletin.engin.umich.edu/courses/eecs/"
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

request = Request(url, headers=headers)
response = urlopen(request)

html_bytes = response.read()
html = html_bytes.decode("utf-8")
# print(html) 

client = MongoClient(CONNECTION_STRING)
db = client['course_database'] # name here
collection = db['course_collection']  # collection name here

soup = BeautifulSoup(html, 'html.parser')
paragraphs = soup.find_all('p')

def parse_elements(para, ele):
    print(ele)
    for i in range(len(ele) - 1):
        
        start_index = para.find(ele[i]) + len(ele[i])
        end_index = para.find(ele[i + 1])

        # Check if there's text between <em> 
        
        if start_index < end_index:
            text = ele[start_index:end_index].strip()
            ele.insert(text, i)
    return ele

def extract_prerequisite_codes(text):
    # Define a regular expression pattern to match course codes
    code_pattern = re.compile(r'([A-Z]+\s\d{3}|\b\d{3}\b)')

    # Identify if it's a prerequisite or accompanied code based on keywords
    prerequisite_keywords = ['Prerequisite']
    preceded_accompanied_keywords = ['Preceded or accompanied by']

    prereq_codes = []
    accompanied_codes = []

    # Check for advisory prerequisites
    if any(keyword in text for keyword in prerequisite_keywords):
        # Extract prerequisite codes within the same sentence
        sentence = text.split('.')
        for s in sentence:
            if any(keyword in s for keyword in prerequisite_keywords):
                codes_in_sentence = code_pattern.findall(s)
                inner_list = []
                stored_word = ''

                for code in codes_in_sentence:
                    if ' ' in code:
                        stored_word = code.split()[0]
                        inner_list.append(code)
                    else:
                        inner_list.append(stored_word + ' ' + code)

                    # Check for 'and' keyword or end of sentence to append the inner list
                    if 'and' in code.lower():
                        prereq_codes.append(inner_list.copy())
                        inner_list.clear()
                    elif code == codes_in_sentence[-1]:
                        prereq_codes.append(inner_list.copy())


    # Check for preceded or accompanied by
    if any(keyword in text for keyword in preceded_accompanied_keywords):
        # Extract accompanied code within the same sentence
        sentence = text.split('.')
        for s in sentence:
            if any(keyword in s for keyword in preceded_accompanied_keywords):
                codes_in_sentence = code_pattern.findall(s)
                inner_list = []

                for code in codes_in_sentence:
                    if ' ' in code:
                        stored_word = code.split()[0]
                        inner_list.append(stored_word)
                    else:
                        inner_list.append(stored_word + ' ' + code)

                    # Check for 'and' keyword or end of sentence to append the inner list
                    if 'and' in code.lower():
                        accompanied_codes.append(inner_list.copy())
                        inner_list.clear()
                    elif code == codes_in_sentence[-1]:
                        accompanied_codes.append(inner_list.copy())

    return prereq_codes, accompanied_codes

# Iterate through each paragraph
def parse_para():
    for paragraph in paragraphs[1:]:
        # Find strong and em elements within the current paragraph
        strong_elements = paragraph.find_all('strong')
        em_elements = paragraph.find_all('em')

        if strong_elements and em_elements:
            strong_text = ' '.join(strong.text.strip() for strong in strong_elements)
            print(strong_text)

            em_text = em_elements[0].text.strip()
            for i in range(1, len(em_elements)):
                if i <= len(em_elements) - 1:
                    between = em_elements[i-1].find_next_sibling(string=True)
                    text_between = between.text.strip() if between else ''
                em_text += text_between
                em_text += em_elements[i].text.strip()

            # print(em_text)

            c_match = re.search(r"\((\S+)\s+credits\)", em_text)
            credits = c_match.group(1) if c_match else None
                # print(credits)
            adv_match = re.search(r"Advisory Prerequisite:\s*(.*?)\.", em_text)
            advisory_text = adv_match.group(1).strip() if adv_match else None
                # print(advisory_text)
            enf_match = re.search(r"Enforced Prerequisite:\s*(.*?)\.", em_text)
            enforced_text = enf_match.group(1).strip() if enf_match else None

            prereq_codes, accompanied_codes = extract_prerequisite_codes(em_text)
            # print(prereq_codes, accompanied_codes)
            
            course = {
                'code': strong_text.split('.')[0],
                'name': strong_text,
                'prereq': em_text,
                'prereq_codes': prereq_codes,
                'accompanied_codes': accompanied_codes,
                'advisory': advisory_text if advisory_text else None,
                'enforced': enforced_text if enforced_text else None,
                'credits': credits
            }
            # print(course)
            collection.insert_one(course)

        # print("\n")
parse_para()
client.close()
