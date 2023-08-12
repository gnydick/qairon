from plugins.baker.controllers import BakerBuilder

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


def bake(deployment_id, build_id, release_job_number, resource=None, **kwargs):
    baker_builder = BakerBuilder(deployment_id, build_id, release_job_number)
    baker = baker_builder.build()
    result = baker.bake()
    q = kwargs.get('q', False)
    if q is False:
        if result is not None:
            print(result)


def files(deployment_id, build_id, release_job_number, resource=None, **kwargs):
    baker_builder = BakerBuilder(deployment_id, build_id, release_job_number)
    baker = baker_builder.files()
    result = baker.bake()
    q = kwargs.get('q', False)
    if q is False:
        if result is not None:
            print(result)
