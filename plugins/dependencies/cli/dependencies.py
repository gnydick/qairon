from controllers import PrintingOutputController
from plugins.dependencies.controllers import DependencyController

dependencies = DependencyController()

COMMANDS = dict(
    get_related=[
        {'related_id': {'dotters': {'completer': 'related_completer'}}}
    ],
    add_related=[
        {'dependency_id': {'dotters': {'completer': 'dependency_completer'}}},
        {'related_id': {'dotters': {'completer': 'related_completer'}}}
    ],
    del_related=[
        {'dependency_id': {'dotters': {'completer': 'dependency_completer'}}},
        {'related_id': {'dotters': {'completer': 'related_completer'}}}
    ]
)

oc = PrintingOutputController()
def add_related(dependency_id, related_id, **kwargs):
    result = dependencies.add_related(dependency_id, related_id)
    oc.handle(result, **kwargs)

def del_related(dependency_id, related_id, **kwargs):
    result = dependencies.del_related(dependency_id, related_id)
    oc.handle(result, **kwargs)

def get_related(related_id, **kwargs):
    result = (dependencies.get_related(related_id))
    oc.handle(result, **kwargs)
