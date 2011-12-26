import bcrypt
from flask import Flask
from flaskext.sqlalchemy import SQLAlchemy

app = Flask(__name__)                                                                                                                            
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/notes.db'
db = SQLAlchemy(app)

tags = db.Table('tags',
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id')),
    db.Column('note_id', db.Integer, db.ForeignKey('note.id'))
)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True)
    pw_hash = db.Column(db.String(255))
    email = db.Column(db.String(120))
    created_date = db.Column(db.DateTime())

    def __init__(self, username, pw_hash, email, created_date):
        self.username = username
        self.pw_hash = pw_hash
        self.email = email
        self.created_date = created_date

    def __repr__(self):                                                                                                                          
        return '<User %s>' % self.username

    def is_active(self):
        return True

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)

    def check_login(self, password):
        return bcrypt.hashpw(password, self.pw_hash)

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Integer, db.ForeignKey('user.id'))
    title = db.Column(db.String(255))
    html_entry = db.Column(db.Text())
    raw_entry = db.Column(db.Text())
    tags = db.relationship('Tag', secondary=tags,
        backref=db.backref('notes', lazy='dynamic'))
    created_date = db.Column(db.DateTime())

    def __init__(self, uid, title, html_entry, raw_entry, created_date):
        self.uid = uid
        self.title = title
        self.html_entry = html_entry
        self.raw_entry = raw_entry
        self.created_date = created_date

    def __repr__(self):
        return '<Note %s>' % self.title

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.String(80))

    def __init__(self, value):
        self.value = value
