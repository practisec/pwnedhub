import os


class BaseConfig(object):

    # base
    DEBUG = False
    SECRET_KEY = '$ecretKey'
    # prevents connection pool exhaustion but disables interactive debugging
    PRESERVE_CONTEXT_ON_EXCEPTION = False

    # oidc
    OAUTH_PROVIDERS = {
        'google': {
            'CLIENT_ID': '1098478339188-pvi39gpsvclmmucvu16vhrh0179sd100.apps.googleusercontent.com',
            'CLIENT_SECRET': '5LFAbNk7rLa00PZOHceQfudp',
            'DISCOVERY_DOC': 'https://accounts.google.com/.well-known/openid-configuration',
        },
    }

    # csrf
    CSRF_TOKEN_NAME = 'X-Csrf-Token'

    # other
    API_BASE_URL = 'http://api.pwnedhub.com'


class Development(BaseConfig):

    DEBUG = True


class Test(object):

    DEBUG = True
    TESTING = True


class Production(BaseConfig):

    pass
