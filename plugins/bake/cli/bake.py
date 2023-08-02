from plugins.bake.controller import BakingBuilder

COMMANDS = dict(
    files=[
        {'deployment_id': {'dotters': {'completer': 'deployment_completer'}}},
        {'build_id': {'dotters': {'completer': 'build_completer'}}},
        'release_job_number'
    ]
)


def files(deployment_id, build_id, release_job_number, resource=None, command=None, q=False):
    baking_builder = BakingBuilder(deployment_id, build_id, release_job_number)
    bake = baking_builder.build()
    result = bake.bake()
    if not q:
        if result is not None:
            print(result)
