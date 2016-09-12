from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask.ext.spyne import Spyne
from flask.ext.session import Session
import os

basedir = os.path.abspath(os.path.dirname(__file__))

# configuration
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'pwnedhub.db')
DEBUG = True
TESTING = False
SECRET_KEY = 'development key'
PW_ENC_KEY = 'sekrit'
UPLOAD_FOLDER = '/tmp'
ALLOWED_EXTENSIONS = set(['txt', 'xml', 'jpg', 'png', 'gif'])
SESSION_COOKIE_HTTPONLY = False
PERMANENT_SESSION_LIFETIME = 3600 # 1 hour

# setting the static_url_path to blank serves static
# files from the web root, allowing for robots.txt
app = Flask(__name__, static_url_path='')
app.config.from_object(__name__)

db = SQLAlchemy(app)
spyne = Spyne(app)
Session(app)

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
