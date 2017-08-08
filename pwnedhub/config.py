import os

basedir = os.path.abspath(os.path.dirname(__file__))

class BaseConfig(object):

    DEBUG = False
    SECRET_KEY = 'development key'
    PW_ENC_KEY = 'sekrit'
    UPLOAD_FOLDER = '/tmp'
    ALLOWED_EXTENSIONS = set(['txt', 'xml', 'jpg', 'png', 'gif'])
    SESSION_COOKIE_HTTPONLY = False
    PERMANENT_SESSION_LIFETIME = 3600 # 1 hour
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class Development(BaseConfig):

    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'pwnedhub.db')

class Test(BaseConfig):

    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

class Production(BaseConfig):

    SQLALCHEMY_DATABASE_URI = 'sqlite:///production.db'
