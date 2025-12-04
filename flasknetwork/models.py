from flasknetwork import db, login_manager
from itsdangerous import URLSafeTimedSerializer as Serializer
from flask import current_app
from datetime import datetime
from flask_login import UserMixin # 4 default methods for user authentication
from sqlalchemy import func
import random
import enum


class WorkloadLevel(enum.Enum):
    """Enum for workload levels in course reviews."""
    light = 'light'
    medium = 'medium'
    heavy = 'heavy'
    
    @classmethod
    def choices(cls):
        """Returns list of (value, label) tuples for form fields."""
        return [(level.value, level.value.capitalize()) for level in cls]

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
    title = db.Column(db.String(50), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    year_taken = db.Column(db.Integer, nullable=False)
    
    # Rating categories (professor, material, peers: 1-5 scale; workload: enum)
    # Note: overall rating is computed via @property from professor, material, peers only
    rating_professor = db.Column(db.Integer, nullable=False)    # Professor quality
    rating_material = db.Column(db.Integer, nullable=False)     # Material & interestingness
    rating_workload = db.Column(db.Enum(WorkloadLevel), nullable=False)  # Workload level
    rating_peers = db.Column(db.Integer, nullable=False)        # Students/peers experience
    
    # Single general comment field
    content = db.Column(db.Text, nullable=True)
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False, index=True)

    __table_args__ = (db.UniqueConstraint('user_id', 'course_id', name='one_review_per_course'),)
    
    course = db.relationship('Course', backref='reviews')

    @property
    def rating(self):
        """
        Computed overall rating as the average of professor, material, and peers ratings.
        Excludes workload since it's a categorical enum, not a numeric scale.
        Returns rounded integer (1-5 scale).
        """
        if all([self.rating_professor, self.rating_material, self.rating_peers]):
            avg = (self.rating_professor + self.rating_material + self.rating_peers) / 3
            return round(avg)
        return None
    
    @rating.setter
    def rating(self, value):
        """
        Setter for backward compatibility - ignore attempts to set the rating directly.
        The rating is now computed from the other ratings.
        """
        pass  # Rating is computed, not stored

    @property
    def workload_display(self):
        """Returns the workload level as a display-friendly string (e.g., 'Light', 'Medium', 'Heavy')."""
        if self.rating_workload:
            return self.rating_workload.value.capitalize()
        return None

    def get_star_ratings(self):
        """Returns list of (label, value) tuples for numeric star ratings only."""
        return [
            ("Overall", self.rating),
            ("Professor", self.rating_professor),
            ("Material", self.rating_material),
            ("Peers", self.rating_peers),
        ]

    def get_content_preview(self, max_words=30):
        """
        Returns a word-based preview of the post content.
        Truncates intelligently at word boundaries, not mid-word.
        Adds "..." to indicate content was truncated.
        CSS handles the final 2-line visual truncation.
        
        Args:
            max_words (int): Maximum number of words to include (default: 30, ensures ~2 lines)
            
        Returns:
            str: Preview text truncated at word boundary with "..." if truncated, or empty string if no content
        """
        if not self.content:
            return ""
        
        words = self.content.split()
        if len(words) <= max_words:
            return self.content
        
        return " ".join(words[:max_words]) + "..."

    def __repr__(self):
        author = self.author.username if self.author else "None"
        course = self.course.name if self.course else "None"
        return f"Post(id={self.id}, title='{self.title}', author='{author}', course='{course}', rating={self.rating})"

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
        Returns courses with review_count attached as attribute.
        
        Args:
            query (str): Search term to match against course name or code
            limit (int): Maximum number of results to return
            
        Returns:
            List[Course]: List of Course objects with review_count attribute
            
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
        
        # Batch review counts using LEFT JOIN and GROUP BY
        results = db.session.query(
            cls,
            func.count(Post.id).label('review_count')
        ).outerjoin(Post, cls.id == Post.course_id)\
         .filter(search_filter)\
         .group_by(cls.id)\
         .order_by(cls.name)\
         .limit(max(1, min(limit, 100))).all()
        
        # Attach review_count to each course object
        courses = []
        for course, count in results:
            course.review_count = count or 0
            courses.append(course)
        
        return courses
    
    @classmethod
    def get_all(cls, limit=20, offset=0):
        """
        Get all courses with pagination, ordered by name.
        Returns courses with review_count attached as attribute.
        
        Args:
            limit (int): Maximum number of results to return (default 20, max 100)
            offset (int): Number of results to skip (for pagination)
            
        Returns:
            tuple: (list of Course objects with review_count attribute, has_more boolean)
        """
        limit = max(1, min(limit, 100))
        offset = max(0, offset)
        
        # Batch review counts using LEFT JOIN and GROUP BY
        # Fetch one extra to check if there are more results
        results = db.session.query(
            cls,
            func.count(Post.id).label('review_count')
        ).outerjoin(Post, cls.id == Post.course_id)\
         .group_by(cls.id)\
         .order_by(cls.name)\
         .offset(offset)\
         .limit(limit + 1).all()
        
        has_more = len(results) > limit
        if has_more:
            results = results[:limit]  # Remove the extra item
        
        # Attach review_count to each course object
        courses = []
        for course, count in results:
            course.review_count = count or 0
            courses.append(course)
            
        return courses, has_more
    
    def to_dict(self):
        """
        Convert Course instance to dictionary for JSON serialization.
        Uses pre-attached review_count if available, otherwise queries database.
        
        Returns:
            dict: Course data as dictionary
        """
        # Use pre-attached review_count if available (from batched queries)
        # Otherwise fall back to querying database
        review_count = getattr(self, 'review_count', None)
        if review_count is None:
            review_count = self.get_review_count()
        
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'review_count': review_count
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
        Calculate the average overall rating for this course.
        Computes from 3 rating categories (professor, material, peers).
        Excludes workload since it's a categorical enum, not a numeric scale.
        
        Returns:
            float: Average rating, or None if no reviews exist
        """
        result = db.session.query(
            db.func.avg(
                (Post.rating_professor + Post.rating_material + Post.rating_peers) / 3.0
            )
        ).filter_by(course_id=self.id).scalar()
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