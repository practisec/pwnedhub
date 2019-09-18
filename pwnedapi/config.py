from common.config import SharedConfig

class BaseConfig(SharedConfig):

    CORS_SUPPORTS_CREDENTIALS = True
    ALLOWED_ORIGINS = ['http://pwnedhub.com:5000', 'http://www.pwnedhub.com:5000']

class Development(BaseConfig):

    DEBUG = True

class Test(BaseConfig):

    DEBUG = True
    TESTING = True

class Production(BaseConfig):

    ALLOWED_ORIGINS = ['http://pwnedhub.com', 'http://www.pwnedhub.com']
