from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from flask_mail import Message
from flasknetwork.models import Post
from flasknetwork.main.forms import FeedbackForm
from flasknetwork import mail

main = Blueprint('main', __name__)


@main.route('/')
@main.route('/home')
def home():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('home.html', title='Home Page', posts=posts)


@main.route('/feedback', methods=['GET', 'POST'])
def feedback():
    form = FeedbackForm()
    redirect_url = request.args.get('next') or url_for('main.home')
    
    if form.validate_on_submit():
        try:
            msg = Message(
                'rateKTH Feedback',
                sender='ratekth@noreply.com',
                recipients=[current_app.config['MAIL_USERNAME']]
            )
            msg.body = f"Feedback from rateKTH:\n\n{form.message.data}"
            mail.send(msg)
            flash('Thanks for your feedback!', 'success')
            return redirect(redirect_url)
        except Exception as e:
            current_app.logger.error(f"Failed to send feedback email: {e}")
            flash('Failed to send feedback. Please try again later.', 'danger')
    
    return render_template('feedback.html', title='Feedback', form=form, redirect_url=redirect_url)