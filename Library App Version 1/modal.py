from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()
import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    profile = db.Column(db.String(200))
    token = db.Column(db.Integer, default=5)

class Section(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date_created = db.Column(db.Date,nullable=False)
    description = db.Column(db.Text)

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text)
    author = db.Column(db.String(100), nullable=False)
    date_issued = db.Column(db.Date,nullable=True)
    profile = db.Column(db.String(200))
    return_date = db.Column(db.Date,nullable=True)
    availability = db.Column(db.Integer, default=1)
    section_id = db.Column(db.Integer, db.ForeignKey('section.id'), nullable=False)
    section = db.relationship('Section', backref=db.backref('books', lazy=True))

class UserBook(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    issue_date = db.Column(db.Date,nullable=False)
    return_date = db.Column(db.Date,nullable=False)

    user = db.relationship('User', backref=db.backref('user_books', lazy=True))
    book = db.relationship('Book', backref=db.backref('user_books', lazy=True))

class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    comment = db.Column(db.Text)
    rating = db.Column(db.Integer)

    user = db.relationship('User', backref=db.backref('feedbacks', lazy=True))
    book = db.relationship('Book', backref=db.backref('feedbacks', lazy=True))