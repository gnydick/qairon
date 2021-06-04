import importlib
import os

import boto3
from boto3 import session
from botocore.exceptions import ClientError


class AwsController:

    @staticmethod
    def create_secret(secret_name, secret_value, kms_key_alias=None, deployment_id=None, q=False):
        """
        Creates a new secret. The secret value can be a string or bytes.
        """
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

        # create a new config object and attach it to the deployment
        if deployment_id:
            pass

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
