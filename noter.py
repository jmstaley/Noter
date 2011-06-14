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
    g.db.execute('insert into notes (title, entry, tags) values (?, ?, ?)',
        [request.form['title'], request.form['entry'], request.form['tags']])
    g.db.commit()
    flash('New note was successflly posted')
    return redirect(url_for('show_notes'))

@app.route('/view/<note_id>')
def view_note(note_id):
    ''' view individual note '''
    note = query_db('select * from notes where id = ?', [note_id],
                    one=True)
    if not note:
        abort(404)

    return render_template('view_note.html', note=note)

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
