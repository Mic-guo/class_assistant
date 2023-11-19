import spacy
from pymongo import MongoClient
from config import CONNECTION_STRING

def extract_prerequisites(course_description):
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(course_description)

    prerequisite_keywords = ["Prerequisite", "Advisory Prerequisite", "Preceded or accompanied by"]

    prerequisite_courses = []

    for sentence in doc.sents:
        for keyword in prerequisite_keywords:
            if keyword in sentence.text:
                for token in sentence:
                    if token.ent_type_ == "COURSE":
                        prerequisite_courses.append(token.text)

    return prerequisite_courses

def get_todo_courses(desired_course_str, completed_courses_str):
    # Connect to MongoDB
    client = MongoClient(CONNECTION_STRING)
    db = client['course_database']  # Update with your database name
    collection = db['course_collection']  # Update with your collection name

    completed_courses = [code.strip() for code in completed_courses_str.split(",")]
    desired_course_code = re.search(r'([A-Z]+\s\d{3})', desired_course_str).group(1)
    desired_course_data = collection.find_one({"code": desired_course_code})

    todo_courses = []

    def find_todo_courses(course_data):
        if course_data:
            prereq_courses = extract_prerequisites(course_data.get("prereq", ""))
            
            for prereq_code in prereq_courses:
                if prereq_code in completed_courses or any(prereq_code in inner_list for inner_list in todo_courses):
                    break
                todo_courses.append([prereq_code])
                
            for prereq_code in prereq_courses:
                prereq_data = collection.find_one({"code": prereq_code})
                find_todo_courses(prereq_data)

    find_todo_courses(desired_course_data)
    client.close()

    return todo_courses

def print_todo(todo_courses):
    result = ", ".join([" or ".join(inner_list) for inner_list in todo_courses])
    return result

# Example usage
desired_course_str = "EECS 280"
completed_courses_str = "ENGR 100, EECS 189"

todo_courses = get_todo_courses(desired_course_str, completed_courses_str)
print_todo(todo_courses)
