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
    if form.validate_on_submit():
        existing_review = Post.query.filter_by(user_id=current_user.id, course_id=form.course.data).first()
        if existing_review:
            flash("You've already reviewed this course! Please edit your existing review instead.", 'warning')
            return redirect(url_for('posts.update_post', post_id=existing_review.id))

        post = Post(
            title=form.title.data, 
            content=form.content.data, 
            author=current_user, 
            course_id=form.course.data,
            year_taken=form.year_taken.data,
            rating=form.rating.data,
            answer_q1=form.answer_q1.data,
            answer_q2=form.answer_q2.data
        )
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('main.home'))
    return render_template('create_post.html', title='New Course Review', form=form, legend='New Course Review')


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
            post.content    = form.content.data
            post.year_taken = form.year_taken.data
            post.rating     = form.rating.data
            post.answer_q1  = form.answer_q1.data
            post.answer_q2  = form.answer_q2.data
            db.session.commit()
            flash('Your post has been updated!', 'success')
            return redirect(url_for('posts.post', post_id=post.id))
    elif request.method == 'GET':
        form.course.data = post.course_id
        form.title.data = post.title
        form.content.data = post.content
        form.year_taken.data = post.year_taken
        form.rating.data = post.rating
        form.answer_q1.data = post.answer_q1
        form.answer_q2.data = post.answer_q2

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