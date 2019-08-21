from common.config import SharedConfig

class BaseConfig(SharedConfig):

    #[vuln] CSRF if set to False
    CSRF_PROTECT = False
    SESSION_COOKIE_HTTPONLY = False
    PERMANENT_SESSION_LIFETIME = 3600 # 1 hour
    MARKDOWN_EXTENSIONS = [
        'markdown.extensions.tables',
        'markdown.extensions.extra',
        'markdown.extensions.attr_list',
        'markdown.extensions.fenced_code',
    ]
    API_BASE_URL = 'http://api.pwnedhub.com:5001'
    OAUTH_PROVIDERS = {
        'google': {
            'CLIENT_ID': '1098478339188-pvi39gpsvclmmucvu16vhrh0179sd100.apps.googleusercontent.com',
            'CLIENT_SECRET': '5LFAbNk7rLa00PZOHceQfudp',
            'DISCOVERY_DOC': 'https://accounts.google.com/.well-known/openid-configuration',
        },
    }

class Development(BaseConfig):

    DEBUG = True

class Test(BaseConfig):

    DEBUG = True
    TESTING = True

class Production(BaseConfig):

    API_BASE_URL = 'http://api.pwnedhub.com'
