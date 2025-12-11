from flask import render_template, url_for, flash, redirect, request, Blueprint
from flask_login import login_user, current_user, logout_user, login_required
from flasknetwork import db, bcrypt
from flasknetwork.models import User, Post, Program
from flasknetwork.users.forms import RegistrationForm, LoginForm, UpdateAccountForm, RequestResetForm, ResetPasswordForm, RequestVerificationForm
from flasknetwork.users.utils import send_reset_email, send_verification_email, validate_profile_picture, send_email_change_email

users = Blueprint('users', __name__)


@users.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    form = RegistrationForm()
    
    if form.validate_on_submit():
        try:
            # Fetch Program object to get program code
            program = Program.query.get(form.program.data)
            if not program:
                flash('Invalid program selected. Please try again.', 'danger')
                return render_template('register.html', title='Register', form=form)
            
            # Create user with temporary username (required for NOT NULL constraint)
            # Will be replaced with generated username after flush
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            user = User(username='TEMP', email=form.email.data, password=hashed_password, program_id=form.program.data)
            db.session.add(user)
            
            # Flush to get user.id without committing
            db.session.flush()
            
            # Generate username using the encapsulated method
            try:
                username = User.generate_username(program.code, user.id)
                user.username = username
            except ValueError as e:
                # Rollback user creation if username generation fails
                db.session.rollback()
                flash(f'Error generating username: {str(e)}. Please try again.', 'danger')
                return render_template('register.html', title='Register', form=form)
            
            # Commit once with real username set
            db.session.commit()
            send_verification_email(user)
            flash('Verification email sent! Check your KTH email to activate your account.', 'info')
            return redirect(url_for('users.login'))
        except Exception as e:
            # Rollback on any unexpected error
            db.session.rollback()
            flash('An error occurred during registration. Please try again.', 'danger')
            return render_template('register.html', title='Register', form=form)
    
    return render_template('register.html', title='Register', form=form)


@users.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            if not user.email_verified:
                flash('Please verify your email before logging in.', 'warning')
                return redirect(url_for('users.login', show_verification='true'))
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@users.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.home'))



@users.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        # Handle picture selection with validation
        if form.picture.data and validate_profile_picture(form.picture.data):
            current_user.image_file = form.picture.data
        elif form.picture.data:
            # Invalid picture selected, use default
            current_user.image_file = 'default1.png'
            flash('Selected profile picture was not available. Using default.', 'warning')
        
        if form.email.data != current_user.email:
            send_email_change_email(current_user, form.email.data)
            flash('A verification email has been sent to your new email. Your email will be updated once you click the link.', 'info')
            return redirect(url_for('users.account'))

        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('users.account')) # post-get-redirect pattern
    elif request.method == 'GET':
        form.email.data = current_user.email
        
        # Ensure current user's image file is valid, fallback to default if not
        if validate_profile_picture(current_user.image_file):
            form.picture.data = current_user.image_file
        else:
            current_user.image_file = 'default1.png'
            db.session.commit()
            form.picture.data = 'default1.png'

    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account', image_file=image_file, form=form)



from flasknetwork.main.utils import get_sorted_posts

@users.route('/user/<string:username>')
def user_posts(username):
    page=request.args.get('page', 1, type=int)
    sort_by = request.args.get('sort', 'newest')
    
    user = User.query.filter_by(username=username).first_or_404()
    
    # Filter by author first
    query = Post.query.filter_by(author=user)
    
    # Apply sorting
    query = get_sorted_posts(query, sort_by)
    
    posts = query.paginate(page=page, per_page=5)
    return render_template('user_posts.html', posts=posts, user=user, sort_by=sort_by)



@users.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('users.login'))
    return render_template('reset_request.html', title='Reset Password', form=form)


@users.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('users.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You can now log in', 'success')
        return redirect(url_for('users.login'))
    return render_template('reset_token.html', title='Reset Password', form=form, user=user)


@users.route('/verify_email/<token>')
def verify_email(token):
    user = User.verify_email_token(token)
    if user is None:
        flash('That is an invalid or expired verification link.', 'warning')
        return redirect(url_for('users.login'))
    if user.email_verified:
        flash('Account already verified. Please log in.', 'info')
        return redirect(url_for('users.login'))
    user.email_verified = True
    db.session.commit()
    flash('Your account has been verified! You can now log in.', 'success')
    return redirect(url_for('users.login'))


@users.route('/verify_change_email/<token>')
def verify_change_email(token):
    if current_user.is_authenticated:
        # If user is logged in, that's fine, we update them.
        # If not, verify_email_change_token loads the user from ID so it still works.
        pass

    result = User.verify_email_change_token(token)
    if result is None:
        flash('That is an invalid or expired token.', 'warning')
        return redirect(url_for('users.account'))
    
    user, new_email = result
    
    # Check if email is already taken (race condition edge case)
    existing_user = User.query.filter_by(email=new_email).first()
    if existing_user:
        flash('That email is already in use by another account.', 'danger')
        return redirect(url_for('users.account'))
        
    user.email = new_email
    user.email_verified = True
    db.session.commit()
    flash('Your email has been updated and verified!', 'success')
    return redirect(url_for('users.account'))


@users.route('/request_verification', methods=['GET', 'POST'])
def request_verification():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RequestVerificationForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_verification_email(user)
        flash('Verification email sent! Check your email.', 'info')
        return redirect(url_for('users.login'))
    return render_template('request_verification.html', title='Request Verification', form=form)