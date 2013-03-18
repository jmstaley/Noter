# Noter
#
# copyright: (c) 2011 by Jon Staley.
# license: GPLv3, see LICENSE for more details.

from datetime import datetime
from flask import Flask
from flaskext.login import LoginManager

from views import note_views
from models import db, User

# config
DEBUG = True
SECRET_KEY = 'development key'
BASE_DIR = '/tmp/'

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/notes.db'

app.config.from_object(__name__)

app.config.from_envvar('NOTER_SETTINGS', silent=True)

login_manager = LoginManager()                                                                                                                   
login_manager.setup_app(app)
login_manager.login_view = '/login'

app.register_blueprint(note_views)

db.init_app(app)

if not app.debug:
    import logging
    from logging import FileHandler
    file_handler = FileHandler('/%s/noter.log' % BASE_DIR)
    file_handler.setLevel(logging.WARNING)
    app.logger.addHandler(file_handler)

def init_db():
    ''' setup database tables '''
    db.create_all()

def create_user(user, pw_hash, email):
    new_user = User(user, pw_hash, email, datetime.now())
    db.session.add(new_user)
    db.session.commit()

@login_manager.user_loader
def load_user(uid):
    return User.query.get(uid)

if __name__ == '__main__':
    app.run()
