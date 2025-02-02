from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    section_score = db.Column(db.Float, nullable=True)  # Stores scores, can be NULL
    key_interest = db.Column(db.String(255), nullable=True)  # Stores user interests
    # Correct relationship with back_populates
    courses = db.relationship('Course', back_populates='author', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    difficulty_matrix = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    content = db.Column(db.Text, nullable=False)
    questions = db.Column(db.Text, nullable=False)

    # Correct ForeignKey reference to User's id
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Correct relationship with back_populates
    author = db.relationship('User', back_populates='courses')

    def __repr__(self):
        return f'<Course {self.name}>'
