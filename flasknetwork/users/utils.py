import os
from PIL import Image
from flask import url_for, current_app
from flask_mail import Message
from flasknetwork import mail


def is_kth_domain(email):
    """Check if email belongs to KTH domain"""
    #allowed_domains = ['@kth.se', '@ug.kth.se']
    allowed_domains = ['@kth.se']
    return any(email.lower().endswith(domain) for domain in allowed_domains)


def get_available_profile_pictures():
    """Get list of available profile pictures for user selection"""
    profile_pics_dir = os.path.join(current_app.root_path, 'static/profile_pics')
    allowed_extensions = ['.jpg', '.jpeg', '.png']
    
    picture_choices = []
    
    try:
        if os.path.exists(profile_pics_dir):
            for filename in sorted(os.listdir(profile_pics_dir)):
                if any(filename.lower().endswith(ext) for ext in allowed_extensions):
                    # Create display name by removing extension and formatting
                    display_name = os.path.splitext(filename)[0].replace('_', ' ')
                    picture_choices.append((filename, display_name))
        
        # Ensure we always have at least a default option
        if not picture_choices:
            picture_choices.append(('default1.png', 'Default Avatar'))
            
    except (OSError, IOError) as e:
        # Fallback in case of filesystem issues
        current_app.logger.error(f"Error accessing profile pictures directory: {e}")
        picture_choices = [('default1.png', 'Default Avatar')]
    
    return picture_choices


def validate_profile_picture(filename):
    """Validate that a profile picture filename exists and is allowed"""
    if not filename:
        return False
        
    profile_pics_dir = os.path.join(current_app.root_path, 'static/profile_pics')
    picture_path = os.path.join(profile_pics_dir, filename)
    
    # Check file exists and has allowed extension
    allowed_extensions = ['.jpg', '.jpeg', '.png']
    return (os.path.isfile(picture_path) and 
            any(filename.lower().endswith(ext) for ext in allowed_extensions))


def resize_profile_picture(picture_path, output_size=(125, 125)):
    """Resize a profile picture to specified dimensions"""
    if not os.path.exists(picture_path):
        raise FileNotFoundError(f"Picture not found: {picture_path}")
    
    try:
        with Image.open(picture_path) as img:
            img.thumbnail(output_size, Image.Resampling.LANCZOS)
            img.save(picture_path, optimize=True, quality=85)
        return picture_path
    except Exception as e:
        raise ValueError(f"Error processing image {picture_path}: {e}")


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request', sender='ratekth@noreply.com', recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{ url_for('users.reset_token', token=token, _external=True) }

If you did not make this request then ignore this email and no changes will be made :)
'''
    mail.send(msg)


def send_verification_email(user):
    token = user.get_verification_token()
    msg = Message('Email Verification', sender='ratekth@noreply.com', recipients=[user.email])
    msg.body = f'''To verify your email, visit the following link:
{ url_for('users.verify_email', token=token, _external=True) }

If you did not make this request, ignore this email.
'''
    mail.send(msg)


def send_email_change_email(user, new_email):
    token = user.get_email_change_token(new_email)
    msg = Message('Confirm Email Change', sender='ratekth@noreply.com', recipients=[new_email])
    msg.body = f'''To confirm your email change to {new_email}, visit the following link:
{ url_for('users.verify_change_email', token=token, _external=True) }

If you did not make this request, ignore this email and your email will remain unchanged.
'''
    mail.send(msg)