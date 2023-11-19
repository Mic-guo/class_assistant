#app.py
from pymongo import MongoClient
from config import CONNECTION_STRING
import re

def get_todo_courses(desired_course_str, completed_courses_str):
    # Connect to MongoDB
    client = MongoClient(CONNECTION_STRING)
    db = client['course_database'] # name here
    collection = db['course_collection']  # collection name here
    print(collection)
    completed_courses = [code.strip() for code in completed_courses_str.split(',')]
    desired_course_code = re.search(r'([A-Z]+\s\d{3})', desired_course_str).group(1)
    desired_course_data = collection.find_one({"code": desired_course_code})

    todo_courses = []

    # Helper function to recursively find to do courses
    def find_todo_courses(course_data):
        if course_data:
            prereq_codes = course_data.get("prereq_codes", [])

            for prereq_code in prereq_codes[0]:
                # If the prereq code is not in completed courses and not in the to-do list, add it
                if prereq_code in completed_courses or any(prereq_code in inner_list for inner_list in todo_courses):
                    break
                todo_courses.append(prereq_codes[0])
            # Recursively find to-do courses for the current prereq code
            prereq_data = collection.find_one({"code": prereq_code})
            find_todo_courses(prereq_data)

    find_todo_courses(desired_course_data)
    client.close()

    return todo_courses

def print_todo(todo_courses):
    result = ', '.join([' or '.join(inner_list) for inner_list in todo_courses])
    return result
    

# Example usage
desired_course_str = "EECS 280"
completed_courses_str = "ENGR 100, EECS 189"

todo_courses = get_todo_courses(desired_course_str, completed_courses_str)
print(print_todo(todo_courses))

