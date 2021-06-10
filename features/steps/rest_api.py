from behave import *


@given('create "{resource}" "{res_id}" via rest')
def step_impl(context, resource, res_id):
    res = context.rest.create_resource(
        {'id': res_id, 'resource': resource})
    data = res.json()
    assert data['id'] == res_id


@then('create provider of type "{provider_type_id}" with native_id "{native_id}" named "{name}" via rest')
def step_impl(context, provider_type_id, native_id, name):
    res = context.rest.create_resource(
        {'provider_type_id': provider_type_id, 'resource': 'provider',
         'name': name, 'native_id': native_id}
    )
    data = res.json()
    assert data['id'] == '%s:%s' % (provider_type_id, native_id)


@then('create "{resource}" "{res_name}" under "{parent_fk_field}" "{parent_id}" via rest')
def step_impl(context, resource, res_name, parent_fk_field, parent_id):
    res = context.rest.create_resource(
        {'name': res_name, parent_fk_field: parent_id, 'resource': resource}
    )
    data = res.json()
    assert data['id'] == '%s:%s' % (parent_id, res_name)


@then(
    'create versioned "{resource}" "{res_name}" version "{version}" under "{parent_fk_field}" "{parent_id}" doc "{doc}" via rest')
def step_impl(context, resource, res_name, version, parent_fk_field, parent_id, doc):
    res = context.rest.create_resource(
        {'name': res_name, parent_fk_field: parent_id, 'resource': resource, 'version': version, 'doc': doc}
    )
    data = res.json()
    assert data['id'] == '%s:%s' % (parent_id, version)


# use_step_matcher("re")
@given('provider "{provider}" can be created via rest')
def step_impl(context, provider):
    prov = context.rest.create_resource(
        {'id': provider, 'resource': 'provider'})
    data = prov.json()
    assert data['id'] == provider


@given('region "{region}" can be created for provider "{provider}" via rest')
def step_impl(context, region, provider):
    new_region = context.rest.create_resource(
        {'name': region, 'provider_id': provider, 'resource': 'region'})
    data = new_region.json()
    assert data['id'] == '%s:%s' % (provider, region)


@given('zone "{zone}" can be created for region "{region}" via rest')
def step_impl(context, zone, region):
    new_zone = context.rest.create_resource(
        {'name': zone, 'region_id': region, 'resource': 'zone', 'defaults': '{}'})
    data = new_zone.json()
    assert data['id'] == '%s:%s' % (region, zone)


@when('delete "{resource}" "{res_id}" via rest')
@then('delete "{resource}" "{res_id}" via rest')
def step_impl(context, resource, res_id):
    response = context.rest.delete_resource(resource, res_id)
    assert response.status_code == 204


@given('application "{app_id}" can be created via rest')
def step_impl(context, app_id):
    new_app = context.rest.create_resource(
        {'id': app_id, 'resource': 'application', 'defaults': '{}'})
    data = new_app.json()
    assert data['id'] == app_id


@given('stack "{stack}" can be created for app "{app_id}" via rest')
def step_impl(context, stack, app_id):
    new_stack = context.rest.create_resource(
        {'name': stack, 'application_id': app_id, 'resource': 'stack', 'defaults': '{}'})
    data = new_stack.json()
    assert data['id'] == '%s:%s' % (app_id, stack)


@given('service "{service}" can be created for stack "{stack}" via rest')
def step_impl(context, service, stack):
    new_service = context.rest.create_resource(
        {'name': service, 'stack_id': stack, 'resource': 'service', 'defaults': '{}'})
    data = new_service.json()
    assert data['id'] == '%s:%s' % (stack, service)


@given('environment "{environment}" can be created at "{deployment_url}" via rest')
def step_impl(context, environment, deployment_url, role):
    new_env = context.rest.create_resource(
        {'resource': 'environment', 'id': environment, 'deployment_url': deployment_url, 'defaults': '{}'}
    )
    data = new_env.json()
    assert data['id'] == environment


@given('create deployment_target "{name}" of type "{dep_target_type}" for "{environment}" in "{partition_id}" via rest')
def step_impl(context, name, dep_target_type, environment, partition_id):
    response = context.rest.create_resource(
        {'resource': 'deployment_target', 'deployment_target_type_id': dep_target_type, 'environment_id': environment,
         'partition_id': partition_id, 'name': name}
    )
    data = response.json()
    print(data)


@given('create build for "{service_id}" from job "{job_number}" tagged "{tag}" via rest')
def step_impl(context, service_id, job_number, tag):
    response = context.rest.create_resource(
        {'resource': 'build', 'service_id': service_id, 'build_num': job_number, 'git_tag': tag})
    data = response.json()
    assert data['id'] == '%s:%s' % (service_id, job_number)

@given(
    'create deployment at "{dep_target_id}" for "{service}" tagged "{tag}" with defaults "{defaults}" at version "{version}" via rest')
