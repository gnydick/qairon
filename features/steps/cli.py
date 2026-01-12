import json

from behave import *


@given('create "{resource}" "{res_id}" via cli')
def step_impl(context, resource, res_id):
    context.cli.create(
        {'id': res_id, 'resource': resource}, output_format='plain', output_fields=['id'])
    output = context.stdout_mock.getvalue().strip()
    context.stdout_mock.seek(0)
    context.stdout_mock.truncate(0)
    assert output == res_id


@then(
    'create build_artifact for "{build_id}" from "{input_repo_id}" uploaded to "{output_repo_id}" named "{name}" in path "{upload_path}" via cli')
def step_impl(context, build_id, input_repo_id, output_repo_id, name, upload_path):
    context.cli.create(
        {'resource': 'build_artifact', 'build_id': build_id, 'input_repo_id': input_repo_id,
         'output_repo_id': output_repo_id, 'name': name, 'upload_path': upload_path},
        output_format='plain', output_fields=['id']
    )
    output = context.stdout_mock.getvalue().strip()
    context.stdout_mock.seek(0)
    context.stdout_mock.truncate(0)
    assert output == ':'.join([build_id, name])


@then(
    'create release_artifact for "{release_id}" from "{input_repo_id}" uploaded to "{output_repo_id}" named "{name}" in path "{upload_path}" via cli')
def step_impl(context, release_id, input_repo_id, output_repo_id, name, upload_path):
    context.cli.create(
        {'resource': 'release_artifact', 'release_id': release_id, 'input_repo_id': input_repo_id,
         'output_repo_id': output_repo_id, 'name': name, 'upload_path': upload_path}, output_format='plain',
        output_fields=['id']
    )
    output = context.stdout_mock.getvalue().strip()
    context.stdout_mock.seek(0)
    context.stdout_mock.truncate(0)
    assert output == ':'.join([release_id, name])


@then(
    'create "{resource}" with parent id "{parent_id}" in parent field "{parent_field}" named "{name}" and "{field1}" equals "{value1}" via cli')
def step_impl(context, resource, parent_id, parent_field, name, field1, value1):
    context.cli.create(
        {'resource': resource, parent_field: parent_id, 'name': name}, output_format='plain', output_fields=['id']
    )
    output = context.stdout_mock.getvalue().strip()
    context.stdout_mock.seek(0)
    context.stdout_mock.truncate(0)
    assert output == ':'.join([parent_id, name])


@then('create "{resource}" with parent id "{parent_id}" in parent field "{parent_field}" named "{name}" via cli')
def step_impl(context, resource, parent_id, parent_field, name):
    context.cli.create(
        {'resource': resource, parent_field: parent_id, 'name': name}, output_format='plain', output_fields=['id']
    )
    output = context.stdout_mock.getvalue().strip()
    context.stdout_mock.seek(0)
    context.stdout_mock.truncate(0)
    assert output == ':'.join([parent_id, name])


@then(
    'create provider in env "{environment_id}" of type "{provider_type_id}" with native_id "{native_id}" via cli')
def step_impl(context, environment_id, provider_type_id, native_id):
    context.cli.create(
        {'environment_id': environment_id, 'provider_type_id': provider_type_id, 'resource': 'provider',
         'native_id': native_id}, output_format='plain', output_fields=['id']
    )
    output = context.stdout_mock.getvalue().strip()
    context.stdout_mock.seek(0)
    context.stdout_mock.truncate(0)
    assert output == ':'.join([environment_id, provider_type_id, native_id])


@then(
    'allocate subnet "{network_id}" from vpc_cidr "{cidr}" with "{additional_mask_bits}" additional bits named "{subnet_name}" via cli')
def step_impl(context, network_id, cidr, additional_mask_bits, subnet_name):
    context.cli.allocate_subnet(network_id, additional_mask_bits, subnet_name)
    output = context.stdout_mock.getvalue().strip()
    context.stdout_mock.seek(0)
    context.stdout_mock.truncate(0)
    subnet = json.loads(output)
    net_base = cidr.split(sep='/')
    assert subnet['id'] == '%s:%s' % (network_id, subnet_name)
    assert subnet['cidr'] == "%s/%d" % (net_base[0], int(net_base[1]) + int(additional_mask_bits))


