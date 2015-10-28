from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask.ext.spyne import Spyne
import os

basedir = os.path.abspath(os.path.dirname(__file__))

# configuration
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'pwnedhub.db')
#SQLALCHEMY_DATABASE_URI = 'mysql://root:pwaptadmin@localhost/pwnedhub'
DEBUG = True
TESTING = False
SECRET_KEY = 'development key'
PW_ENC_KEY = 'sekrit'
UPLOAD_FOLDER = os.path.join(basedir, 'artifacts')
ALLOWED_EXTENSIONS = set(['txt', 'xml', 'jpg', 'png', 'gif'])
# ;;session cookie with HttpOnly disabled
SESSION_COOKIE_HTTPONLY = False
#SESSION_REFRESH_EACH_REQUEST = False # not available in 0.10.1

# setting the static_url_path to blank serves static
# files from the web root, allowing for robots.txt
# ;;verbose robots.txt file
app = Flask(__name__, static_url_path='')
app.config.from_object(__name__)

db = SQLAlchemy(app)
spyne = Spyne(app)

def initdb():
    db.create_all()
    print 'Database initialized.'

def dropdb():
    db.drop_all()
    print 'Database dropped.'

import models
import views

def make_admin(username):
    user = models.User.get_by_username(username)
    user.role = 0
    db.session.add(user)
    db.session.commit()
