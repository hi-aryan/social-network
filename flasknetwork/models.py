from flasknetwork import db, login_manager
from itsdangerous import URLSafeTimedSerializer as Serializer
from flask import current_app
from datetime import datetime
from flask_login import UserMixin # 4 default methods for user authentication
import random

# the extension has to know how to find/load a user from the user ID stored in the session
# @login_manager.user_loader is the decorator so Flask-Login recognizes the function
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin): # the *table* name is 'user' by default, not 'User'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default1.png')
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

    def can_review(self, course):
        """
        Return True if this user
        1) has verified their email,
        2) hasn't already reviewed this course, and
        3) the course is in their program.
        """
        if not self.email_verified:
            return False

        if course.is_reviewed_by(self):
            return False

        return course.course_is_available_for_program(self.program_id)

    def __repr__(self):
        return f"User properties: (ID: '{self.id}', '{self.username}', '{self.email}', '{self.image_file}', '{self.email_verified}', program ID: '{self.program_id}')"


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    year_taken = db.Column(db.Integer, nullable=False)  # e.g., 2023
    rating = db.Column(db.Integer, nullable=False)  # e.g., 1-5
    
    # All 6 questions are now optional, but at least one must be filled
    answer_q1 = db.Column(db.Text, nullable=True)
    answer_q2 = db.Column(db.Text, nullable=True)
    answer_q3 = db.Column(db.Text, nullable=True)
    answer_q4 = db.Column(db.Text, nullable=True)
    answer_q5 = db.Column(db.Text, nullable=True)
    answer_q6 = db.Column(db.Text, nullable=True)
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)

    # what is this for?
    __table_args__ = (db.UniqueConstraint('user_id', 'course_id', name='one_review_per_course'),)
    
    # TODO: are these needed? what are they for?
    course = db.relationship('Course', backref='reviews')
    #author = db.relationship('User', backref='reviews')

    def get_answered_questions(self):
        """
        Returns a list of (question, answer) tuples for only the questions that have been answered.
        Encapsulates the logic for determining which questions to display.
        """
        questions_map = [
            ("Did you have fun?", self.answer_q1),
            ("How was the professor?", self.answer_q2),
            ("How was the workload?", self.answer_q3),
            ("Did you learn anything or just memorize a bunch of stuff?", self.answer_q4),
            ("What was the best part of the course?", self.answer_q5),
            ("A word to enrolling students?", self.answer_q6),
        ]
        
        # Return only questions that have non-empty answers
        return [(question, answer) for question, answer in questions_map 
                if answer and answer.strip()]

    def __repr__(self):
        author = self.author.username if self.author else "None"
        course = self.course.name if self.course else "None"
        answered_questions = len(self.get_answered_questions())
        return f"\n\nPost('{self.id}', '{self.title}', '{self.date_posted}', author='{author}', course='{course}', year_taken='{self.year_taken}', rating='{self.rating}', answered_questions='{answered_questions}/6')\n\n"

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
    name = db.Column(db.String(150), nullable=False, index=True)
    code = db.Column(db.String(20), unique=True, nullable=False, index=True)
    
    @classmethod
    def search(cls, query, limit=50):
        """
        Search courses by name or code with case-insensitive matching.
        
        Args:
            query (str): Search term to match against course name or code
            limit (int): Maximum number of results to return
            
        Returns:
            List[Course]: List of matching courses
            
        Raises:
            ValueError: If query is invalid
        """
        if not query or not isinstance(query, str):
            raise ValueError("Search query must be a non-empty string")
            
        # Sanitize input - remove extra whitespace and limit length
        sanitized_query = query.strip()[:100]  # Limit to 100 chars
        
        if len(sanitized_query) < 2:
            raise ValueError("Search query must be at least 2 characters long")
        
        # Use ilike for case-insensitive search with wildcards
        search_filter = db.or_(
            cls.name.ilike(f'%{sanitized_query}%'),
            cls.code.ilike(f'%{sanitized_query}%')
        )
        
        return cls.query.filter(search_filter).limit(max(1, min(limit, 100))).all()
    
    def to_dict(self):
        """
        Convert Course instance to dictionary for JSON serialization.
        
        Returns:
            dict: Course data as dictionary
        """
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'review_count': self.get_review_count()
        }

    def get_review_count(self):
        """
        Get the total number of reviews for this course efficiently.
        
        Returns:
            int: Number of reviews for this course
        """
        return Post.query.filter_by(course_id=self.id).count()

    def get_average_rating(self):
        """
        Calculate the average rating for this course efficiently.
        
        Returns:
            float: Average rating, or None if no reviews exist
        """
        result = db.session.query(db.func.avg(Post.rating)).filter_by(course_id=self.id).scalar()
        return result if result is not None else None

    def is_reviewed_by(self, user):
        """Return True if `user` has already reviewed this course."""
        if not user or user.is_anonymous:
            return False
        return any(r.user_id == user.id for r in self.reviews)

    def course_is_available_for_program(self, program_id):
        """
        Return True if this course is available for the given program_id.
        """
        return any(cp.program_id == program_id for cp in self.course_programs)

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

class RandomUsername(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    is_used = db.Column(db.Boolean, nullable=False, default=False)
    
    @classmethod
    def get_random_unused(cls):
        """
        Get a random unused username from the pool.
        
        Returns:
            str: A random unused username, or None if pool is exhausted
        """
        unused_usernames = cls.query.filter_by(is_used=False).all()
        if not unused_usernames:
            return None
        
        random_username = random.choice(unused_usernames)
        return random_username.username
    
    @classmethod
    def mark_as_used(cls, username):
        """
        Mark a username as used.
        
        Args:
            username (str): The username to mark as used
            
        Returns:
            bool: True if successfully marked, False if username not found
        """
        username_obj = cls.query.filter_by(username=username, is_used=False).first()
        if username_obj:
            username_obj.is_used = True
            db.session.commit()
            return True
        return False
    
    @classmethod
    def get_unused_count(cls):
        """
        Get the count of unused usernames in the pool.
        
        Returns:
            int: Number of unused usernames available
        """
        return cls.query.filter_by(is_used=False).count()
    
    @classmethod
    def is_username_available(cls, username):
        """
        Check if a username is available (either not in pool or in pool but unused).
        
        Args:
            username (str): Username to check
            
        Returns:
            bool: True if available, False if taken
        """
        # Check if username exists in User table
        if User.query.filter_by(username=username).first():
            return False
        
        # Check if username exists in RandomUsername table and is used
        random_username = cls.query.filter_by(username=username).first()
        if random_username and random_username.is_used:
            return False
            
        return True
    
    def __repr__(self):
        return f"RandomUsername('{self.id}', '{self.username}', used={self.is_used})"