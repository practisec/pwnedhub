from cachelib.file import FileSystemCache
import os


class BaseConfig(object):

    # base
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.getenv('SECRET_KEY', default='$ecretKey')
    # prevents connection pool exhaustion but disables interactive debugging
    PRESERVE_CONTEXT_ON_EXCEPTION = False
    MESSAGES_PER_PAGE = 5

    # database
    DATABASE_HOST = os.environ.get('DATABASE_HOST', 'localhost')
    SQLALCHEMY_DATABASE_URI = f"mysql://pwnedhub:dbconnectpass@{DATABASE_HOST}/pwnedhub"
    SQLALCHEMY_BINDS = {
        'admin': f"mysql://pwnedhub:dbconnectpass@{DATABASE_HOST}/pwnedhub-admin"
    }
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # redis
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://')

    # file upload
    UPLOAD_FOLDER = '/tmp/artifacts'
    ALLOWED_EXTENSIONS = set(['txt', 'xml', 'jpg', 'png', 'gif', 'pdf'])
    ALLOWED_MIMETYPES = set(['text/plain', 'application/xml', 'image/jpeg', 'image/png', 'image/gif', 'application/pdf'])

    # session
    SESSION_TYPE = 'cachelib'
    SESSION_SERIALIZATION_FORMAT = 'json'
    SESSION_CACHELIB = FileSystemCache(threshold=500, cache_dir='/tmp/sessions')
    SESSION_COOKIE_NAME = 'session'
    SESSION_COOKIE_HTTPONLY = False
    SESSION_REFRESH_EACH_REQUEST = False
    PERMANENT_SESSION_LIFETIME = 3600 # 1 hour

    # oidc
    OAUTH_PROVIDERS = {
        'google': {
            'CLIENT_ID': '1098478339188-pvi39gpsvclmmucvu16vhrh0179sd100.apps.googleusercontent.com',
            'CLIENT_SECRET': '5LFAbNk7rLa00PZOHceQfudp',
            'DISCOVERY_DOC': 'https://accounts.google.com/.well-known/openid-configuration',
        },
    }

    # markdown
    MARKDOWN_EXTENSIONS = [
        'markdown.extensions.tables',
        'markdown.extensions.extra',
        'markdown.extensions.attr_list',
        'markdown.extensions.fenced_code',
    ]


class Development(BaseConfig):

    DEBUG = True


class Test(BaseConfig):

    DEBUG = True
    TESTING = True


class Production(BaseConfig):

    pass
