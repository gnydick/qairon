from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.pool import QueuePool

from base import app


SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_size': 3,
    'pool_recycle': 120,
    'pool_pre_ping': True
}
db = SQLAlchemy(app, engine_options=SQLALCHEMY_ENGINE_OPTIONS)
