from common.config import SharedBaseConfig, SharedDevConfig, SharedTestConfig, SharedProdConfig

class BaseConfig(SharedBaseConfig):

    CORS_SUPPORTS_CREDENTIALS = True
    ALLOWED_ORIGINS = ['http://www.pwnedhub.com:5000', 'http://test.pwnedhub.com:5001']

class Development(SharedDevConfig, BaseConfig):

    pass

class Test(SharedTestConfig, BaseConfig):

    pass

class Production(SharedProdConfig, BaseConfig):

    ALLOWED_ORIGINS = ['http://www.pwnedhub.com', 'http://test.pwnedhub.com']
