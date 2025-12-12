# note: current script tries to add ALL tags.
# works if ran on a fresh DB
# if ran on a DB that already has tags, it will crash (IntegrityError) because of unique=True ??

# ran this on both prod db and local db

from dotenv import load_dotenv
import sys
import os

# Add parent directory to path to allow importing flasknetwork
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

load_dotenv(os.path.join(os.path.dirname(__file__), '../.env'))
  # seeding after migration
from flasknetwork import db, create_app
from flasknetwork.models import Tag, TagSentiment
   
app = create_app()
with app.app_context():
    tags_data = [
        ("Group Projects", TagSentiment.positive),
        ("Clear Grading Criteria", TagSentiment.positive),
        ("Lots of Reading", TagSentiment.negative),
        ("Entertaining Lectures", TagSentiment.positive),
        ("Textbook Required", TagSentiment.negative),
        ("Tough Grading", TagSentiment.negative),
        ("Bamboozling Exams", TagSentiment.negative),
        ("Friendly TAs", TagSentiment.positive),
        ("Professor & TAs are Accessible Outside Class", TagSentiment.positive),
        ("Recorded Lectures", TagSentiment.positive),
        ("LOTS of Assignments", TagSentiment.negative),
        ("Bad Course Layout", TagSentiment.negative),
        ("Lecture Heavy", TagSentiment.negative),
        #("Attendance Mandatory", TagSentiment.negative),
        ("Industry Relevant", TagSentiment.positive),
        ("Outdated Content", TagSentiment.negative),
    ]

    for name, sentiment in tags_data:
        tag = Tag(name=name, sentiment=sentiment)
        db.session.add(tag)
    db.session.commit()