@then('create "{field}" "{field_val}" "{resource}" "{res_name}" under "{parent_fk_field}" "{parent_id}" via cli')
def step_impl(context, field, field_val, resource, res_name, parent_fk_field, parent_id):
    context.cli.create(
        {'name': res_name, parent_fk_field: parent_id, 'resource': resource, field: field_val}, output_format='plain',
        output_fields=['id']
    )
    output = context.stdout_mock.getvalue().strip()
    context.stdout_mock.seek(0)
    context.stdout_mock.truncate(0)
    assert output == '%s:%s' % (parent_id, res_name)


@then('create "{resource}" "{res_name}" under "{parent_fk_field}" "{parent_id}" via cli')
def step_impl(context, resource, res_name, parent_fk_field, parent_id):
    context.cli.create(
        {'name': res_name, parent_fk_field: parent_id, 'resource': resource}, output_format='plain',
        output_fields=['id']
    )
    output = context.stdout_mock.getvalue().strip()
    context.stdout_mock.seek(0)
    context.stdout_mock.truncate(0)
    assert output == '%s:%s' % (parent_id, res_name)


@then(
    'create textresource "{resource}" "{res_name}" under "{parent_fk_field}" "{parent_id}" with doc "{doc}" via cli')
def step_impl(context, resource, res_name, parent_fk_field, parent_id, doc):
    context.cli.create(
        {'id': res_name, parent_fk_field: parent_id, 'resource': resource, 'doc': doc}, output_format='plain',
        output_fields=['id']
    )
    output = context.stdout_mock.getvalue().strip()
    context.stdout_mock.seek(0)
    context.stdout_mock.truncate(0)
    assert output == res_name


# use_step_matcher("re")
@given('provider "{provider}" can be created via cli')
def step_impl(context, provider):
    context.cli.create(
        {'id': provider, 'resource': 'provider'}, output_format='plain', output_fields=['id'])
    output = context.stdout_mock.getvalue().strip()
    context.stdout_mock.seek(0)
    context.stdout_mock.truncate(0)
    assert output == provider


@given('region "{region}" can be created for provider "{provider}" via cli')
def step_impl(context, region, provider):
    context.cli.create(
        {'name': region, 'provider_id': provider, 'resource': 'region'}, output_format='plain', output_fields=['id'])
    output = context.stdout_mock.getvalue().strip()
    context.stdout_mock.seek(0)
    context.stdout_mock.truncate(0)
    assert output == '%s:%s' % (provider, region)


@given('zone "{zone}" can be created for region "{region}" via cli')
def step_impl(context, zone, region):
    context.cli.create(
        {'name': zone, 'region_id': region, 'resource': 'zone', 'defaults': '{}'}, output_format='plain',
        output_fields=['id'])
    output = context.stdout_mock.getvalue().strip()
    context.stdout_mock.seek(0)
    context.stdout_mock.truncate(0)
    assert output == '%s:%s' % (region, zone)


@when('delete "{resource}" "{res_id}" via cli')
@then('delete "{resource}" "{res_id}" via cli')
def step_impl(context, resource, res_id):
    context.cli.delete(resource, res_id)
    output = json.loads(context.stdout_mock.getvalue().strip())
    context.stdout_mock.seek(0)
    context.stdout_mock.truncate(0)
    assert output['id'] == res_id
    assert output['status'] == 204
    assert output['resource'] == resource


@given('application "{app_id}" can be created via cli')
def step_impl(context, app_id):
    context.cli.create(
        {'id': app_id, 'resource': 'application', 'defaults': '{}'}, output_format='plain', output_fields=['id'])
    output = context.stdout_mock.getvalue().strip()
    context.stdout_mock.seek(0)
    context.stdout_mock.truncate(0)
    assert output == app_id


@given('stack "{stack}" can be created for app "{app_id}" via cli')
def step_impl(context, stack, app_id):
    context.cli.create(
        {'name': stack, 'application_id': app_id, 'resource': 'stack', 'defaults': '{}'}, output_format='plain',
        output_fields=['id'])
    output = context.stdout_mock.getvalue().strip()
    context.stdout_mock.seek(0)
    context.stdout_mock.truncate(0)
    assert output == '%s:%s' % (app_id, stack)


@given('service "{service}" can be created for stack "{stack}" via cli')
def step_impl(context, service, stack):
    context.cli.create(
        {'name': service, 'stack_id': stack, 'resource': 'service', 'defaults': '{}'}, output_format='plain',
        output_fields=['id'])
    output = context.stdout_mock.getvalue().strip()
    context.stdout_mock.seek(0)
    context.stdout_mock.truncate(0)
    assert output == '%s:%s' % (stack, service)


