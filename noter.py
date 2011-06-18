# Noter
#
# copyright: (c) 2011 by Jon Staley.
# license: GPLv3, see LICENSE for more details.

import sqlite3
from flask import Flask, request, session, g, redirect, url_for, \
    abort, render_template, flash
from contextlib import closing

# config
DATABASE = '/tmp/noter.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'

app = Flask(__name__)
app.config.from_object(__name__)

app.config.from_envvar('NOTER_SETTINGS', silent=True)

def connect_db():
    ''' connect to data base in config '''
    return sqlite3.connect(app.config['DATABASE'])

def init_db():
    ''' setup database tables '''
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql') as f:
            db.cursor().executescript(f.read())
        db.commit()

def query_db(query, args=(), one=False):
    cur = g.db.execute(query, args)
    rv = [dict((cur.description[idx][0], value)
               for idx, value in enumerate(row)) for row in cur.fetchall()]
    return (rv[0] if rv else None) if one else rv

def save_tags(tags, note_id):
    ''' save all tags to the appropriate tables '''
    for tag in tags:
        tag = tag.strip()

        tag_exists = query_db('select * from tags where tag = ?', [tag], one=True)

        if not tag_exists:
            cur = g.db.execute('insert into tags (tag) values (?)', [tag])
            tag_id = cur.lastrowid
        else:
            tag_id = tag_exists['id']

        g.db.execute('insert into note_tags (note_id, tag_id) values (?, ?)',
            [note_id, tag_id])
    g.db.commit()

@app.before_request
def before_request():
    ''' make database connection is present for each
        request '''
    g.db = connect_db()

@app.after_request
def after_request(response):
    ''' make sure that database connection is closed
    after each request'''
    g.db.close()
    return response

@app.route('/')
def show_notes():
    ''' show notes '''
    notes = query_db('select id, title, entry from notes order by id desc')
    return render_template('show_notes.html', notes=notes)

@app.route('/add', methods=['POST'])
def add_note():
    ''' add note entry '''
    if not session.get('logged_in'):
        abort(401)
    cur = g.db.execute('insert into notes (title, entry) values (?, ?)',
        [request.form['title'], request.form['entry']])
    note_id = cur.lastrowid
    g.db.commit()

    if request.form['tags']:
        tags = request.form['tags'].split(',')
        save_tags(tags, note_id)

    flash('New note was successflly posted')
    return redirect(url_for('show_notes'))

@app.route('/remove/<note_id>')
def remove_note(note_id):
    ''' remove individual note '''
    if not session.get('logged_in'):
        abort(401)
    g.db.execute('delete from notes where id=?', [note_id])
    g.db.commit()
    flash('Note was successfully removed')
    return redirect(url_for('show_notes'))

@app.route('/view/<note_id>')
def view_note(note_id):
    ''' view individual note '''
    note = query_db('select * from notes where id = ?', [note_id],
                    one=True)
    tags = query_db('select tags.id, tags.tag from tags, note_tags where note_tags.note_id = ? and note_tags.tag_id = tags.id', [note_id])

    if not note:
        abort(404)

    return render_template('view_note.html', note=note, tags=tags)

@app.route('/tag/<tag>')
def view_tags_notes(tag):
    notes = query_db('select notes.id, notes.title, notes.entry from notes, tags, note_tags where tags.tag = ? and note_tags.tag_id = tags.id and note_tags.note_id = notes.id', [tag])
    title = 'Notes for tag: %s' % tag

    return render_template('list_view.html', notes=notes, title=title)

@app.route('/login', methods=['GET', 'POST'])
def login():
    ''' login user '''
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username and password combination'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid username and password combination'
        else:
            session['logged_in'] = True
            flash('You are logged in')
            return redirect(url_for('show_notes'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    ''' logout user '''
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_notes'))

if __name__ == '__main__':
    app.run()
