from flask import (render_template, url_for, flash, redirect, request, abort, Blueprint)
from flask_login import current_user, login_required
from flasknetwork import db
from flasknetwork.models import Post
from flasknetwork.posts.forms import PostForm

posts = Blueprint('posts', __name__)


@posts.route('/post/new', methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    existing_review_id = None
    
    if form.validate_on_submit():
        existing_review = Post.query.filter_by(user_id=current_user.id, course_id=form.course.data).first()
        if existing_review:
            # Add error to form instead of redirecting (preserves user input)
            form.course.errors.append("You've already reviewed this course! You can edit your existing review instead.")
            existing_review_id = existing_review.id
        else:
            # Create new post (follows PRG pattern)
            post = Post(
                title=form.title.data, 
                author=current_user, 
                course_id=form.course.data,
                year_taken=form.year_taken.data,
                rating=form.rating.data,
                answer_q1=form.answer_q1.data if form.answer_q1.data and form.answer_q1.data.strip() else None,
                answer_q2=form.answer_q2.data if form.answer_q2.data and form.answer_q2.data.strip() else None,
                answer_q3=form.answer_q3.data if form.answer_q3.data and form.answer_q3.data.strip() else None,
                answer_q4=form.answer_q4.data if form.answer_q4.data and form.answer_q4.data.strip() else None,
                answer_q5=form.answer_q5.data if form.answer_q5.data and form.answer_q5.data.strip() else None,
                answer_q6=form.answer_q6.data if form.answer_q6.data and form.answer_q6.data.strip() else None
            )
            db.session.add(post)
            db.session.commit()
            flash('Thank you for sharing your course review! Your feedback helps fellow students <33', 'success')
            return redirect(url_for('main.home'))
    elif request.method == 'GET':
        # Handle course_id URL parameter for pre-selection
        course_id = request.args.get('course_id', type=int)
        if course_id:
            form.course.data = course_id

    
    return render_template('create_post.html', title='Course Review', form=form, 
                         legend='Course Review', existing_review_id=existing_review_id)


@posts.route('/ty')
def thankyou():
    flash('Thank you for sharing your course review! Your feedback helps fellow students <33', 'success')
    return redirect(url_for('main.home'))


@posts.route('/post/<int:post_id>')
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post)


@posts.route('/post/<int:post_id>/update', methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        dup = Post.query.filter_by(user_id=current_user.id, course_id=form.course.data).first()
        if dup and dup.id != post.id:
            form.course.errors.append("You've already reviewed this course.")
        else:
            post.course_id  = form.course.data
            post.title      = form.title.data
            post.year_taken = form.year_taken.data
            post.rating     = form.rating.data
            post.answer_q1  = form.answer_q1.data if form.answer_q1.data and form.answer_q1.data.strip() else None
            post.answer_q2  = form.answer_q2.data if form.answer_q2.data and form.answer_q2.data.strip() else None
            post.answer_q3  = form.answer_q3.data if form.answer_q3.data and form.answer_q3.data.strip() else None
            post.answer_q4  = form.answer_q4.data if form.answer_q4.data and form.answer_q4.data.strip() else None
            post.answer_q5  = form.answer_q5.data if form.answer_q5.data and form.answer_q5.data.strip() else None
            post.answer_q6  = form.answer_q6.data if form.answer_q6.data and form.answer_q6.data.strip() else None
            db.session.commit()
            flash('Your post has been updated!', 'success')
            return redirect(url_for('posts.post', post_id=post.id))
    elif request.method == 'GET':
        form.course.data = post.course_id
        form.title.data = post.title
        form.year_taken.data = post.year_taken
        form.rating.data = post.rating
        form.answer_q1.data = post.answer_q1
        form.answer_q2.data = post.answer_q2
        form.answer_q3.data = post.answer_q3
        form.answer_q4.data = post.answer_q4
        form.answer_q5.data = post.answer_q5
        form.answer_q6.data = post.answer_q6

    return render_template('create_post.html', title='Update Post', form=form, legend='Update Post')


@posts.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('main.home'))