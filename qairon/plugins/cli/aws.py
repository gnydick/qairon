import importlib
import os

import boto3
from boto3 import session
from botocore.docs import paginator
from botocore.exceptions import ClientError
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
        'secret_name'
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


def get_secret_string(resource, command, secret_name=None, q=False):
    result = aws.get_secret_string(secret_name)
    if result[0]:
        if not q:
            print(result[0]['SecretString'])
    else:
        print(result[1])
        exit(255)
