from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

basedir = '/tmp'#os.path.abspath(os.path.dirname(__file__))

# configuration
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'pwnedhub.db')
DEBUG = True
TESTING = False
SECRET_KEY = 'development key'
PW_ENC_KEY = 'sekrit'
UPLOAD_FOLDER = '/tmp/artifacts'
ALLOWED_EXTENSIONS = set(['txt', 'xml'])

app = Flask(__name__)
app.config.from_object(__name__)

db = SQLAlchemy(app)

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
