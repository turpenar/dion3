

class Config(object):
    DEBUG = False
    TESTING = False

    SECRET_KEY = 'Your Kung-Fu is Very Good'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///main/users.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'isolation_level': 'READ UNCOMMITTED'
        }
    SESSION_TYPE = "sqlalchemy"
    SESSION_SQLALCHEMY = 'db'

class ProductionConfig(Config):
    pass

class DevelopmentConfig(Config):
    ENV = 'development'
    DEVELOPMENT = True
    DEBUG = True

class TestingConfig(Config):
    TESTING = True