@given('environment "{environment}" can be created at "{deployment_url}" via cli')
def step_impl(context, environment, deployment_url, role):
    context.cli.create(
        {'resource': 'environment', 'id': environment, 'deployment_url': deployment_url, 'defaults': '{}'},
        output_format='plain', output_fields=['id']
    )
    output = context.stdout_mock.getvalue().strip()
    context.stdout_mock.seek(0)
    context.stdout_mock.truncate(0)
    assert output == environment


@given('create deployment_target "{name}" of type "{dep_target_type}" in "{partition_id}" via cli')
def step_impl(context, name, dep_target_type, partition_id):
    context.cli.create(
        {'resource': 'deployment_target', 'deployment_target_type_id': dep_target_type,
         'partition_id': partition_id, 'name': name}, output_format='plain', output_fields=['id']
    )
    output = context.stdout_mock.getvalue().strip()
    context.stdout_mock.seek(0)
    context.stdout_mock.truncate(0)
    assert output == '%s:%s:%s' % (partition_id, dep_target_type, name)


@then('create build for "{service_id}" from job "{job_number}" tagged "{tag}" via cli')
def step_impl(context, service_id, job_number, tag):
    context.cli.create(
        {'resource': 'build', 'service_id': service_id, 'build_num': job_number, 'vcs_ref': tag},
        output_format='plain', output_fields=['id'])
    output = context.stdout_mock.getvalue().strip()
    context.stdout_mock.seek(0)
    context.stdout_mock.truncate(0)
    assert output == '%s:%s' % (service_id, job_number)


@then('create release for "{deployment_id}" from build "{build_id}" from job "{build_num}" via cli')
def step_impl(context, deployment_id, build_id, build_num):
    context.cli.create(
        {'resource': 'release', 'deployment_id': deployment_id, 'build_id': build_id, 'build_num': build_num},
        output_format='plain', output_fields=['id'])
    output = context.stdout_mock.getvalue().strip()
    context.stdout_mock.seek(0)
    context.stdout_mock.truncate(0)
    assert output == '%s:%s' % (deployment_id, build_num)


@then(
    'create deployment at "{dep_target_id}" for "{service}" tagged "{tag}" with defaults "{defaults}" via cli')
def step_impl(context, dep_target_id, service, tag, defaults):
    context.cli.create(
        {'resource': 'deployment', 'deployment_target_id': dep_target_id, 'service_id': service,
         'tag': tag, 'defaults': defaults}, output_format='plain', output_fields=['id']
    )
    output = context.stdout_mock.getvalue().strip()
    context.stdout_mock.seek(0)
    context.stdout_mock.truncate(0)
    assert output == '%s:%s:%s' % (dep_target_id, service, tag)
    context.cli.get('deployment', output)
    new_dep = json.loads(context.stdout_mock.getvalue().strip())
    context.stdout_mock.seek(0)
    context.stdout_mock.truncate(0)
    assert new_dep['defaults'] == defaults
    assert new_dep['tag'] == tag


@then(
    'create config for resource "{resource}" named "{name}" from template "{config_template_id}" can be created for "{resource_id}" tagged "{tag}" via cli')
@given(
    'create config for resource "{resource}" named "{name}" from template "{config_template_id}" can be created for "{resource_id}" tagged "{tag}" via cli')
def step_impl(context, resource, name, config_template_id, resource_id, tag):
    payload = {'resource': "%s_config" % resource, 'name': name, 'config_template_id': config_template_id,
               '%s_id' % resource: resource_id, 'tag': tag}
    context.cli.create(payload, output_format='plain', output_fields=['id'])
    output = context.stdout_mock.getvalue().strip()
    context.stdout_mock.seek(0)
    context.stdout_mock.truncate(0)
    assert output == '%s:%s:%s:%s' % (resource_id, config_template_id, name, tag)


@given('update "{field}" for "{resource}" "{resource_id}" to "{value}" via cli')
def step_impl(context, resource, resource_id, field, value):
    context.cli.update_resource(resource, resource_id, field, value)


@given('create environment "{env}" for "{role_id}" via cli')
def step_impl(context, env, role_id):
    expected_env_id = '%s:%s' % (role_id, env)
    context.cli.create(
        {'resource': 'environment', 'role_id': role_id, 'name': env}, output_format='plain', output_fields=['id']
    )
    context.stdout_mock.seek(0)
    context.stdout_mock.truncate(0)
    context.cli.get('environment', expected_env_id)
    environment = json.loads(context.stdout_mock.getvalue().strip())
    context.stdout_mock.seek(0)
    context.stdout_mock.truncate(0)
    assert environment['id'] == expected_env_id


