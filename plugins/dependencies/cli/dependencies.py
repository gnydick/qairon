from plugins.dependencies.controllers import DependencyController

dependencies = DependencyController()

COMMANDS = dict(
    get_related=[
        {'dependency_id': {'dotters': {'completer': 'dependency_completer'}}}
    ],
    add_related=[
        {'dependency_id': {'dotters': {'completer': 'dependency_completer'}}},
        {'related_id': {'dotters': {'completer': 'related_completer'}}}
    ]
)


def add_related(dependency_id, related_id, command=None, resource=None, q=False):
    result = dependencies.add_related(dependency_id, related_id)
    if not q:
        print(result)
