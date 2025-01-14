import os
from decouple import config
from datetime import timedelta

BASE_DIR = os.path.dirname(os.path.realpath(__file__))

class Config:
    SECRET_KEY = config('SECRET_KEY', 'my_secret_key')
    JWT_SECRET_KEY = config('JWT_SECRET_KEY')
    access_token_expire = timedelta(minutes=30)
    refresh_token_expire = timedelta(days=30)

class DevConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'db.sqlite3') # use sqlite database
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    FLASK_ECHO = True

class ProdConfig(Config):
    # DEBUG = False # turn off the debug mode
    # SQLALCHEMY_DATABASE_URI = config('DATABASE_URL') # use the DATABASE_URL from heroku
    # SQLALCHEMY_TRACK_MODIFICATIONS = False # turn off the modification tracker
    # SQLALCHEMY_ECHO = False # turn off the echo
    pass

class TestConfig(Config):
    # TESTING = True
    # SQLALCHEMY_DATABASE_URI = 'sqlite://' # use in-memory sqlite database
    # SQLALCHEMY_TRACK_MODIFICATIONS = False
    # SQLALCHEMY_ECHO = True
    pass
    
config_dict = {
    'dev': DevConfig,
    'prod': ProdConfig,
    'test': TestConfig
}