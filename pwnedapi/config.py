import os

basedir = os.path.abspath(os.path.dirname(__file__))

class BaseConfig(object):

    DEBUG = False
    SECRET_KEY = 'development key'
    PW_ENC_KEY = 'sekrit'
    UPLOAD_FOLDER = '/tmp/artifacts'
    ALLOWED_EXTENSIONS = set(['txt', 'xml', 'jpg', 'png', 'gif', 'pdf'])
    ALLOWED_MIMETYPES = set(['text/plain', 'application/xml', 'image/jpeg', 'image/png', 'image/gif', 'application/pdf'])
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = 'mysql://pwnedhub:dbconnectpass@localhost/pwnedhub'
    #[vuln] arbitrary reflected origin, providing a list enables whitelisting
    #CORS_ORIGINS = ['http://pwnedhub.com:5000', 'http://www.pwnedhub.com:5000']

class Development(BaseConfig):

    DEBUG = True

class Test(BaseConfig):

    DEBUG = True
    TESTING = True

class Production(BaseConfig):

    SECRET_KEY = 'M>\n\xb2\xa9B\xae\x8cL~\x0b\xc4\x19\r/GR6\xca\xd1^o\xa3$'
    #[vuln] arbitrary reflected origin, providing a list enables whitelisting
    #CORS_ORIGINS = ['http://pwnedhub.com', 'http://www.pwnedhub.com']
