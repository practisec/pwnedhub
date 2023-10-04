import os


class BaseConfig(object):

    # base
    DEBUG = False
    SECRET_KEY = '$ecretKey'
    # prevents connection pool exhaustion but disables interactive debugging
    PRESERVE_CONTEXT_ON_EXCEPTION = False

    # database
    DATABASE_HOST = os.environ.get('DATABASE_HOST', 'localhost')
    SQLALCHEMY_DATABASE_URI = f"mysql://pwnedhub:dbconnectpass@{DATABASE_HOST}/pwnedhub-test"
    SQLALCHEMY_BINDS = {
        'config': f"mysql://pwnedhub:dbconnectpass@{DATABASE_HOST}/pwnedhub-config"
    }
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # csrf
    CSRF_TOKEN_NAME = 'X-Csrf-Token'

    # redis
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://')

    # cors
    CORS_SUPPORTS_CREDENTIALS = True
    ALLOWED_ORIGINS = ['http://www.pwnedhub.com', 'http://test.pwnedhub.com']

    # oidc
    OAUTH_PROVIDERS = {
        'google': {
            'CLIENT_ID': '1098478339188-pvi39gpsvclmmucvu16vhrh0179sd100.apps.googleusercontent.com',
            'CLIENT_SECRET': '5LFAbNk7rLa00PZOHceQfudp',
            'DISCOVERY_DOC': 'https://accounts.google.com/.well-known/openid-configuration',
        },
    }

    # other
    INBOX_PATH = os.environ.get('INBOX_PATH', '/tmp/inbox')

    # unused
    API_CONFIG_KEY_NAME = 'X-API-Key'
    API_CONFIG_KEY_VALUE = 'verysekrit'


class Development(BaseConfig):

    DEBUG = True


class Test(BaseConfig):

    DEBUG = True
    TESTING = True


class Production(BaseConfig):

    pass
