from urllib.parse import urlparse
from flask import (render_template, url_for, flash, redirect, request, abort, Blueprint)
from flask_login import current_user, login_required
from flasknetwork import db
from flasknetwork.models import Post, WorkloadLevel, Tag
from flasknetwork.posts.forms import PostForm

posts = Blueprint('posts', __name__)

class BackLinkResolver:
    """Resolve a safe internal back-link with a graceful fallback."""

    @staticmethod
    def get_back_url(request_obj, default_url):
        host = request_obj.host

        return_to = request_obj.args.get('return_to')
        if BackLinkResolver._is_safe_path(return_to, host):
            return return_to

        return default_url

    @staticmethod
    def _is_safe_path(target, host):
        if not target:
            return False

        parsed = urlparse(target)

        if parsed.scheme:
            return parsed.netloc == host

        return target.startswith('/') and not parsed.netloc


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

                author=current_user,
                course_id=form.course.data,
                year_taken=form.year_taken.data,
                # rating is computed from professor, material, and peers ratings
                rating_professor=form.rating_professor.data,
                rating_material=form.rating_material.data,
                rating_workload=WorkloadLevel(form.rating_workload.data),
                rating_peers=form.rating_peers.data,
                content=form.content.data.strip() if form.content.data else None
            )
            db.session.add(post)
            db.session.flush()  # Flush to get post.id before assigning tags
            
            # Assign tags if provided
            if form.tags.data:
                post.tags = Tag.query.filter(Tag.id.in_(form.tags.data)).all()
            
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
    back_url = BackLinkResolver.get_back_url(request, url_for('main.home'))
    return render_template('post.html', title=f"{post.course.code} Review", post=post, back_url=back_url)


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

            post.year_taken = form.year_taken.data
            # rating is computed from professor, material, and peers ratings
            post.rating_professor = form.rating_professor.data
            post.rating_material = form.rating_material.data
            post.rating_workload = WorkloadLevel(form.rating_workload.data)
            post.rating_peers = form.rating_peers.data
            post.content = form.content.data.strip() if form.content.data else None
            
            # Update tags
            if form.tags.data:
                post.tags = Tag.query.filter(Tag.id.in_(form.tags.data)).all()
            else:
                post.tags = []
            
            db.session.commit()
            flash('Your post has been updated!', 'success')
            return redirect(url_for('posts.post', post_id=post.id))
    elif request.method == 'GET':
        form.course.data = post.course_id

        form.year_taken.data = post.year_taken
        # rating is computed, no need to set form.rating.data
        form.rating_professor.data = post.rating_professor
        form.rating_material.data = post.rating_material
        form.rating_workload.data = post.rating_workload.value if post.rating_workload else None
        form.rating_peers.data = post.rating_peers
        form.content.data = post.content
        form.tags.data = [tag.id for tag in post.tags]

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