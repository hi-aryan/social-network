# KTH Course Review App: A Detailed Development Plan

This document outlines a comprehensive, step-by-step plan for building the KTH Course Review web application. The plan is designed to be efficient, reusing existing code and concepts from the initial Flask project, while prioritizing clean, Object-Oriented, and secure code.

## Guiding Principles

*   **Incremental Development:** We will build the application in small, manageable steps, ensuring each feature is fully functional and tested before moving to the next.
*   **Leverage Existing Code:** To maximize efficiency, we will adapt and extend the existing Flask application's structure, including blueprints, forms, models, and templates.
*   **Security First:** Security will be a primary consideration at every stage, with a focus on preventing common web application vulnerabilities.
*   **OOP Best Practices:** We will adhere to Object-Oriented Programming principles to create a robust, maintainable, and scalable codebase.

## The Plan: Five-Phase Approach

I have broken down the development process into five distinct phases. This phased approach allows for a logical progression of work, with each phase building upon the previous one.

### Phase 1: Core Data Modeling and Integration

This initial phase focuses on establishing the data foundation for the application. We will create the necessary database models for KTH-specific data and integrate them into the existing SQLAlchemy setup.

**Step 1.1: Database Schema for KTH Data**

*   **Objective:** Design and implement the database models for Programs, Courses, and Professors.
*   **Details:**
    *   We will create three new models in `flasknetwork/models.py`: `Program`, `Course`, and `Professor`.
    *   `Program`: Will have a `name` (e.g., "Teknisk Fysik") and a relationship to `Course`.
    *   `Course`: Will have a `name` (e.g., "DD1337 - Programmering"), a `course_code` (e.g., "DD1337"), and relationships to `Program` and `Professor`. We will also include a relationship to the `Post` model to represent reviews.
    *   `Professor`: Will have a `name` and a relationship to `Course`.
    *   We will establish many-to-many relationships between these models to accurately represent the connections between programs, courses, and professors. For example, a course can be part of multiple programs, and a professor can teach multiple courses.
*   **Code Skeleton (`flasknetwork/models.py`):**

    ```python
    # ... existing imports ...

    class Program(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(100), unique=True, nullable=False)
        courses = db.relationship('Course', secondary='program_course', backref='programs', lazy=True)

    class Course(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(100), nullable=False)
        course_code = db.Column(db.String(10), unique=True, nullable=False)
        reviews = db.relationship('Post', backref='course_reviewed', lazy=True)
        professors = db.relationship('Professor', secondary='course_professor', backref='courses', lazy=True)

    class Professor(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(100), nullable=False)

    # Association tables for many-to-many relationships
    program_course = db.Table('program_course',
        db.Column('program_id', db.Integer, db.ForeignKey('program.id'), primary_key=True),
        db.Column('course_id', db.Integer, db.ForeignKey('course.id'), primary_key=True)
    )

    course_professor = db.Table('course_professor',
        db.Column('course_id', db.Integer, db.ForeignKey('course.id'), primary_key=True),
        db.Column('professor_id', db.Integer, db.ForeignKey('professor.id'), primary_key=True)
    )
    ```

**Step 1.2: Populating the KTH Data**

*   **Objective:** Populate the `Program`, `Course`, and `Professor` tables with data.
*   **Details:**
    *   For the MVP, we will manually populate the database. This is the simplest and most controlled approach.
    *   We will create a Python script to be run once to populate the database. This script will use the SQLAlchemy models to create and add the data.
    *   In the future, we can explore web scraping or using a KTH API if one becomes available. For now, manual population is the most pragmatic choice.

### Phase 2: User Registration and Authentication with KTH Email Verification

This phase focuses on modifying the user registration process to enforce the use of KTH email addresses and implementing an email verification system.

**Step 2.1: KTH Email Validation in Registration Form**

*   **Objective:** Modify the `RegistrationForm` to only accept `@kth.se` or `@ug.kth.se` email addresses.
*   **Details:**
    *   We will add a custom validator to the `email` field in `flasknetwork/users/forms.py`.
    *   This validator will use a regular expression to check if the email address ends with `@kth.se` or `@ug.kth.se`.
*   **Code Skeleton (`flasknetwork/users/forms.py`):**

    ```python
    # ... existing imports ...
    import re

    class RegistrationForm(FlaskForm):
        # ... existing fields ...

        def validate_email(self, email):
            if not re.match(r"[^@]+@(kth\.se|ug\.kth\.se)$", email.data):
                raise ValidationError('Only KTH email addresses (@kth.se or @ug.kth.se) are allowed.')
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')
    ```

**Step 2.2: Email Verification Flow**

