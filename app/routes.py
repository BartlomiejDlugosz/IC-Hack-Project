from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from flask_login import login_user, login_required, logout_user, current_user
from app import db, login_manager
from app.models import User, Course

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
    courses = Course.query.filter_by(author_id=current_user.id).all()
    return render_template('dashboard.html', courses=courses)

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
    if request.method == 'POST':
        name = request.form['name']
        difficulty_matrix = request.form['difficulty_matrix']
        description = request.form['description']
        content = request.form['content']
        questions = request.form['questions']

        # Create the new course with the logged-in user as the author
        new_course = Course(
            name=name,
            difficulty_matrix=difficulty_matrix,
            description=description,
            content=content,
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
