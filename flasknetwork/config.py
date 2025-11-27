import os

class Config:
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY')
    
    # Render uses DATABASE_URL; fallback to local dev variable
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or os.environ.get('FLASK_SQLALCHEMY_DATABASE_URI')
    # Render uses postgres:// but SQLAlchemy requires postgresql://
    if SQLALCHEMY_DATABASE_URI and SQLALCHEMY_DATABASE_URI.startswith('postgres://'):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace('postgres://', 'postgresql://', 1)
    
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('FLASK_EMAIL_USER')
    MAIL_PASSWORD = os.environ.get('FLASK_EMAIL_PASS')