# useful stuff

** OUTDATED "app" grejer! **

## always do this first
from flasknetwork import create_app, db
from flasknetwork.models import User, Post, Program, Course, Professor, Course_Program, Course_Professor
app = create_app()
app.app_context().push()


## PROGRAM CRUD & RELATIONSHIPS
program1 = Program(name='Teknisk Fysik', code='TF') 
db.session.add(program1); db.session.commit()       # create
Program.query.all()                                 # list all
Program.query.get(program1.id)                      # get by PK
Program.query.filter_by(code='TF').first()          # filter
program1.name                                       # read field
program1.students                                   # all User in this program
program1.course_programs                            # all Course_Program links
[p.course for p in program1.course_programs]        # all Courses in this program


## COURSE CRUD & RELATIONSHIPS
course1 = Course(name='Programmering', code='DD1337')
db.session.add(course1); db.session.commit()        # create
Course.query.all()                                  # list all
Course.query.get(course1.id)                        # get by PK
Course.query.filter(Course.code.like('%1337')).all()
course1.course_programs                             # Course_Program links
[cp.program for cp in course1.course_programs]      # all Programs for this course


## LINK PROGRAM ⇆ COURSE
cp = Course_Program(course=course1, program=program1)
db.session.add(cp); db.session.commit()              # associate
cp.course                                           # that Course
cp.program                                          # that Program


## PROFESSOR CRUD & RELATIONSHIPS
prof1 = Professor(name='Dr. Euler')
db.session.add(prof1); db.session.commit()           # create
Professor.query.all()                                # list all
prof1.course_professors                              # Course_Professor links
[c.course for c in prof1.course_professors]          # Courses taught


## LINK COURSE ⇆ PROFESSOR
cp2 = Course_Professor(course=course1, professor=prof1, semester_taught='HT2023', is_current=True)
db.session.add(cp2); db.session.commit()             # associate
course1.course_professors                            # links for course
prof1.course_professors                              # links for professor


## USER CRUD & RELATIONSHIPS
user1 = User(username='bob', email='bob@kth.se', password='hashedpw', program=program1)
db.session.add(user1); db.session.commit()           # create
User.query.all()                                     # list all users
user1 = User.query.filter_by(username='bob').first()
user1.program                                        # that Program
user1.posts                                          # all Posts by user
program1.students    


## POST (REVIEW) CRUD & RELATIONSHIPS
post1 = Post(title='DD1337 Review', content='Great course!', author=user1, course=course1, professor=prof1)
db.session.add(post1); db.session.commit()           # create
Post.query.all()                                     # list all posts
Post.query.get(post1.id)                             # get by PK
Post.query.filter_by(user_id=user1.id).all()         # all posts by user1
course1.reviews                                      # all posts for course1
prof1.reviews                                        # all posts for prof1


## UPDATES
user1.email = 'bob2@kth.se'; db.session.commit()     # change & save
course1.name = 'DD1337 – Programmering'; db.session.commit()


## DELETIONS
db.session.delete(post1); db.session.commit()        # delete post
db.session.delete(cp2); db.session.commit()          # delete course–professor link
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


# todo
1. long blogpost titles go outside of the window lol (fixed?)
2. avoid names that are only differently capitalized
3. clean up unused profile pictures
4. change "create_post" to "manage_post" or something since now it also edits the posts