from flask import Blueprint, request, redirect, url_for, \
    abort, render_template, flash
from flaskext.login import login_user, logout_user, \
    current_user, login_required

from sqlalchemy import desc
import markdown
from datetime import datetime

from forms import LoginForm, NoteForm
from models import db, Note, Tag, User

note_views = Blueprint('notes', __name__,
                       template_folder='templates')

@note_views.route('/')
def show_notes():
    ''' show notes '''
    notes = []
    if current_user.is_authenticated():
        notes = get_notes()
    tags = Tag.query.all()
    return render_template('list_view.html', notes=notes, tags=tags)

@note_views.route('/<page_num>')
def show_page(page_num=1):
    ''' show paginated notes '''
    notes = []
    if current_user.is_authenticated():
        notes = get_notes(page_num)
    return render_template('list_view.html', notes=notes)

@login_required
@note_views.route('/add', methods=['GET','POST'])
def add_note():
    ''' add note form '''
    form = NoteForm()
    if form.validate_on_submit():
        save(form)
        return redirect(url_for('notes.show_notes'))
    return render_template('add_note.html', form=form)

@login_required
@note_views.route('/remove/<note_id>')
def remove_note(note_id):
    ''' remove individual note '''
    note = Note.query.get(note_id)
    db.session.delete(note)
    db.session.commit()
    flash('Note was successfully removed')
    return redirect(url_for('notes.show_notes'))

@note_views.route('/view/<note_id>', methods=['GET', 'POST'])
def view_note(note_id):
    ''' view individual note '''
    note = Note.query.filter_by(id=note_id, uid=current_user.id).first()
    tags = note.tags
    tags_string = ', '.join([tag.value for tag in tags])
    if not note:
        abort(404)
        
    form = NoteForm(obj=note)

    # hack to populate tag field
    # tags are a list of objects need to hack string into form
    if request.method == 'GET':
        form.tags.data = tags_string

    if form.validate_on_submit():
        save(form, note_id=note_id)
        flash('Note was successfully saved')
        return redirect(url_for('notes.show_notes'))

    return render_template('view_note.html', 
                           note=note,
                           tags=tags,
                           form=form)

@note_views.route('/tag/<tag>')
def view_tags_notes(tag):
    tag_obj = Tag.query.filter_by(value=tag).first()
    title = 'Notes for tag: %s' % tag

    notes = tag_obj.notes
    notes = notes.paginate(page=1)

    return render_template('list_view.html', notes=notes, title=title)

@note_views.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user.check_login(form.password.data):
            login_user(user)
            return redirect(url_for('notes.show_notes'))
    return render_template('login.html', form=form)

@note_views.route('/logout')
def logout():
    ''' logout user '''
    logout_user()
    flash('You were logged out')
    return redirect(url_for('notes.show_notes'))

@note_views.route('/signup')
def signup():
    ''' user registration '''
    return render_template('signup.html')

def get_notes(page_num=1):
    notes = Note.query.filter_by(uid=current_user.id).order_by(desc(Note.created_date))
    page_notes = notes.paginate(int(page_num), per_page=10)
    return page_notes

def save(form, note_id=None):
    ''' save or update note '''
    tags = []
    nt = []
    html_entry =  markdown.markdown(form.raw_entry.data, ['codehilite'])

    if form.tags.data:
        tags = form.tags.data.split(',')

    if tags:
        nt = save_tags(tags)

    if note_id:
        note = Note.query.get(note_id)
        note.title = form.title.data
        note.html_entry = html_entry
        note.raw_entry = form.raw_entry.data
        note.tags = nt
        db.session.merge(note)
    else:
        uid = current_user.id
        note = Note(uid, 
                    form.title.data, 
                    html_entry, 
                    form.raw_entry.data,
                    nt,
                    datetime.now())
        note_id = note.id
        db.session.add(note)
    db.session.commit()

def save_tags(tags):
    ''' save all tags to the note_viewsropriate tables '''
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
