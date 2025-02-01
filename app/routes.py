from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from flask_login import login_user, login_required, logout_user, current_user
from app import db, login_manager
from app.models import User

# Define Blueprint
main = Blueprint('main', __name__)

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
