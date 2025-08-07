# useful stuff

** OUTDATED "app" grejer! **

#### db stuff

set FLASK_APP=run.py
flask db init
flask db migrate -m "initial schema"
flask db upgrade

rmdir /s /q migrations

*import and push app first!!*
from sqlalchemy import text
db.session.execute(text('DROP TABLE IF EXISTS alembic_version'))
db.session.execute(text('DROP TABLE IF EXISTS _alembic_tmp_post'))
db.session.commit()

### listing all user-defined variables in the session

[v for v in locals() if not v.startswith('__')]


### finding courses with no program connection

[course for course in Course.query.all() if not course.course_programs]


### print all courses

for c in Course.query.all():
    c


## always do this first
from flasknetwork import create_app, db

from flasknetwork.models import User, Post, Program, Course, Course_Program

app = create_app()

app.app_context().push()


## find all related programs/courses for a course/program using the code

c = Course.query.filter_by(code="DD1337").first()

[cp.program for cp in c.course_programs]

*or*

p = Program.query.filter_by(code="TF").first()

[cp.course for cp in p.course_programs]


## PROGRAM CRUD & RELATIONSHIPS

program1 = Program(name='Teknisk Fysik', code='TF', program_type='bachelor')

db.session.add(program1); db.session.commit()       # create

Program.query.all()                                 # list all

db.session.get(Program, program1.id)                # get by PK (SQLAlchemy 2.0)

Program.query.filter_by(code='TF').first()          # filter by code

Program.query.filter_by(program_type='bachelor').all()  # filter by program_type

program1.name                                       # read name

program1.program_type                               # read program type

program1.students                                   # all User in this program

program1.course_programs                            # all Course_Program links

[p.course for p in program1.course_programs]        # all Courses in this program

*or print each one on new line*

for cp in program1.course_programs:
print(cp.course)

## COURSE CRUD & RELATIONSHIPS

course1 = Course(name='Programmering', code='DD1337')

db.session.add(course1); db.session.commit()        # create

Course.query.all()                                  # list all

db.session.get(Course, course1.id)                  # get by PK (SQLAlchemy 2.0)

*or*

specific_course = Course.query.filter_by(code='THECODE').first()

Course.query.filter(Course.code.like('%1337')).all()

>alternatives to the line above^
- Course.query.filter_by(code='DD1337').all()       # seems easiest
- Course.query.filter(Course.code.contains('1337')).all()
- Course.query.filter(Course.name.contains('architecture')).all()
- Course.query.filter(Course.code.endswith('1337')).all()

course1.course_programs                             # Course_Program links

[cp.program for cp in course1.course_programs]      # all Programs for this course


## LINK PROGRAM ⇆ COURSE

Course_Program.query.all()

cp = Course_Program(course=course1, program=program1)

db.session.add(cp); db.session.commit()              # associate

cp.course                                           # that Course

cp.program                                          # that Program



## USER CRUD & RELATIONSHIPS

user1 = User(username='bob', email='bob@kth.se', password='hashedpw', program=program1)

db.session.add(user1); db.session.commit()           # create

User.query.all()                                     # list all users

user1 = User.query.filter_by(username='bob').first()

user1.program                                        # that Program

user1.posts                                          # all Posts by user

program1.students    


## POST (REVIEW) CRUD & RELATIONSHIPS

post1 = Post(title='DD1337 Review', content='Great course!', author=user1, course=course1)

db.session.add(post1); db.session.commit()           # create

Post.query.all()                                     # list all posts

db.session.get(Post, post1.id)                       # get by PK (SQLAlchemy 2.0)

Post.query.filter_by(user_id=user1.id).all()         # all posts by user1

course1.reviews                                      # all posts for course1


## UPDATES

user1.email = 'bob2@kth.se'; db.session.commit()     # change & save

course1.name = 'DD1337 – Programmering'; db.session.commit()


## DELETIONS

db.session.delete(post1); db.session.commit()        # delete post

db.session.delete(cp); db.session.commit()           # delete program–course link

db.session.delete(user1); db.session.commit()        # delete user


## SESSION MANAGEMENT

db.session.rollback()                                # undo uncommitted changes

db.session.add_all([program1, course1]); db.session.commit()  # add many

db.session.expunge(user1)                            # remove from session

db.session.is_modified(user1)                        # check dirty


## AGGREGATES & COUNTS

User.query.count()                                   # number of users

Course.query.count()                                 # number of courses

Program.query.count()  


## start up db
db.create_all()


## delete db
db.drop_all()


# older stuff


## add user
user1 = User(username='testuser', email='test@example.com', password='password')
db.session.add(user1)
db.session.commit()


## list all users
User.query.all()


## get user by username
user = User.query.filter_by(username='aryan').first()


## update email
user.email = 'newemail@example.com'
db.session.commit()


## delete user
user = User.query.filter_by(username='aryan').first()
db.session.delete(user)
db.session.commit()


# TODO:
*new*
* write review in courses/course/id should check if the user has already reviewed that course. if so, don't display "Write review".
* don't need TWO buttons to write a new review?? either keep "Add your Review" or "Write Review"
* margin or spacing or whatever for "Back to Search" and "Write Review" in course/courses/id for those with no reviews are very ugly.
* make "Back to Search" prettier in courses/course/id. and perhaps move it to top left
* perhaps the "Course Information" box could be the sidebar? looks weird with 2 of them
* fix text sizing in create_post (course title and content inputs are bigger than the rest)
* what does manually changing the id in "/post/new?course_id=2" change? it doesn't update the selected course? and it seems to have no effect on what courses the user can post for. so what does changing the id DO?
* ^^related to the above: pressing "Write the First Review" in an empty course takes me to "/post/new?course_id=2" but the selected course is still the first one (with id=1)?? what other issues does this have (where else is this exact functionality used?)
* fix the autocomplete
* change questions in post!
* sidebar: override it or edit it on certain subpages? refactor needed? if kept: fix/delete for mobile!
* "my reviews" in /account
* browse programs/courses
* notification system? maybe a bit annoying.


1. long blogpost titles go outside of the window lol (fixed?)
2. avoid names that are only differently capitalized
3. clean up unused profile pictures
4. change "create_post" to "manage_post" or something since now it also edits the posts