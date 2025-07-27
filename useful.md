# useful stuff

## always do this first
from flasknetwork import app, db
from flasknetwork.models import User, Post


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


## get user by username
user = User.query.filter_by(username='aryan').first()


## update email
user.email = 'newemail@example.com'
db.session.commit()



# todo
1. long blogpost titles go outside of the window lol (fixed?)
2. avoid names that are only differently capitalized
3. clean up unused profile pictures
4. change "create_post" to "manage_post" or something since now it also edits the posts