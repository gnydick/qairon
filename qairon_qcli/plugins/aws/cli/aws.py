from ..controllers import AwsServiceController

aws = AwsServiceController()

COMMANDS = dict(
    register_secret=[
        {'deployment_id': {'dotters': {'completer': 'deployment_completer'}}},
        'secret_id',
        'secret_name',
        'secret_value',
        {'-k': {'args': {'dest': 'kms_key_alias'}}}
    ],
    update_secret=[
        {'deployment_id': {'dotters': {'completer': 'deployment_completer'}}},
        'secret_name',
        'secret_value',
        {'-k': {'args': {'dest': 'kms_key_alias'}}}
    ],
    get_secret_string=[
        {'deployment_id': {'dotters': {'completer': 'deployment_completer'}}},
        'secret_name'

    ]
)


def register_secret(deployment_id, secret_id, secret_name, secret_value, secret_tag="default", kms_key_alias=None, command=None,
                    resource=None, **kwargs):
    result = aws.register_secret(deployment_id, secret_id, secret_name, secret_value, secret_tag=secret_tag,
                                 kms_key_alias=kms_key_alias)
    q = kwargs.get('q', False)
    if q is False:
        print(result)


def update_secret(deployment_id, secret_name, secret_value, secret_tag="default", kms_key_alias=None,
                  resource=None, **kwargs):
    """
    Creates a new secret. The secret value can be a string or bytes.
    """
    result = aws.update_secret(deployment_id, secret_name, secret_value, secret_tag, kms_key_alias=kms_key_alias)
    q = kwargs.get('q', False)
    if q is False:
        print(result)


def get_secret_string(resource, command, deployment_id, secret_name, **kwargs):
    result = aws.get_secret_string_for_deployment(deployment_id, secret_name)
    if result is not None:
        q = kwargs.get('q', False)
        if q is False:
            print(result['SecretString'])
    else:
        print(result)
        exit(255)
