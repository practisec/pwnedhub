import os

basedir = os.path.abspath(os.path.dirname(__file__))

class BaseConfig(object):

    DEBUG = False
    SECRET_KEY = 'development key'
    UPLOAD_FOLDER = '/tmp/artifacts'
    ALLOWED_EXTENSIONS = set(['txt', 'xml', 'jpg', 'png', 'gif', 'pdf'])
    ALLOWED_MIMETYPES = set(['text/plain', 'application/xml', 'image/jpeg', 'image/png', 'image/gif', 'application/pdf'])
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = 'mysql://pwnedhub:dbconnectpass@localhost/pwnedhub'

class Development(BaseConfig):

    DEBUG = True

class Test(BaseConfig):

    DEBUG = True
    TESTING = True

class Production(BaseConfig):

    SECRET_KEY = 'M>\n\xb2\xa9B\xae\x8cL~\x0b\xc4\x19\r/GR6\xca\xd1^o\xa3$'
