from flask.ext.wtf import Form, TextField, TextAreaField, PasswordField, validators

class LoginForm(Form):
    email = TextField('Email', [validators.required()])
    password = PasswordField('Password', [validators.required()])

class NoteForm(Form):
    title = TextField('Title', [validators.optional()])
    raw_entry = TextAreaField('Entry', [validators.required()])
    tags = TextField('Tags', [validators.optional()])
