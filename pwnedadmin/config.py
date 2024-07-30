import os


class BaseConfig(object):

    # base
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.getenv('SECRET_KEY', default='$ecretKey')
    # prevents connection pool exhaustion but disables interactive debugging
    PRESERVE_CONTEXT_ON_EXCEPTION = False

    # database
    DATABASE_HOST = os.environ.get('DATABASE_HOST', 'localhost')
    SQLALCHEMY_DATABASE_URI = f"mysql://pwnedhub:dbconnectpass@{DATABASE_HOST}/pwnedhub-admin"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class Development(BaseConfig):

    DEBUG = True


class Test(BaseConfig):

    DEBUG = True
    TESTING = True


class Production(BaseConfig):

    pass
