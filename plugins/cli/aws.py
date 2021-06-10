import importlib
import os

from plugins.controller.aws import AwsController
aws = AwsController()

COMMANDS = dict(
    create_secret=[
        'secret_name',
        'secret_value',
        {'deployment_id': {'dotters': {'completer': 'deployment_completer'}}},
        {'-k': {'args': {'dest': 'kms_key_alias'}}}
    ],
    get_secret_string=[
        'secret_name',
        {'deployment_id': {'dotters': {'completer': 'deployment_completer'}}}
    ]
)


def create_secret(secret_name=None, secret_value=None, kms_key_alias=None,
                  deployment_id=None, resource=None, command=None, q=False):
    """
    Creates a new secret. The secret value can be a string or bytes.
    """
    result = aws.create_secret(secret_name, secret_value, kms_key_alias=kms_key_alias, deployment_id=deployment_id)
    if not q:
        print(result)


def get_secret_string(resource, command, secret_name, deployment_id, q=False):


    result = aws.get_secret_string_for_deployment(secret_name, deployment_id)
    if result[0]:
        if not q:
            print(result[0]['SecretString'])
    else:
        print(result[1])
        exit(255)
