import os


class BaseConfig(object):

    # base
    DEBUG = False
    SECRET_KEY = '$ecretKey'
    # prevents connection pool exhaustion but disables interactive debugging
    PRESERVE_CONTEXT_ON_EXCEPTION = False
    MESSAGES_PER_PAGE = 5

    # database
    DATABASE_HOST = os.environ.get('DATABASE_HOST', 'localhost')
    SQLALCHEMY_DATABASE_URI = f"mysql://pwnedhub:dbconnectpass@{DATABASE_HOST}/pwnedhub"
    SQLALCHEMY_BINDS = {
        'config': f"mysql://pwnedhub:dbconnectpass@{DATABASE_HOST}/pwnedhub-config"
    }
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # file upload
    UPLOAD_FOLDER = '/tmp/artifacts'
    ALLOWED_EXTENSIONS = set(['txt', 'xml', 'jpg', 'png', 'gif', 'pdf'])
    ALLOWED_MIMETYPES = set(['text/plain', 'application/xml', 'image/jpeg', 'image/png', 'image/gif', 'application/pdf'])

    # session
    SESSION_COOKIE_HTTPONLY = False
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


class Test(object):

    DEBUG = True
    TESTING = True


class Production(BaseConfig):

    pass
