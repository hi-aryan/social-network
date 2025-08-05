from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length
from flasknetwork.models import Course_Program
from flask_login import current_user


class PostForm(FlaskForm):
    course = SelectField('Course', coerce=int, validators=[DataRequired()])
    title = StringField('Title', validators=[DataRequired(), Length(max=100)])
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Post')

    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        # Populate course choices from database
        if current_user.is_authenticated:
            user_program = current_user.program_id
            available_courses = [cp.course for cp in Course_Program.query.filter_by(program_id=user_program).all()]
            self.course.choices = [(c.id, f"{c.name} ({c.code})") for c in available_courses]
        else:
            self.course.choices = []