def step_impl(context, dep_target_id, service, tag, defaults, version):
    response = context.rest.create_resource(
        {'resource': 'deployment', 'deployment_target_id': dep_target_id, 'service_id': service,
         'tag': tag, 'defaults': defaults, 'version': version}
    )
    data = response.json()
    assert data['id'] == '%s:%s:%s' % (dep_target_id, service, tag)
    new_dep = context.rest.get_instance('deployment', data['id'])
    assert new_dep['defaults'] == defaults
    assert new_dep['tag'] == tag



@then(
    'service_config_template "{service_config_template}" can be created for service "{service}" of type "{config_template_type_id}" via rest')
def step_impl(context, service_config_template, service, config_template_type_id):
    response = context.rest.create_resource(
        {'resource': 'service_config_template', 'name': service_config_template, 'service_id': service, 'template': '',
         'config_template_type_id': config_template_type_id}
    )
    new_svc_config = response.json()
    assert new_svc_config['id'] == '%s:%s' % (service, service_config_template)


@when('add first "{plural_resource}" "{item_id}" on "{dest_resource}" "{dest_id}" via rest')
def step_impl(context, plural_resource, item_id, dest_resource, dest_id):
    response = context.rest.add_to_many_to_many(dest_resource, dest_id, plural_resource, item_id)
    new_plural = response.json()[plural_resource]
    assert item_id in [x['id'] for x in new_plural]
    assert len(new_plural) == 1


@when('add second "{plural_resource}" "{item_id}" on "{dest_resource}" "{dest_id}" via rest')
def step_impl(context, plural_resource, item_id, dest_resource, dest_id):
    response = context.rest.add_to_many_to_many(dest_resource, dest_id, plural_resource, item_id)
    new_plural = response.json()[plural_resource]
    assert item_id in [x['id'] for x in new_plural]
    assert len(new_plural) == 2


@then('remove first "{plural_resource}" "{item_id}" on "{dest_resource}" "{dest_id}" via rest')
def step_impl(context, plural_resource, item_id, dest_resource, dest_id):
    response = context.rest.del_from_many_to_many(dest_resource, dest_id, plural_resource, item_id)
    new_plural = response.json()[plural_resource]
    assert item_id not in [x['id'] for x in new_plural]
    assert len(new_plural) == 0


@then('remove second "{plural_resource}" "{item_id}" on "{dest_resource}" "{dest_id}" via rest')
def step_impl(context, plural_resource, item_id, dest_resource, dest_id):
    response = context.rest.del_from_many_to_many(dest_resource, dest_id, plural_resource, item_id)
    new_plural = response.json()[plural_resource]
    assert item_id not in [x['id'] for x in new_plural]
    assert len(new_plural) == 1


@given('config_template_type "{config_template_type}" can be created via rest')
def step_impl(context, config_template_type):
    cfgtype = context.rest.create_resource(
        {'id': config_template_type, 'resource': 'config_template_type'})
    data = cfgtype.json()
    assert data['id'] == config_template_type


@then(
    'create config for resource "{resource}" named "{name}" from template version "{config_template}" can be created for "{resource_id}" tagged "{tag}" via rest')
@given(
    'create config for resource "{resource}" named "{name}" from template version "{config_template}" can be created for "{resource_id}" tagged "{tag}" via rest')
def step_impl(context, resource, name, config_template, resource_id, tag):
    cfg = context.rest.create_resource(
        {'resource': "%s_config" % resource, 'name': name, 'config_template_id': config_template,
         '%s_id' % resource: resource_id, 'tag': tag})
    data = cfg.json()
    assert data['config_template_id'] == config_template


@given('update "{field}" for "{resource}" "{resource_id}" to "{value}" via rest')
def step_impl(context, resource, resource_id, field, value):
    results = context.rest.update_resource(resource, resource_id, field, value)


@given('create environment "{env}" for "{role_id}" via rest')
def step_impl(context, env, role_id):
    expected_env_id = '%s:%s' % (role_id, env)
    context.cli.create(
        {'resource': 'environment', 'role_id': role_id, 'name': env}
    )
    environment = context.rest.get_instance('environment', expected_env_id)
    assert environment['id'] == expected_env_id


@step('create k8s_cluster "{name}" in "{environment}" via rest')
def step_impl(context, name, environment):
    expected_cluster_id = '%s:%s:k8s' % (environment, name)
    context.cli.create(
        {'resource': 'k8s_cluster', 'environment_id': environment, 'name': name}
    )
    k8s_cluster = context.rest.get_instance('k8s_cluster', expected_cluster_id)
    assert k8s_cluster['id'] == expected_cluster_id


@step('environment "{id}" can be created via rest')
def step_impl(context, id):
    prov = context.rest.create_resource(
        {'id': id, 'resource': 'environment'})
    data = prov.json()
    assert data['id'] == id
