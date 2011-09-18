from flaskext.wtf import Form, TextField, PasswordField, validators

class LoginForm(Form):
    username = TextField('Username', [validators.required()])
    password = PasswordField('Password', [validators.required()])
