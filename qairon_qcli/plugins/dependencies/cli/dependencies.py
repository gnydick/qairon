
from plugins.dependencies.controllers import DependencyController
from qairon_qcli.controllers import PrintingOutputController

COMMANDS = dict(
    get_related=[
        {'dependency_id': {'dotters': {'completer': 'dependency_completer'}}},
        {'-o': {'args': {'dest': 'output_format'}}},
        {'-f': {'args': {'dest': 'output_fields', 'action': 'append'}}}
    ]

)


def get_related(dependency_id, **kwargs):
    oc = PrintingOutputController()
    dep_con = DependencyController()
    rows = dep_con.get_related(dependency_id)
    oc.handle(rows, **kwargs)
