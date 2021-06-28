import json

from boto3 import session

from qairon.controllers import RestController

rest = RestController()


def __update_secret__(secret_id, secret_value, secret_tag, kms_key_alias):
    """
    update a secret for a deployment
    """


    boto_sess = session.Session()
    secrets_client = boto_sess.client("secretsmanager")
    kwargs = {"SecretId": secret_id}

    if isinstance(secret_value, str):
        kwargs["SecretString"] = secret_value
    elif isinstance(secret_value, bytes):
        kwargs["SecretBinary"] = secret_value

    if kms_key_alias is not None:
        kwargs["KmsKeyId"] = kms_key_alias

    response = secrets_client.update_secret(**kwargs)
    # create a new config object and attach it to the deployment for
    # the short-name:long-name mapping
    return response


def __fqsn__(deployment_id, secret_name):
    fqsn = format("%s.%s" % (secret_name, str(deployment_id).replace(':', '-')))


def __get_secret_id__(deployment_id, secret_name) -> object:
    config_templs = rest.query("config_template", "config_template_type_id", "eq", "secret_name_map_item")
    possible_configs = rest.get_field("deployment", deployment_id, 'configs')
    configs = [c for c in possible_configs if c['name'] == secret_name and c['config_template_id'] in config_templs[0]]

    if len(configs) != 1:
        exit(255)

    secret_id = json.loads(configs[0]['config'])[secret_name]
    return secret_id


class AwsController:

    @staticmethod
    def register_secret(deployment_id, secret_id, secret_name, secret_value, secret_tag, kms_key_alias=None):
        template = rest.get_instance('config_template', 'secret_name_map_item:1')

        doc = template['doc']
        doc = str(doc).replace("%--key--%", secret_name).replace("%--value--%", secret_id)

        payload = {'resource': 'deployment_config',
                   'config_template_id': 'secret_name_map_item:1',
                   'name': secret_name, 'deployment_id': deployment_id,
                   'config': doc, 'tag': 'default'
                   }

        new_config = rest.create_resource(payload)
        response = __update_secret__(secret_id, secret_value, secret_tag, kms_key_alias=None)

        return json.loads(new_config.content)

    @staticmethod
    def update_secret(deployment_id, secret_name, secret_value, secret_tag, kms_key_alias=None):
        secret_id = __get_secret_id__(deployment_id, secret_name)
        return __update_secret__(secret_id, secret_value, secret_tag, kms_key_alias)

    @staticmethod
    def get_secret_string_for_deployment(deployment_id, secret_name):
        secret_id = __get_secret_id__(deployment_id, secret_name)

        boto_sess = session.Session()
        client = boto_sess.client(
            service_name='secretsmanager'
        )
        get_secret_value_response = client.get_secret_value(SecretId=secret_id)
        return get_secret_value_response
