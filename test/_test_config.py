import os

from dotenv import load_dotenv
from config import Config

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))
test_data_path = os.path.join(basedir, "test_data")

class TestConfig(Config):
    Config.TESTING = True
    Config.DEBUG = True
    Config.SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:postgres@postgres:15432/test'