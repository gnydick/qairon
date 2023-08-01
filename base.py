import importlib
import os
import pkgutil

from flask import Flask
from flask_talisman import Talisman
from flask import request
import logging

from sqlalchemy import event
logging.basicConfig()
logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)

SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_size': 32,
    'pool_recycle': 4,
    'pool_pre_ping': True,
    'logging_name': 'PoolLog',
    'pool_use_lifo': True,
    'pool_timeout': 2
}

app = Flask(__name__)


def change_url():
    base_url = request.base_url
    if request.headers.get('X-FORWARDED-PROTO', 'http') == 'https' and request.path not in ('/up', '/up/'):
        request.base_url = base_url.replace('http://', 'https://')


app.before_request(change_url)
csp = {
    # 'default-src':  ['\'self\'',
    #       '\'unsafe-inline\''],
    # 'script-src': '\'self\'',
    # 'img-src': '*',
}
talisman = Talisman(
    app,
    content_security_policy=csp,
    content_security_policy_nonce_in=['script-src']
)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = 'SQLALCHEMY_TRACK_MODIFICATIONS' in os.environ
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = SQLALCHEMY_ENGINE_OPTIONS
app.config['SQLALCHEMY_RECORD_QUERIES'] = 'SQLALCHEMY_RECORD_QUERIES' in os.environ
app.config['SQLALCHEMY_ECHO'] = 'SQLALCHEMY_ECHO' in os.environ
app.config['FLASK_ADMIN_SWATCH'] = str(os.getenv('FLASK_ADMIN_SWATCH', default='superhero'))

