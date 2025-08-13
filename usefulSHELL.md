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


## ALL courses a user hasn't reviewed (including those not in program)

reviewed_courses = [post.course for post in user1.posts]

not_reviewed_courses = [course for course in Course.query.all() if course not in reviewed_courses]



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

post1 = Post(
    title='DD1337 Review',
    year_taken=2025,
    rating=4,
    answer_q1='Yes, I’d recommend.',
    answer_q2='Challenging but fun.', # NEW (can) omit for None)
    author=user1,
    course=course1
)

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
* "taken in YEAR" texten är konstig på mobil
* mycket weird blankspace till höger på alla posts
* kolla notes på luren!
* make "Back to Search" prettier in courses/course/id (antingen ta bort texten och bara ha pil eller gör den mindre). and perhaps move it to top left (Maybe add the gradient-anim class?!) more it to somewhere better placed (AND BE WARE OF DOWNSTREAM ISSUES OF WHERE THE BACK TO SEARCH WAS! i think the text to the left is spaced or something dependent on or with attention to the button)
* make ratings (when publishing a post, and maybe also in /home) which have yellow background gradients?
* make all post/submit/"read full review"/"back to home" buttons gradient anims
* browse the website on mobile! It's shit!! ("course information" for each courses/course/id is below the actual reviews??)
* pre-filling the select dropdown in /post/new?course_id=1 based on the id in the URL. it currently doesn't update the selected course. (see help_post_select_dropdown.txt in Desktop for more info. models struggled with this, it seems either SelectOptGroupWidget or PostForm or the new_post() route is causing issues, maybe overriding or something)
* ^^related to the above: pressing "Write the First Review" in an empty course takes me to "/post/new?course_id=2" but the selected course is still the first one (with id=1)??
* fix color hierarchy in posts!! color of questions and stuff should be lighter than title and so on! (check twitter! https://x.com/heysatya_/status/1952975293590958444 )
* fix the autocomplete
* only allow @kth.se emails! (@ug.kth.se is the same anyways?! just makes for more complications)
* add a random name generator for username on register (reddit-type names)
* autofill login (and maybe register? but then maybe it's not as obvious that only @kth.se mails are allowed??) with @kth.se so users only need to type the first part on login
* fix the 'remember me' or delete it!
* change questions in post!
* make the "New Post" (should be New Review maybe) prettier and more popping (add an icon?)
* "my reviews" in /account
* browse programs/courses
* remove the blue border that appears when clicking the New Post (gradient-anim) button???

* testa: pagination på course_details page (/courses/course/id)

* LATER: notification system? maybe a bit annoying.
* LATER: if an auth user makes a search then sort the search in 2 sections "my program" and "all courses"
* LATER: REQUIRES CUSTOM DROPDOWN LIBRARIES! fix the course dropdown (when open) in /post/new (if possible!), it's very ugly! fix!


1. long blogpost titles go outside of the window lol (fixed?)
2. avoid names that are only differently capitalized
3. clean up unused profile pictures
4. change "create_post" to "manage_post" or something since now it also edits the posts




# adding dummy data
*after pushing app and stuff*

prog = Program.query.filter_by(name="Computer Science and Engineering").first()
course = Course.query.filter_by(name="Algorithms and Data Structures").first()

for i in range(1, 6):
    email = f"dummy{i}@kth.se"
    if User.query.filter_by(email=email).first():
        continue  # skip existing

    u = User(
        username=f"dummy{i}",
        email=email,
        password="password",
        program=prog
    )
    db.session.add(u)

    review = Post(
        title=f"Algorithms Review #{i}",
        year_taken=2025,
        rating=4,
        answer_q1="Solid course, learned a lot.",
        author=u,
        course=course
    )
    db.session.add(review)

db.session.commit()