@step('create k8s_cluster "{name}" in "{environment}" via cli')
def step_impl(context, name, environment):
    expected_cluster_id = '%s:%s:k8s' % (environment, name)
    context.cli.create(
        {'resource': 'k8s_cluster', 'environment_id': environment, 'name': name}, output_format='plain',
        output_fields=['id']
    )
    context.stdout_mock.seek(0)
    context.stdout_mock.truncate(0)
    context.cli.get('k8s_cluster', expected_cluster_id)
    k8s_cluster = json.loads(context.stdout_mock.getvalue().strip())
    context.stdout_mock.seek(0)
    context.stdout_mock.truncate(0)
    assert k8s_cluster['id'] == expected_cluster_id


@step('environment "{id}" can be created via cli')
def step_impl(context, id):
    context.cli.create(
        {'id': id, 'resource': 'environment'}, output_format='plain', output_fields=['id'])
    output = context.stdout_mock.getvalue().strip()
    context.stdout_mock.seek(0)
    context.stdout_mock.truncate(0)
    assert output == id


@given('create dependency_case called "{idee}" with "{relatable_type}" related to "{related_type}" "{cardinality}"')
def step_impl(context, idee, relatable_type, related_type, cardinality):
    resource_dict = {'resource': 'dependency_case', 'id': idee, 'relatable_type': relatable_type,
                     'related_type': related_type, 'allowed_relationship': cardinality}
    context.cli.create(resource_dict)
    output_obj = json.loads(context.stdout_mock.getvalue().strip())
    context.stdout_mock.seek(0)
    context.stdout_mock.truncate(0)
    output_obj['resource'] = 'dependency_case'
    assert output_obj == resource_dict


@then('create "{resource}" with "{field1}" equals "{value1}" and "{field2}" equals "{value2}" named "{name}" via cli')
def step_impl(context, resource, field1, value1, field2, value2, name):
    resource_dict = {'resource': resource, field1: value1, field2: value2, 'name': name}
    context.cli.create(resource_dict)
    output_obj = json.loads(context.stdout_mock.getvalue().strip())
    context.stdout_mock.seek(0)
    context.stdout_mock.truncate(0)
    output_obj['resource'] = resource
    resource_dict['id'] = ':'.join([value1, value2, name])
    assert output_obj == resource_dict

@then('create failed "{resource}" with "{field1}" equals "{value1}" and "{field2}" equals "{value2}" and "{field3}" equals "{value3} via cli')
def step_impl(context, resource, field1, value1, field2, value2, field3, value3):
    resource_dict = {'resource': resource, field1: value1, field2: value2, field3: value3}
    context.cli.create(resource_dict)
    output_obj = json.loads(context.stdout_mock.getvalue().strip())
    context.stdout_mock.seek(0)
    context.stdout_mock.truncate(0)
    output_obj['resource'] = resource
    resource_dict['id'] = ':'.join([value1, value2, value3])
    assert output_obj == resource_dict

@then('create "{resource}" with "{field1}" equals "{value1}" and "{field2}" equals "{value2}" and "{field3}" equals "{value3}" via cli')
def step_impl(context, resource, field1, value1, field2, value2, field3, value3):
    resource_dict = {'resource': resource, field1: value1, field2: value2, field3: value3}
    context.cli.create(resource_dict)
    output_obj = json.loads(context.stdout_mock.getvalue().strip())
    context.stdout_mock.seek(0)
    context.stdout_mock.truncate(0)
    output_obj['resource'] = resource
    resource_dict['id'] = ':'.join([value1, value2, value3])
    assert output_obj == resource_dict


@then('create "{resource}" with "{field1}" equals "{value1}" and "{field2}" equals "{value2}" via cli')
def step_impl(context, resource, field1, value1, field2, value2):
    resource_dict = {'resource': resource, field1: value1, field2: value2}
    context.cli.create(resource_dict)
    output_obj = json.loads(context.stdout_mock.getvalue().strip())
    context.stdout_mock.seek(0)
    context.stdout_mock.truncate(0)
    output_obj['resource'] = resource
    resource_dict['id'] = ':'.join([value1, value2])
    assert output_obj == resource_dict
