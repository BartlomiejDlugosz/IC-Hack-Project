from flask import Blueprint, render_template, redirect, url_for, request, flash, session, jsonify
import openai
from flask_login import login_user, login_required, logout_user, current_user
from app import db, login_manager
from app.models import User
import os
from dotenv import load_dotenv
import json

from openai_integration import askGPT

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
    return f'Hello, {current_user.username}! Welcome to your dashboard. <a href="/logout">Logout</a>'

@main.route('/logout')
@login_required
def logout():
    session.pop('username', None)
    logout_user()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('main.home'))

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
