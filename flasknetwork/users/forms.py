from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_login import current_user
from flasknetwork.models import User, Program, RandomUsername
from flasknetwork.users.utils import is_kth_domain, get_available_profile_pictures, validate_profile_picture


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()], 
                        render_kw={'placeholder': 'email@kth.se (your email won\'t be displayed publicly, only your username)'})
    password = PasswordField('', validators=[DataRequired(), Length(min=6, max=30)],
                        render_kw={'placeholder': 'Password'})
    confirm_password = PasswordField('', validators=[DataRequired(), EqualTo('password')],
                                render_kw={'placeholder': 'Confirm Password'})
    program = SelectField('Program', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Sign Up')

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        # Populate program choices from database
        self.program.choices = [(p.id, f"{p.name} ({p.program_type.title()})") 
                               for p in Program.query.order_by(Program.name).all()]

    def validate_username(self, username):
        # Use our centralized availability check
        if not RandomUsername.is_username_available(username.data):
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')
        
        if not is_kth_domain(email.data):
            raise ValidationError('Only KTH students (@kth.se) can register.')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()], 
                        render_kw={'placeholder': 'email@kth.se'})
    password = PasswordField('', validators=[DataRequired()],
                        render_kw={'placeholder': 'Password'})
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class UpdateAccountForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()], 
                        render_kw={'placeholder': 'email@kth.se'})
    picture = SelectField('Profile Picture', coerce=str, validators=[DataRequired()])
    submit = SubmitField('Update')
    
    def __init__(self, *args, **kwargs):
        super(UpdateAccountForm, self).__init__(*args, **kwargs)
        # Populate picture choices from available images
        self.picture.choices = get_available_profile_pictures()

    def validate_picture(self, picture):
        """Validate that the selected picture exists"""
        if picture.data and not validate_profile_picture(picture.data):
            raise ValidationError('Selected profile picture is not available.')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:  
                raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')
        if not is_kth_domain(email.data):
            raise ValidationError('Only KTH students (@kth.se) can register.')


class RequestResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()], 
                        render_kw={'placeholder': 'email@kth.se'})
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('There is no account with that email. Please register first.')
        if not is_kth_domain(email.data):
            raise ValidationError('Only KTH students (@kth.se) can register.')
        

class ResetPasswordForm(FlaskForm):
    password = PasswordField('', validators=[DataRequired(), Length(min=6, max=30)],
                        render_kw={'placeholder': 'Password'})
    confirm_password = PasswordField('', validators=[DataRequired(), EqualTo('password')],
                                render_kw={'placeholder': 'Confirm Password'})
    submit = SubmitField('Reset Password')


class RequestVerificationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()], 
                        render_kw={'placeholder': 'email@kth.se'})
    submit = SubmitField('Send Verification Email')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('No account found with that email.')
        if user.email_verified:
            raise ValidationError('This account is already verified.')
        if not is_kth_domain(email.data):
            raise ValidationError('Only KTH students (@kth.se) can register.')