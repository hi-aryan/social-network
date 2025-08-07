from flask import Blueprint, render_template, request
from flasknetwork.models import Post

main = Blueprint('main', __name__)


@main.route('/')
@main.route('/home')
def home():
    page=request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('home.html', title='Home Page', posts=posts)


# About page removed - replaced with course search functionality in courses blueprint