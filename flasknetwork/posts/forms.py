from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, SelectField, IntegerField, RadioField
from wtforms.validators import DataRequired, Length, NumberRange
from flasknetwork.models import Course_Program
from flask_login import current_user


class PostForm(FlaskForm):
    course = SelectField('Course', coerce=int, validators=[DataRequired()])
    title = StringField('Title', validators=[DataRequired(), Length(max=100)])
    year_taken = IntegerField('Year Taken', validators=[DataRequired(), NumberRange(min=2000, max=2100)])
    rating = RadioField('Course Rating', coerce=int, choices=[(i, str(i)) for i in range(1,6)], validators=[DataRequired()])
    answer_q1 = TextAreaField('What did you like most?', validators=[DataRequired(), Length(max=200)])
    answer_q2 = TextAreaField('What could be improved?', validators=[DataRequired(), Length(max=200)])


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