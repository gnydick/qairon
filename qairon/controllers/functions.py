import json
import sys


def error_exit(error_code, message):
    sys.stderr.write(message)
    sys.exit(error_code)


def confirm_stack_operation(stack_id):
    response = input("prompt")
    return response == stack_id


def __parse_deployment__(deployment_id):
    if type(deployment_id) == str:
        deployment = json.loads(deployment_id)
    else:
        deployment = deployment_id
    (deployment_target, env, app, stack, service, tag) = deployment['id'].split(sep=':')
    version = deployment['version']
    from pathlib import Path

    rancher_compose_file = "../../apps/%s/stacks/%s/%s/rancher-compose.yml" % (app, stack, service)

    my_file = Path(rancher_compose_file)
    if not my_file.is_file():
        rancher_compose_file = '../../apps/%s/stacks/%s/%s/rancher-compose.yml' % (stack, stack, service)

    docker_compose_file = "../../apps/%s/stacks/%s/%s/docker-compose.yml" % (app, stack, service)

    my_file = Path(docker_compose_file)
    if not my_file.is_file():
        docker_compose_file = '../../apps/%s/stacks/%s/%s/docker-compose.yml' % (stack, stack, service)

    config = {
        'deployment_target': deployment_target,
        'env_id': env,
        'app_id': app,
        'stack_name': stack,
        'service_name': service,
        'tag': tag,
        'stack_id': "%s:%s" % (app, stack),
        'service_id': "%s:%s:%s" % (app, stack, service),
        'rancher_service': "%s/%s" % (stack, service),
        'docker_compose_file': docker_compose_file,
        'rancher_compose_file': rancher_compose_file,
        'rancher_catalog_file': "../../apps/%s/stacks/%s/%s/rancher-catalog" % (app, stack, service),
        'env_file': 'qairon.conf',
        'version': version
    }
    return config


def __call_command__(command_line, config, envs, dry=False):
    from subprocess import call
    from os import environ
    command = command_line.split()

    if dry:
        return command_line
    else:
        envvars = environ.copy()

        for k, v in envs.items():
            envvars[k] = v
        call(command, env=envvars)


def clean_command_line(command_line):
    import re
    command_line = re.sub(' +', ' ', command_line)
    command_line = re.sub(' $', '', command_line)
    command_line = re.sub('^ ', '', command_line)
    return command_line
