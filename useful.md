# useful stuff

## always do this first
from app import app, db, Post, User


## when starting a shell
*( to first to create app context for flask/sqlalchemy commands without wrapping every command in "with app.app_context() )*
app.app_context().push()


## start up db
with app.app_context():
    db.create_all()
    print("success")

or

app.app_context().push()
db.create_all()


## delete context
db.drop_all()


## add user
user1 = User(username='testuser', email='test@example.com', password='password')
db.session.add(user1)
db.session.commit()


## list all users
User.query.all()


## get and update email specific
user.email = 'newemail@example.com'
db.session.commit()