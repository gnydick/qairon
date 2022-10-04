import os

from flask import Flask


SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_size': 32,
    'pool_recycle': 4,
    'pool_pre_ping': True,
    'logging_name': 'PoolLog',
    'pool_use_lifo': True,
    'pool_timeout': 2
}
app = Flask(__name__)
app.app_context().push()
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = 'SQLALCHEMY_TRACK_MODIFICATIONS' in os.environ
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = SQLALCHEMY_ENGINE_OPTIONS
app.config['SQLALCHEMY_RECORD_QUERIES'] = 'SQLALCHEMY_RECORD_QUERIES' in os.environ
app.config['SQLALCHEMY_ECHO'] = 'SQLALCHEMY_ECHO' in os.environ

app.config['DEBUG'] = os.getenv('DEBUG', True)