from flaskext.script import Manager
import bcrypt
from noter import app, db, create_user

manager = Manager(app)

@manager.command
def initdb():
    """ create all database tables """
    with app.test_request_context():
        db.create_all()

@manager.command
def dropdb():
    """ drops all database tables """
    with app.test_request_context():
        db.drop_all()

@manager.option('-u', '--username', dest="username", help="username")
@manager.option('-p', '--password', dest="password", help="password")
@manager.option('-e', '--email', dest="email", help="email")
def createuser(username, password, email):
    """ create a new user """
    passwd = bcrypt.hashpw(password, bcrypt.gensalt())
    with app.test_request_context():
        create_user(username, passwd, email)

if __name__ == "__main__":
    manager.run()
