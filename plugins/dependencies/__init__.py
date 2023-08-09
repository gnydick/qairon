import importlib

from plugins.dependencies.cli import *
from plugins.dependencies.controllers import QaironSchema
from plugins.dependencies.views import *


def import_models(plugin_package):
    models_module = importlib.import_module(".".join([plugin_package.__name__, "models"]))
    return models_module
