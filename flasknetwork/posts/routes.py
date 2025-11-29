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
            form.course.errors.append("You've already reviewed this course! You can edit your existing review instead.")
            existing_review_id = existing_review.id
        else:
            post = Post(
                title=form.title.data,
                author=current_user,
                course_id=form.course.data,
                year_taken=form.year_taken.data,
                # rating is now computed from the other ratings
                rating_professor=form.rating_professor.data,
                rating_material=form.rating_material.data,
                rating_workload=form.rating_workload.data,
                rating_peers=form.rating_peers.data,
                content=form.content.data.strip() if form.content.data else None
            )
            db.session.add(post)
            db.session.commit()
            flash('Thank you for sharing your review! Your feedback helps fellow students <33', 'success')
            return redirect(url_for('main.home'))
    elif request.method == 'GET':
        course_id = request.args.get('course_id', type=int)
        if course_id:
            form.course.data = course_id
    
    return render_template('create_post.html', title='Course Review', form=form, 
                           legend='Course Review', existing_review_id=existing_review_id)


@posts.route('/test-alerts')
def test_alerts():
    flash('This is a success message', 'success')
    flash('This is a danger message', 'danger')
    flash('This is a warning message', 'warning')
    flash('This is an info message', 'info')
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
            post.course_id = form.course.data
            post.title = form.title.data
            post.year_taken = form.year_taken.data
            # rating is computed from other ratings
            post.rating_professor = form.rating_professor.data
            post.rating_material = form.rating_material.data
            post.rating_workload = form.rating_workload.data
            post.rating_peers = form.rating_peers.data
            post.content = form.content.data.strip() if form.content.data else None
            db.session.commit()
            flash('Your post has been updated!', 'success')
            return redirect(url_for('posts.post', post_id=post.id))
    elif request.method == 'GET':
        form.course.data = post.course_id
        form.title.data = post.title
        form.year_taken.data = post.year_taken
        # rating is computed, no need to set form.rating.data
        form.rating_professor.data = post.rating_professor
        form.rating_material.data = post.rating_material
        form.rating_workload.data = post.rating_workload
        form.rating_peers.data = post.rating_peers
        form.content.data = post.content

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