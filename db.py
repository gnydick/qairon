import importlib
import os
import pkgutil

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.pool import QueuePool

from base import app

db = SQLAlchemy(app)
