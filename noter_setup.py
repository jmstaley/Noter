import bcrypt
import getpass
from noter import init_db, create_user

init_db()

while True:
    admin = raw_input("Admin username?\t").strip()
    if admin != '':
        break

while True:
    raw_pass = getpass.getpass("Admin password?\t").strip()
    if raw_pass != '':
        break

while True:
    email = raw_input("Admin email?\t").strip()
    if email != '':
        break

passwd = bcrypt.hashpw(raw_pass, bcrypt.gensalt())
create_user(admin, passwd, email)
