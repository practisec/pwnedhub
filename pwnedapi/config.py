from common.config import SharedConfig

class BaseConfig(SharedConfig):

    #[vuln] arbitrary reflected origin, providing a list enables whitelisting
    #CORS_ORIGINS = ['http://pwnedhub.com:5000', 'http://www.pwnedhub.com:5000']
    pass

class Development(BaseConfig):

    DEBUG = True

class Test(BaseConfig):

    DEBUG = True
    TESTING = True

class Production(BaseConfig):

    #[vuln] arbitrary reflected origin, providing a list enables whitelisting
    #CORS_ORIGINS = ['http://pwnedhub.com', 'http://www.pwnedhub.com']
    pass
