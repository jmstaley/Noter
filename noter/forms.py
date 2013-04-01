from flaskext.wtf import Form, TextField, TextAreaField, PasswordField, validators
from noter.models import User

class LoginForm(Form):
    username = TextField('Username', [validators.required()])
    password = PasswordField('Password', [validators.required()])

    def validate_username(form, field):
        try:
            user = User.query.filter_by(username=form.username.data).first()
        except:
            raise validators.ValidationError('Username/password incorrect')

class NoteForm(Form):
    title = TextField('Title', [validators.optional()])
    raw_entry = TextAreaField('Entry', [validators.required()])
    tags = TextField('Tags', [validators.optional()])
