import importlib
import os

import boto3
from boto3 import session
from botocore.exceptions import ClientError

from controllers import RestController

rest = RestController()


class AwsController:

    @staticmethod
    def __creat_if_not_exists_config_type__(config_type):
        results = rest.query('config_template_type', 'id', 'eq', config_type, 'id')
        if len(results) == 0:
            new_config_template_type = rest.create_resource({'id': config_type, 'resource': 'config_template_type'})
            print(new_config_template_type)
        print(results)

    @staticmethod
    def create_secret(secret_name, secret_value, kms_key_alias=None, deployment_id=None):
        """
        Creates a new secret. The secret value can be a string or bytes.
        """
        import pydevd_pycharm
        pydevd_pycharm.settrace('localhost', port=54321, stdoutToServer=True, stderrToServer=True)

        boto_sess = session.Session()
        secrets_client = boto_sess.client("secretsmanager")
        kwargs = {"Name": secret_name}

        if isinstance(secret_value, str):
            kwargs["SecretString"] = secret_value
        elif isinstance(secret_value, bytes):
            kwargs["SecretBinary"] = secret_value

        if kms_key_alias is not None:
            kwargs["KmsKeyId"] = kms_key_alias

        response = secrets_client.create_secret(**kwargs)
        # create a new config object and attach it to the deployment for
        # the short-name:long-name mapping
        if deployment_id:
            template = rest.get_instance('config_template', 'secret_name_map_item:1')

            doc = template['doc']
            doc = str(doc).replace("%--key--%", secret_name).replace("%--value--%", response['ARN'])

            payload = {'resource': 'deployment_config',
                       'config_template_id': 'secret_name_map_item:1',
                       'name': secret_name, 'deployment_id': deployment_id,
                       'config': doc, 'tag': 'default'
                       }

            new_config = rest.create_resource(payload)

        return response

    @staticmethod
    def get_secret_string(secret_name):
        boto_sess = session.Session()
        client = boto_sess.client(
            service_name='secretsmanager'
        )

        try:
            secrets_list = client.list_secrets(
                Filters=[
                    {
                        'Key': 'name',
                        'Values': [
                            secret_name
                        ]
                    }
                ]
            )

            if 'SecretList' in secrets_list:
                if len(secrets_list['SecretList']) == 1:
                    response = secrets_list['SecretList'][0]
                    id = response['ARN']
                    get_secret_value_response = client.get_secret_value(SecretId=id)
                    return [get_secret_value_response, None]
                else:
                    return [None, "Too many results!"]
            else:
                return [None, "Not found!"]
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                print("The requested secret " + secret_name + " was not found")
            elif e.response['Error']['Code'] == 'InvalidRequestException':
                print("The request was invalid due to:", e)
            elif e.response['Error']['Code'] == 'InvalidParameterException':
                print("The request had invalid params:", e)
            elif e.response['Error']['Code'] == 'DecryptionFailure':
                print("The requested secret can't be decrypted using the provided KMS key:", e)
            elif e.response['Error']['Code'] == 'InternalServiceError':
                print("An error occurred on service side:", e)