*   **Objective:** Implement an email verification system to ensure the user owns the KTH email address.
*   **Details:**
    *   We will add a `is_verified` boolean field to the `User` model in `flasknetwork/models.py`, defaulting to `False`.
    *   Upon successful registration, we will send a verification email to the user's KTH email address. This email will contain a unique verification link.
    *   We will create a new route, `/verify_email/<token>`, to handle the verification link. This route will be similar to the existing `reset_token` route.
    *   When the user clicks the link, the `is_verified` field for their account will be set to `True`.
*   **Security Note:** The verification token should be a securely generated, time-sensitive token, just like the password reset token. The existing `itsdangerous` library is perfect for this.

### Phase 3: Course Review (Post) Functionality

This phase focuses on adapting the existing "Post" functionality to become the "Course Review" functionality.

**Step 3.1: Modifying the Post Model and Form**

*   **Objective:** Update the `Post` model and `PostForm` to represent a course review.
*   **Details:**
    *   In `flasknetwork/models.py`, we will rename the `Post` model to `Review` and add fields for `rating` (e.g., an integer from 1 to 5), and a foreign key to the `Course` model.
    *   In `flasknetwork/posts/forms.py`, we will rename `PostForm` to `ReviewForm` and add fields for `rating` and a `SelectField` for the `Course`.
*   **Code Skeleton (`flasknetwork/models.py`):**

    ```python
    # ... existing imports ...

    class Review(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        title = db.Column(db.String(100), nullable=False)
        date_posted = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
        content = db.Column(db.Text, nullable=False)
        rating = db.Column(db.Integer, nullable=False)
        user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
        course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)

        def __repr__(self):
            return f"Review('{self.title}', '{self.date_posted}')"
    ```

**Step 3.2: Creating and Viewing Reviews**

*   **Objective:** Implement the logic for creating and viewing course reviews.
*   **Details:**
    *   We will modify the `new_post` route in `flasknetwork/posts/routes.py` to become `new_review`. This route will populate the `Course` `SelectField` in the `ReviewForm`.
    *   We will modify the `post` route to display a single review.
    *   We will update the home page (`main/routes.py`) to display a list of recent reviews, showing the course name, rating, and the review content.

### Phase 4: User Profile and My Reviews

This phase focuses on enhancing the user profile to display the user's program and a list of their reviews.

**Step 4.1: Adding Program to User Profile**

*   **Objective:** Allow users to select their KTH program during registration and display it on their profile.
*   **Details:**
    *   We will add a foreign key to the `Program` model in the `User` model in `flasknetwork/models.py`.
    *   We will add a `SelectField` for `Program` to the `RegistrationForm` in `flasknetwork/users/forms.py`. This field will be populated with all the programs from the database.
    *   We will update the `account.html` template to display the user's program.

**Step 4.2: "My Reviews" Page**

*   **Objective:** Create a page where users can see all of their own reviews.
*   **Details:**
    *   We will reuse the existing `user_posts` route and template (`users/routes.py` and `user_posts.html`) and adapt them to display a user's reviews instead of posts.

### Phase 5: Advanced Features and Refinements

This final phase focuses on adding more advanced features and refining the application.

**Step 5.1: "Like" or "Helpful" Button for Reviews**

*   **Objective:** Allow signed-in users to mark a review as helpful.
*   **Details:**
    *   We will create a new `Like` model in `flasknetwork/models.py` with foreign keys to `User` and `Review`.
    *   We will add a "Helpful" button to the review display page.
    *   We will use JavaScript and a new route to handle the "like" action without a full page reload, providing a smoother user experience.

**Step 5.2: Pre-populating Professor Field**

*   **Objective:** Pre-populate the professor field based on the selected course when creating a review.
*   **Details:**
    *   This is a more advanced feature that we can implement after the MVP.
    *   We will use JavaScript to dynamically update the `Professor` `SelectField` based on the selected `Course`. This will require an API endpoint that returns the professors for a given course.

## Security Considerations Throughout the Project

*   **Input Validation:** We will continue to use WTForms for all forms, which provides excellent protection against Cross-Site Scripting (XSS) and other input-based attacks.
*   **SQL Injection:** By using SQLAlchemy's ORM, we are protected against most SQL injection vulnerabilities. We will continue to use the ORM for all database interactions.
*   **Cross-Site Request Forgery (CSRF):** Flask-WTF provides CSRF protection, and we will ensure it is enabled on all forms.
*   **Password Hashing:** We will continue to use `bcrypt` for hashing passwords, which is a secure and industry-standard practice.

This plan provides a clear roadmap for developing the KTH Course Review application. By following these steps, we can build a robust, secure, and user-friendly platform for KTH students.
