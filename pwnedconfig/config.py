from common.config import SharedBaseConfig, SharedDevConfig, SharedTestConfig, SharedProdConfig

class BaseConfig(SharedBaseConfig):

    pass

class Development(SharedDevConfig, BaseConfig):

    pass

class Test(SharedTestConfig, BaseConfig):

    pass

class Production(SharedProdConfig, BaseConfig):

    pass
