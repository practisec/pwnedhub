from common.config import SharedBaseConfig, SharedDevConfig, SharedTestConfig, SharedProdConfig

class BaseConfig(SharedBaseConfig):

    API_BASE_URL = 'http://api.pwnedhub.com:5002'

class Development(SharedDevConfig, BaseConfig):

    pass

class Test(SharedTestConfig, BaseConfig):

    pass

class Production(SharedProdConfig, BaseConfig):

    API_BASE_URL = 'http://api.pwnedhub.com'
