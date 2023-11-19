# app.py
from flask import Flask, render_template
from course_searcher import todo_courses  # Import your Python file or module

app = Flask(__name__)

@app.route('/')
def index():
    data = todo_courses()  # Assuming your Python file has a function to get data
    return render_template('index.html', data=data)

if __name__ == '__main__':
    app.run(debug=True)
