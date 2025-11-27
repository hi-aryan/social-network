from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length


class FeedbackForm(FlaskForm):
    message = TextAreaField('Feedback', validators=[DataRequired(), Length(min=10, max=2000)],
                           render_kw={'placeholder': 'Your feedback...', 'rows': 6})
    submit = SubmitField('Send')

