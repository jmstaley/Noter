# Noter
#
# copyright: (c) 2011 by Jon Staley.
# license: GPLv3, see LICENSE for more details.

import markdown
from datetime import datetime
from flask import request, redirect, url_for, \
    abort, render_template, flash
from flaskext.login import LoginManager, login_user, logout_user, \
    current_user, login_required
from sqlalchemy import desc

from forms import LoginForm, NoteForm
from models import db, app, Note, Tag, User

# config
DATABASE = '/tmp/noter.db'
DEBUG = True
SECRET_KEY = 'development key'

login_manager = LoginManager()                                                                                                                   
login_manager.setup_app(app)
login_manager.login_view = '/login'

app.config.from_object(__name__)

app.config.from_envvar('NOTER_SETTINGS', silent=True)

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

def save(form, note_id=None):
    ''' save or update note '''
    tags = []
    html_entry =  markdown.markdown(form.entry.data, ['codehilite'])

    if form.tags.data:
        tags = form.tags.data.split(',')

    if tags:
        nt = save_tags(tags)

    if note_id:
        note = Note.query.get(note_id)
        note.title = form.title.data
        note.html_entry = html_entry
        note.raw_entry = form.entry.data
        note.tags = nt
        db.session.merge(note)
    else:
        uid = current_user.id
        note = Note(uid, 
                    form.title.data, 
                    html_entry, 
                    form.entry.data,
                    nt,
                    datetime.now())
        note_id = note.id
        db.session.add(note)
    db.session.commit()

def save_tags(tags):
    ''' save all tags to the appropriate tables '''
    new_tags = []
    for tag in tags:
        tag = tag.strip()

        tag_exists = Tag.query.filter_by(value=tag).first()

        if not tag_exists:
            new_tag = Tag(tag)
            db.session.add(new_tag)
            db.session.commit()
            tag_id = new_tag.id
            new_tags.append(new_tag)
        else:
            tag_id = tag_exists.id
            new_tags.append(tag_exists)
    return new_tags

@app.route('/')
def show_notes():
    ''' show notes '''
    notes = []
    if current_user.is_authenticated():
        notes = Note.query.filter_by(uid=current_user.id).order_by(desc(Note.created_date))
    return render_template('list_view.html', notes=notes)

@login_required
@app.route('/add', methods=['GET','POST'])
def add_note():
    ''' add note form '''
    form = NoteForm()
    if form.validate_on_submit():
        save(form)
        return redirect(url_for('show_notes'))
    return render_template('add_note.html', form=form)

@login_required
@app.route('/remove/<note_id>')
def remove_note(note_id):
    ''' remove individual note '''
    note = Note.query.get(note_id)
    db.session.delete(note)
    db.session.commit()
    flash('Note was successfully removed')
    return redirect(url_for('show_notes'))

@app.route('/view/<note_id>', methods=['GET', 'POST'])
def view_note(note_id):
    ''' view individual note '''
    note = Note.query.filter_by(id=note_id, uid=current_user.id).first()
    tags = note.tags
    tags_string = ', '.join([tag.value for tag in tags])
    if not note:
        abort(404)
        
    form = NoteForm()

    # hack to populate fields until using objects
    if request.method == 'GET':
        form.title.data = note.title
        form.entry.data = note.raw_entry
        form.tags.data = tags_string

    if form.validate_on_submit():
        save(form, note_id=note_id)
        flash('Note was successfully saved')
        return redirect(url_for('show_notes'))

    return render_template('view_note.html', 
                           note=note,
                           tags=tags,
                           form=form)

@app.route('/tag/<tag>')
def view_tags_notes(tag):
    tag_obj = Tag.query.filter_by(value=tag).first()
    title = 'Notes for tag: %s' % tag

    notes = tag_obj.notes.all()

    return render_template('list_view.html', notes=notes, title=title)

@app.route('/login', methods=['GET', 'POST'])
def login():                                                                                                                                     
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user.check_login(form.password.data):
            login_user(user)
            return redirect(url_for('show_notes'))
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    ''' logout user '''
    logout_user()
    flash('You were logged out')
    return redirect(url_for('show_notes'))

if __name__ == '__main__':
    app.run()
