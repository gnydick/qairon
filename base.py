import os

from flask import Flask
from flask_talisman import Talisman

SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_size': 32,
    'pool_recycle': 4,
    'pool_pre_ping': True,
    'logging_name': 'PoolLog',
    'pool_use_lifo': True,
    'pool_timeout': 2
}

app = Flask(__name__)

from flask import request


def change_url():
    base_url = request.base_url
    print("fofofofof")
    if 'X-FORWARDED-PROTO' in request.headers and request.path not in ('/up', '/up/'):
        request.base_url = base_url.replace('http://', 'https://')


app.before_request(change_url)
Talisman(app)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = 'SQLALCHEMY_TRACK_MODIFICATIONS' in os.environ
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = SQLALCHEMY_ENGINE_OPTIONS
app.config['SQLALCHEMY_RECORD_QUERIES'] = 'SQLALCHEMY_RECORD_QUERIES' in os.environ
app.config['SQLALCHEMY_ECHO'] = 'SQLALCHEMY_ECHO' in os.environ
