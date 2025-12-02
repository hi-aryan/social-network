from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env

from flasknetwork import create_app, db, bcrypt
from flasknetwork.models import User, Post, Program, Course, WorkloadLevel

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
    hashed_password = bcrypt.generate_password_hash("password").decode('utf-8')
    user = User(username=f"dummy{i}", email=email, password=hashed_password, program=prog)
    db.session.add(user)
    db.session.flush()  # so user.id is available

    # now create one post per course in our list
    for course in courses:
        post = Post(
            title=f"{course.name} Review by dummy{i}",
            year_taken=2025,
            # rating is computed from professor, material, and peers ratings
            rating_professor=4,
            rating_material=3,
            rating_workload=WorkloadLevel.medium,
            rating_peers=4,
            content="Solid course overall. The professor was engaging and the material was interesting. Workload was manageable if you stay on top of things. Great classmates to work with!",
            author=user,
            course=course
        )
        db.session.add(post)

db.session.commit()