from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, SelectField, IntegerField, RadioField
from wtforms.validators import DataRequired, Length, NumberRange, ValidationError, Optional
from wtforms.widgets import Select as BaseSelectWidget, html_params
from markupsafe import escape, Markup
from flasknetwork.models import Course_Program, Post
from flask_login import current_user


# Rating choices used across all rating fields (1-5 scale)
RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]


class SelectOptGroupWidget(BaseSelectWidget):
    """
    Custom widget for SelectField that supports optgroups.
    Renders select options with optgroup support for categorizing choices.
    """
    
    def render_option(self, value, label, selected_value):
        """Render an individual option with proper selected attribute."""
        if value == selected_value:
            return f'<option value="{escape(value)}" selected>{escape(label)}</option>'
        else:
            return f'<option value="{escape(value)}">{escape(label)}</option>'

    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        html = ['<select %s>' % html_params(name=field.name, **kwargs)]
        
        for item in field.choices:
            if isinstance(item, (list, tuple)) and len(item) == 2:
                group_label, choices = item
                if isinstance(choices, (list, tuple)):
                    if choices:
                        html.append(f'<optgroup label="{escape(group_label)}">')
                        for value, label in choices:
                            html.append(self.render_option(value, label, field.data))
                        html.append('</optgroup>')
                    else:
                        continue
                else:
                    html.append(self.render_option(group_label, choices, field.data))
        
        html.append('</select>')
        return Markup(''.join(html))


class SelectOptGroupField(SelectField):
    """
    Custom SelectField that supports optgroups for organizing options.
    Maintains compatibility with standard SelectField while adding optgroup support.
    """
    widget = SelectOptGroupWidget()

    def process_formdata(self, valuelist):
        if valuelist:
            try:
                self.data = self.coerce(valuelist[0])
            except (TypeError, ValueError):
                self.data = None

    def _iter_flattened_choices(self):
        for item in self.choices:
            if isinstance(item, (list, tuple)) and len(item) == 2:
                first, second = item
                if isinstance(second, (list, tuple)):
                    for value, label in second:
                        yield value, label
                else:
                    yield first, second
            else:
                try:
                    value, label = item
                    yield value, label
                except Exception:
                    continue

    def pre_validate(self, form):
        if self.data is None:
            return
        for value, _ in self._iter_flattened_choices():
            if value == self.data:
                return
        raise ValidationError(self.gettext('Not a valid choice.'))


class PostForm(FlaskForm):
    """Form for creating and editing course reviews with multiple rating categories."""
    
    course = SelectOptGroupField('Course', coerce=int, validators=[DataRequired()])
    title = StringField('Review Title', validators=[DataRequired(), Length(max=100)])
    year_taken = IntegerField('Year Taken', validators=[DataRequired(), NumberRange(min=2000, max=2100)])
    
    # Rating categories (all required, 1-5 scale)
    rating = RadioField('Overall Rating', coerce=int, 
                        choices=RATING_CHOICES, validators=[DataRequired()])
    rating_professor = RadioField('Professor', coerce=int, 
                                  choices=RATING_CHOICES, validators=[DataRequired()])
    rating_material = RadioField('Material & Interestingness', coerce=int, 
                                 choices=RATING_CHOICES, validators=[DataRequired()])
    rating_workload = RadioField('Workload', coerce=int, 
                                 choices=RATING_CHOICES, validators=[DataRequired()])
    rating_peers = RadioField('Peers & Community', coerce=int, 
                              choices=RATING_CHOICES, validators=[DataRequired()])
    
    # Single general comment (optional)
    content = TextAreaField('Your Thoughts', validators=[Optional(), Length(max=2000)])
    
    submit = SubmitField('Post')

    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        self.course.choices = self.build_course_choices()

    def build_course_choices(self):
        # Returns the choices list for the course field
        if not current_user.is_authenticated:
            return []
        try:
            user_program_id = current_user.program_id
            available_courses = [
                cp.course for cp in 
                Course_Program.query.filter_by(program_id=user_program_id).all()
            ]
            if not available_courses:
                return [('', 'No courses available in your program')]
            reviewed_course_ids = {
                post.course_id for post in 
                Post.query.filter_by(user_id=current_user.id).all()
            }
            unreviewed_courses = []
            reviewed_courses = []
            for course in available_courses:
                course_choice = (course.id, f"{course.name} ({course.code})")
                if course.id in reviewed_course_ids:
                    reviewed_courses.append(course_choice)
                else:
                    unreviewed_courses.append(course_choice)
            choices = []
            if unreviewed_courses:
                choices.append(('Courses to Review', unreviewed_courses))
            if reviewed_courses:
                choices.append(('Already Reviewed Courses', reviewed_courses))
            if not unreviewed_courses and not reviewed_courses:
                choices = [('', 'No courses available')]
            elif not unreviewed_courses:
                choices = [('All Courses Reviewed', reviewed_courses)]
            return choices
        except Exception:
            return [('', 'Error loading courses. Please try again.')]
