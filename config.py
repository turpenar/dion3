import os
import psycopg2
import dotenv as dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
dotenv.load_dotenv(os.path.join(basedir, '.env'))

FLASK_ENV = os.environ.get('FLASK_ENV')

class Config(object):
    DEBUG = False
    TESTING = False

    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'isolation_level': 'READ UNCOMMITTED'
        }
    SQLALCHEMY_POOL_SIZE = None
    SQLALCHEMY_POOL_TIMEOUT = None
    SESSION_TYPE = "sqlalchemy"
    SESSION_SQLALCHEMY = 'db'

class ProductionConfig(Config):
    DATABASE_URL = os.environ.get('DATABASE_URL_PRODUCTION')
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')

class DevelopmentConfig(Config):
    ENV = 'development'
    DEVELOPMENT = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL_DEVELOPMENT')

class TestingConfig(Config):
    TESTING = True