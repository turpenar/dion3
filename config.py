import os
import psycopg2

class Config(object):
    DEBUG = False
    TESTING = False

    print(os.environ['DATABASE_URL'])

    DATABASE_URL = os.environ.get('DATABASE_URL')
    print(DATABASE_URL)
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')

    SECRET_KEY = 'Your Kung-Fu is Very Good'
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
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