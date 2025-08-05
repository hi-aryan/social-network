from flasknetwork import db, login_manager
from itsdangerous import URLSafeTimedSerializer as Serializer
from flask import current_app
from datetime import datetime
from flask_login import UserMixin # 4 default methods for user authentication

# the extension has to know how to find/load a user from the user ID stored in the session
# @login_manager.user_loader is the decorator so Flask-Login recognizes the function
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin): # the *table* name is 'user' by default, not 'User'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)
    email_verified = db.Column(db.Boolean, nullable=False, default=False)
    # update any code that creates a user to set program_id??
    program_id = db.Column(db.Integer, db.ForeignKey('program.id'), nullable=False)
    program = db.relationship('Program', backref='students')

    def get_verification_token(self):
        s = Serializer(current_app.config['SECRET_KEY'])
        return s.dumps({'user_id': self.id, 'action': 'verify_email'})
    
    @staticmethod
    def verify_email_token(token, expires_sec=3600):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token, max_age=expires_sec)
            if data.get('action') != 'verify_email':
                return None
        except:
            return None
        return User.query.get(data['user_id'])

    def get_reset_token(self):
        s = Serializer(current_app.config['SECRET_KEY'])
        return s.dumps({'user_id': self.id, 'action': 'reset_password'})
    
    @staticmethod
    def verify_reset_token(token, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token, max_age=expires_sec)
            if data.get('action') != 'reset_password':
                return None
            user_id = data['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User properties: ('{self.username}', '{self.email}', '{self.image_file}', '{self.email_verified}', program ID: '{self.program_id}')"


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)

    # what is this for?
    __table_args__ = (db.UniqueConstraint('user_id', 'course_id', name='_user_course_uc'),)
    
    # are these needed? what are they for?
    course = db.relationship('Course', backref='reviews')

    def __repr__(self):
        author = self.author.username if self.author else "None"
        course = self.course.name if self.course else "None"
        return f"Post('{self.id}', '{self.title}', '{self.date_posted}', author='{author}', course='{course}')"

class Program(db.Model):
    id = db.Column(db.Integer, primary_key=True) # or int??
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(20), unique=True, nullable=False)
    # restrict program_type to either 'bachelor' or 'master'
    program_type = db.Column(db.Enum('bachelor', 'master', name='program_type'), nullable=False)

    def __repr__(self):
        return f"Program('{self.id}', '{self.name}', '{self.code}', '{self.program_type}')"
    

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(20), unique=True, nullable=False)
    
    def __repr__(self):
        return f"Course('{self.id}', '{self.name}', '{self.code}')"
    

class Course_Program(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    program_id = db.Column(db.Integer, db.ForeignKey('program.id'), nullable=False)

    course = db.relationship('Course', backref='course_programs')
    program = db.relationship('Program', backref='course_programs')

    def __repr__(self):
        return f"Course_Program('{self.id}', '{self.course_id}', '{self.program_id}')"