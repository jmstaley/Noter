from flaskext.wtf import Form, TextField, TextAreaField, PasswordField, validators

class LoginForm(Form):
    username = TextField('Username', [validators.required()])
    password = PasswordField('Password', [validators.required()])

class NoteForm(Form):
    title = TextField('Title', [validators.optional()])
    raw_entry = TextAreaField('Entry', [validators.required()])
    tags = TextField('Tags', [validators.optional()])
