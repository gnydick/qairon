from plugins.controller import BakerBuilder

baker_builder = BakerBuilder()

COMMANDS = dict(
    bake=[
        {'deployment_id': {'dotters': {'completer': 'deployment_completer'}}},
        {'build_id': {'dotters': {'completer': 'build_completer'}}},
        'release_job_number'
    ]
)


def bake(deployment_id, build_id, release_job_number, resource=None, command=None, q=False):
    baker = baker_builder.build(deployment_id, build_id, release_job_number)
    result = baker.bake()
    if not q:
        if result is not None:
            print(result)
