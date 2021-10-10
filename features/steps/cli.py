from behave import *
from behave import then, when


@given('create "{pk}" "{resource}" "{resource_id}" in "{parent_field}" "{parent_id}" via cli')
def step_impl(context, pk, resource, resource_id, parent_field, parent_id):
    context.cli.create({'resource': resource, pk: resource_id, parent_field: parent_id})
    resource_obj = context.rest.get_instance(resource, parent_id + ':' + resource_id)
    assert resource_obj[pk] == resource_id
    assert resource_obj[parent_field] == parent_id


@given('create "{pk}" "{resource}" "{resource_id}" via cli')
def step_impl(context, pk, resource, resource_id):
    context.cli.create({'resource': resource, pk: resource_id})
    resource_obj = context.rest.get_instance(resource, resource_id)
    assert resource_obj[pk] == resource_id


@given('create service_config_template "{svc_config_name}" for "{svc}" via cli')
def step_impl(context, svc_config_name, svc):
    expected_svc_cfg_id = '%s:%s' % (svc, svc_config_name)
    context.cli.create({'resource': 'service_config_template', 'name': svc_config_name, 'service_id': svc})
    svc_cfg = context.rest.get_instance('service_config_template', expected_svc_cfg_id)
    assert svc_cfg['id'] == expected_svc_cfg_id


@given('create environment "{env}" via cli')
def step_impl(context, env):
    expected_env_id = env
    context.cli.create(
        {'resource': 'environment', 'id': env}
    )
    environment = context.rest.get_instance('environment', expected_env_id)
    assert environment['id'] == expected_env_id


@given('create deployment for service "{service_id}" in k8s "{deployment_target}" via cli')
def step_impl(context, service_id, deployment_target):
    expected_dep_id = '%s:%s:default' % (deployment_target, service_id)
    context.cli.create(
        {'resource': 'deployment', 'service_id': service_id, 'deployment_target_id': deployment_target,
         'tag': 'default'})
    deployment = context.rest.get_instance('deployment', expected_dep_id)
    assert deployment['id'] == expected_dep_id


@given('create config "{config_name}" type "{config_type_id}" for deployment "{deployment_id}" tagged "{tag}" via cli')
def step_impl(context, config_name, config_type_id, deployment_id, tag):
    expected_config_id = '%s:%s:%s:%s' % (deployment_id, config_type_id, config_name, tag)
    context.cli.create(
        {'resource': 'config', 'name': config_name, 'config_type_id': config_type_id, 'deployment_id': deployment_id,
         'tag': tag})
    config = context.rest.get_instance('config', expected_config_id)
    assert config['id'] == expected_config_id


@when('get "{resource}" "{resource_id}" via cli')
def step_impl(context, resource, resource_id):
    context.cli.get(**{'resource': resource, 'id': resource_id})


@when('modify "{resource}" "{resource_id}" "{field}" "{value}" via cli')
def step_impl(context, resource, resource_id, field, value):
    context.cli.set_field(**{'resource': resource, 'id': resource_id, 'field': field, 'value': value})


@then('delete "{resource}" "{resource_id}" via cli')
def step_impl(context, resource, resource_id):
    context.cli.delete(**{'resource': resource, 'id': resource_id})
    results = context.rest.get_instance(resource, resource_id)
    assert results == {}


@when('add_to_collection "{item_id}" "{number:d}" to "{items}" on "{owner}" "{owner_id}" via cli')
def step_impl(context, number, item_id, items, owner, owner_id):
    owner_obj = context.rest.get_instance(owner, owner_id)
    assert len(owner_obj[items]) == number - 1
    context.cli.add_to_collection(owner, owner_id, items, item_id)
    owner_obj = context.rest.get_instance(owner, owner_id)
    assert len(owner_obj[items]) == number


@then('del_from_collection "{item_id}" "{number:d}" to "{items}" on "{owner}" "{owner_id}" via cli')
def step_impl(context, number, item_id, items, owner, owner_id):
    owner_obj = context.rest.get_instance(owner, owner_id)
    assert len(owner_obj[items]) == number
    context.cli.del_from_collection(owner, owner_id, items, item_id)
    owner_obj = context.rest.get_instance(owner, owner_id)
    assert len(owner_obj[items]) == number - 1


@then('query something "{resource}" "{field}" "{op}" "{value}"')
def step_impl(context, resource, field, op, value):
    resource_ids = context.cli.query(
        **{'resource': resource, 'search_field': field, 'op': op, 'value': value, 'output_fields': 'id'})
    pass
