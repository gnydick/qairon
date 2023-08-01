from qcli_plugins.baker.controller import BakerBuilder

COMMANDS = dict(
    bake=[
        {'deployment_id': {'dotters': {'completer': 'deployment_completer'}}},
        {'build_id': {'dotters': {'completer': 'build_completer'}}},
        'release_job_number'
    ],

    files=[
        {'deployment_id': {'dotters': {'completer': 'deployment_completer'}}},
        {'build_id': {'dotters': {'completer': 'build_completer'}}},
        'release_job_number'
    ]
)


def bake(deployment_id, build_id, release_job_number, resource=None, command=None, q=False):
    baker_builder = BakerBuilder(deployment_id, build_id, release_job_number)
    baker = baker_builder.build()
    result = baker.bake()
    if not q:
        if result is not None:
            print(result)


def files(deployment_id, build_id, release_job_number, resource=None, command=None, q=False):
    baker_builder = BakerBuilder(deployment_id, build_id, release_job_number)
    baker = baker_builder.files()
    result = baker.bake()
    if not q:
        if result is not None:
            print(result)
