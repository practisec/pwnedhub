import os

class SharedConfig(object):

    DEBUG = False
    SECRET_KEY = 'M>\n\xb2\xa9B\xae\x8cL~\x0b\xc4\x19\r/GR6\xca\xd1^o\xa3$'
    PW_ENC_KEY = 'sekrit'
    API_CONFIG_KEY_NAME = 'X-API-Key'
    API_CONFIG_KEY_VALUE = 'verysekrit'
    UPLOAD_FOLDER = '/tmp/artifacts'
    ALLOWED_EXTENSIONS = set(['txt', 'xml', 'jpg', 'png', 'gif', 'pdf'])
    ALLOWED_MIMETYPES = set(['text/plain', 'application/xml', 'image/jpeg', 'image/png', 'image/gif', 'application/pdf'])
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DATABASE_HOST = os.environ.get('DATABASE_HOST', 'localhost')
    SQLALCHEMY_DATABASE_URI = f"mysql://pwnedhub:dbconnectpass@{DATABASE_HOST}/pwnedhub"
    # prevents connection pool exhaustion
    # but disables interactive debugging
    PRESERVE_CONTEXT_ON_EXCEPTION = False
