import bcrypt
from flaskext.sqlalchemy import SQLAlchemy
from sqlalchemy import event
from sqlalchemy.orm.session import Session

db = SQLAlchemy()

tags = db.Table('tags',
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id')),
    db.Column('note_id', db.Integer, db.ForeignKey('note.id')),
    db.Column('link_id', db.Integer, db.ForeignKey('link.id'))
)

@event.listens_for(Session, 'after_flush')
def delete_tag_orphans(session, ctx):
    session.query(Tag).\
        filter(~Tag.notes.any()).\
        delete(synchronize_session=False)

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

    def __init__(self, uid, title, html_entry, raw_entry, tags, created_date):
        self.uid = uid
        self.title = title
        self.html_entry = html_entry
        self.raw_entry = raw_entry
        self.tags = tags
        self.created_date = created_date

    def __repr__(self):
        return '<Note %s>' % self.title

class Link(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Integer, db.ForeignKey('user.id'))
    title = db.Column(db.String(255))
    url = db.Column(db.String(255))
    created_date = db.Column(db.DateTime())
    tags = db.relationship('Tag', secondary=tags,
        backref=db.backref('links', lazy='dynamic'))

#    def __init__(self, uid, title, url, created_date):
#        self.uid = uid
#        self.title = title
#        self.url = url
#        self.created_date = created_date

    def __repr__(self):
        return '<Link %s>' % self.title

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.String(80))

    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return '<Tag %s>' % self.value
