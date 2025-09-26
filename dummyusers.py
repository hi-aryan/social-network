from flasknetwork import create_app, db
from flasknetwork.models import User, Post, Program, Course

app = create_app()
app.app_context().push()

# select a program for dummy data
prog = Program.query.filter_by(name="Computer Science and Engineering").first()

# pick two distinct courses (e.g. the first two, or you can randomize)
courses = Course.query.order_by(Course.id).limit(2).all()

for i in range(1, 6):
    email = f"dummy{i}@kth.se"
    if User.query.filter_by(email=email).first():
        continue

    # create dummy user
    user = User(username=f"dummy{i}", email=email, password="password", program=prog)
    db.session.add(user)
    db.session.flush()  # so user.id is available

    # now create one post per course in our list
    for course in courses:
        post = Post(
            title=f"{course.name} Review by dummy{i}",
            year_taken=2025,
            rating=4,
            answer_q1="Solid course, learned a lot.",
            answer_q2="Would recommend.",
            author=user,
            course=course
        )
        db.session.add(post)

db.session.commit()