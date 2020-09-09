import os

class SharedBaseConfig(object):

    # all
    DEBUG = False
    SECRET_KEY = 'M>\n\xb2\xa9B\xae\x8cL~\x0b\xc4\x19\r/GR6\xca\xd1^o\xa3$'

    # app, api
    PW_ENC_KEY = 'sekrit'
    DATABASE_HOST = os.environ.get('DATABASE_HOST', 'localhost')
    SQLALCHEMY_DATABASE_URI = f"mysql://pwnedhub:dbconnectpass@{DATABASE_HOST}/pwnedhub"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # prevents connection pool exhaustion but disables interactive debugging
    PRESERVE_CONTEXT_ON_EXCEPTION = False
    UPLOAD_FOLDER = '/tmp/artifacts'
    ALLOWED_EXTENSIONS = set(['txt', 'xml', 'jpg', 'png', 'gif', 'pdf'])
    ALLOWED_MIMETYPES = set(['text/plain', 'application/xml', 'image/jpeg', 'image/png', 'image/gif', 'application/pdf'])

    # app, spa
    OAUTH_PROVIDERS = {
        'google': {
            'CLIENT_ID': '1098478339188-pvi39gpsvclmmucvu16vhrh0179sd100.apps.googleusercontent.com',
            'CLIENT_SECRET': '5LFAbNk7rLa00PZOHceQfudp',
            'DISCOVERY_DOC': 'https://accounts.google.com/.well-known/openid-configuration',
        },
    }

    # spa, api
    CSRF_TOKEN_NAME = 'X-Csrf-Token'

    # unused
    API_CONFIG_KEY_NAME = 'X-API-Key'
    API_CONFIG_KEY_VALUE = 'verysekrit'

class SharedDevConfig(object):

    DEBUG = True

class SharedTestConfig(object):

    DEBUG = True
    TESTING = True

class SharedProdConfig(object):

    pass
