# Noter
#
# copyright: (c) 2011 by Jon Staley.
# license: GPLv3, see LICENSE for more details.

import markdown
from datetime import datetime
from flask import request, session, g, redirect, url_for, \
    abort, render_template, flash
from flaskext.login import LoginManager, login_user, logout_user, \
    current_user, login_required

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
    existing_tags = []
    tags = []
    html_entry =  markdown.markdown(form.entry.data, ['codehilite'])

    if note_id:
        cur = g.db.execute('update note set title=?, html_entry=?, raw_entry=? where id=?', 
            [form.title.data, html_entry, form.entry.data, note_id])
        existing_tags = get_note_tags(note_id)
    else:
        uid = current_user.id
        note = Note(uid, 
                    form.title.data, 
                    html_entry, 
                    form.entry.data,
                    datetime.now())
        db.session.add(note)
        db.session.commit()
        note_id = note.id

    if form.tags.data:
        # only send new tags to save
        tags = form.tags.data.split(',')
        tags = [tag.strip() for tag in tags if tag.strip() not in existing_tags]

    if tags:
        save_tags(tags, note_id)

def save_tags(tags, note_id):
    ''' save all tags to the appropriate tables '''
    # need to get notes existing tag and check for removal (seperate func)
    for tag in tags:
        tag = tag.strip()

        tag_exists = Tag.query.filter_by(value=tag).first()

        if not tag_exists:
            new_tag = Tag(tag)
            db.session.add(new_tag)
            db.session.commit()
            tag_id = new_tag.id
        else:
            tag_id = tag_exists.id

def get_note_tags(note_id):
    ''' return a list of a notes tags as strings '''
    existing_tags = Note.query.get(note_id).tags
    existing_tags = [tag['tag'] for tag in existing_tags]
    return existing_tags

@app.route('/')
def show_notes():
    ''' show notes '''
    notes = Note.query.order_by('created_date')
    return render_template('list_view.html', notes=notes)

@app.route('/add', methods=['GET','POST'])
@login_required
def add_note():
    ''' add note form '''
    if not session.get('logged_in'):
        abort(401)
    form = NoteForm()
    if form.validate_on_submit():
        save(form)
        return redirect(url_for('show_notes'))
    return render_template('add_note.html', form=form)

@app.route('/remove/<note_id>')
@login_required
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
    note = Note.query.get(note_id)
    tags = note.tags
    from pdb import set_trace; set_trace()
    tags_string = ', '.join([tag['tag'] for tag in tags])

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
    notes = query_db('select note.id, note.title, note.html_entry from note, tags, note_tags where tags.tag = ? and note_tags.tag_id = tags.id and note_tags.note_id = note.id', [tag])
    title = 'Notes for tag: %s' % tag

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
