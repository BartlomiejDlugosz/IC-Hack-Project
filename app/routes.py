from flask import Blueprint, render_template, redirect, url_for, request, flash, session, jsonify
import os
import openai
from flask_login import login_user, login_required, logout_user, current_user
from dotenv import load_dotenv
from app import db, login_manager
from app.models import User, Course
import json

from openai_integration import askGPT
import json

# Load environment variables from .env file
load_dotenv()

# Define Blueprint
main = Blueprint('main', __name__)
openai.api_key = os.getenv('OPENAIAPI_KEY')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@main.route('/')
def home():
    return render_template('index.html')

@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return redirect(url_for('main.register'))

        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('main.login'))

    return render_template('register.html')

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            session['username'] = username
            flash('Logged in successfully!', 'success')
            return redirect(url_for('main.dashboard'))

        flash('Invalid username or password', 'danger')

    return render_template('login.html')

@main.route('/dashboard')
@login_required
def dashboard():
    username = current_user.username
    interest = current_user.key_interest
    courses = Course.query.filter_by(author_id=current_user.id).all()
    return render_template('dashboard.html', courses=courses, interest=interest, username=username)

@main.route('/logout')
@login_required
def logout():
    session.pop('username', None)
    logout_user()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('main.home'))


# All methods for courses ---------------------
@main.route('/course/create', methods=['GET', 'POST'])
@login_required
def create_course():
    print(request)
    interest = current_user.key_interest
    print(interest)
    if request.method == 'POST':
        name = request.form['name']
        difficulty_matrix = request.form['difficulty_matrix']
        description = request.form['description']
        content = request.form['content']
        questions = request.form['questions']
        # interest = request.form['interest']
        prompt_analogy = f"Explain {name} using an analogy related to . Make it simple and engaging."
        print('Prompt Prompt')
        print(prompt_analogy)
        analogy = askGPT(f"Create the table of content for the following prompt to learn the topic, do not add bolding {prompt_analogy}", prompt_analogy)
        # Create the new course with the logged-in user as the author
        new_course = Course(
            name=name,
            difficulty_matrix=difficulty_matrix,
            description=description,
            content=analogy,
            questions=questions,
            author_id=current_user.id  # Set the author_id to the current user's ID
        )

        db.session.add(new_course)
        db.session.commit()
        flash('Course created successfully!', 'success')
        return redirect(url_for('main.dashboard'))
    return render_template('courses/create_course.html')

@main.route('/course/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_course(id):
    course = Course.query.get_or_404(id)

    # Ensure the current user is the author of the course
    if course.author_id != current_user.id:
        flash('You do not have permission to edit this course.', 'danger')
        return redirect(url_for('main.view_courses'))

    if request.method == 'POST':
        course.name = request.form['name']
        course.difficulty_matrix = request.form['difficulty_matrix']
        course.description = request.form['description']
        course.content = request.form['content']
        course.questions = request.form['questions']

        db.session.commit()
        flash('Course updated successfully!', 'success')
        return redirect(url_for('main.view_course', id=course.id))

    return render_template('courses/edit_course.html', course=course)

@main.route('/courses')
def view_courses():
    courses = Course.query.all()
    return render_template('courses/view_courses.html', courses=courses)

@main.route('/course/<int:id>')
def view_course(id):
    course = Course.query.get_or_404(id)
    return render_template('courses/view_course_detail.html', course=course)

@main.route('/course/delete/<int:id>', methods=['POST'])
def delete_course(id):
    # Your delete logic here
    course = Course.query.get_or_404(id)
    db.session.delete(course)
    db.session.commit()
    flash('Course deleted successfully', 'success')
    return redirect(url_for('main.dashboard'))

# Creating the prompting.
@main.route('/generate-analogy', methods=['POST'])
def generate_analogy():
    data = request.json
    interest = data.get('interest')
    concept = data.get('concept')

    # Prompt for generating the analogy
    prompt_analogy = f"Explain {concept} using an analogy related to {interest}. Make it simple and engaging."

    # Prompt for generating the quiz based on the analogy
    prompt_quiz = f"""
    Based on the analogy you provided for {concept}, create a multiple-choice question in the following format:
    Question: [Your question here]
    A) Option A
    B) Option B
    C) Option C
    D) Option D
    Correct Answer: [Specify A, B, C, or D]
    Make sure to follow this format exactly to ensure proper parsing.
    """

    try:
        # Generate the analogy
        analogy = askGPT("""You are an expert teacher specializing in making complex concepts easy to understand using real-life analogies.
        You will return the analogy based on the concept and interest provided in a JSON format in this style:
        {
            "analogy": "Your analogy here"
        }""",
                                  prompt_analogy)

        quiz_text = askGPT("""You are an expert teacher who generates quiz questions based on explanations.
        You will return a multiple-choice question based on the analogy provided in a JSON format in this style:
        {
            "question": "Your question here",
            "options": [
                "A": "Your options here",
                "B": "Your options here",
                "C": "Your options here",
                "D": "Your options here"
            ],
            "correct_answer": "Correct answer here"
        }""",
                           f"{prompt_analogy}\n\n{analogy}\n\n{prompt_quiz}")
        print(analogy)
        print(quiz_text)

        return jsonify({
            'analogy': json.loads(analogy)["analogy"],
            'quiz': json.loads(quiz_text)
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Creating the prompting.
@main.route('/create-analogy', methods=['POST'])
def create_analogy():
    data = request.json
    interest = data.get('interest')
    concept = data.get('concept')

    # Prompt for generating the analogy
    prompt_analogy = f"Explain {concept} using an analogy related to {interest}. Make it simple and engaging."
    try:
        analogy = askGPT("You are an expert teacher specializing in making complex concepts easy to understand using real-life analogies.",
                                  prompt_analogy)

        # Extracting values from the JSON object

        new_course = Course(
            name='test',  # The title from the split content
            difficulty_matrix='test',  # The difficulty description from the split content
            description='',  # The short description from the split content
            content=analogy,  # Set the analogy as the course content
            questions='quiz_text',  # Set the generated quiz text as the questions
            author_id=current_user.id  # Ensure this is the current logged-in user's ID
        )
        db.session.add(new_course)
        db.session.commit()
        return ''


    except Exception as e:
        return jsonify({'error': str(e)}), 500
