from behave import *


@given('create "{resource}" "{res_id}" via rest')
def step_impl(context, resource, res_id):
    res = context.rest.create_resource(
        {'id': res_id, 'resource': resource})
    data = res.json()
    assert data['id'] == res_id


@then('create build_artifact for "{build_id}" from "{input_repo_id}" uploaded to "{output_repo_id}" named "{name}" in path "{upload_path}"')
def step_impl(context, build_id, input_repo_id, output_repo_id, name, upload_path):
    res = context.rest.create_resource(
        {'resource': 'build_artifact', 'build_id': build_id, 'input_repo_id': input_repo_id, 'output_repo_id': output_repo_id, 'name': name, 'upload_path': upload_path}
    )
    data = res.json()
    assert data['id'] == ':'.join([build_id, name])


@then('create release_artifact for "{release_id}" from "{input_repo_id}" uploaded to "{output_repo_id}" named "{name}" in path "{upload_path}"')
def step_impl(context, release_id, input_repo_id, output_repo_id, name, upload_path):
    res = context.rest.create_resource(
        {'resource': 'release_artifact', 'release_id': release_id, 'input_repo_id': input_repo_id, 'output_repo_id': output_repo_id, 'name': name, 'upload_path': upload_path}
    )
    data = res.json()
    assert data['id'] == ':'.join([release_id, name])

@then('create "{resource}" with parent id "{parent_id}" in parent field "{parent_field}" named "{name}"')
def step_impl(context, resource, parent_id, parent_field, name):
    res = context.rest.create_resource(
        {'resource': resource, parent_field: parent_id, 'name': name}
    )
    data = res.json()
    assert data['id'] == ':'.join([parent_id, name])


@then(
    'create provider in env "{environment_id}" of type "{provider_type_id}" with native_id "{native_id}" via rest')
def step_impl(context, environment_id, provider_type_id, native_id):
    res = context.rest.create_resource(
        {'environment_id': environment_id, 'provider_type_id': provider_type_id, 'resource': 'provider',
         'native_id': native_id}
    )
    data = res.json()
    assert data['id'] == ':'.join([environment_id, provider_type_id, native_id])


@then('create "{resource}" "{res_name}" under "{parent_fk_field}" "{parent_id}" via rest')
def step_impl(context, resource, res_name, parent_fk_field, parent_id):
    res = context.rest.create_resource(
        {'name': res_name, parent_fk_field: parent_id, 'resource': resource}
    )
    data = res.json()
    assert data['id'] == '%s:%s' % (parent_id, res_name)


@then(
    'create textresource "{resource}" "{res_name}" under "{parent_fk_field}" "{parent_id}" with doc "{doc}" via rest')
def step_impl(context, resource, res_name, parent_fk_field, parent_id, doc):
    res = context.rest.create_resource(
        {'id': res_name, parent_fk_field: parent_id, 'resource': resource, 'doc': doc}
    )
    data = res.json()
    assert data['id'] == res_name


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


@given('create deployment_target "{name}" of type "{dep_target_type}" in "{partition_id}" via rest')
def step_impl(context, name, dep_target_type, partition_id):
    response = context.rest.create_resource(
        {'resource': 'deployment_target', 'deployment_target_type_id': dep_target_type,
         'partition_id': partition_id, 'name': name}
    )
    data = response.json()
    print(data)


@then('create build for "{service_id}" from job "{job_number}" tagged "{tag}" via rest')
def step_impl(context, service_id, job_number, tag):
    response = context.rest.create_resource(
        {'resource': 'build', 'service_id': service_id, 'build_num': job_number, 'vcs_ref': tag})
    data = response.json()
    assert data['id'] == '%s:%s' % (service_id, job_number)


@then('create release for "{deployment_id}" from build "{build_id}" from job "{build_num}" via rest')
def step_impl(context, deployment_id, build_id, build_num):
    response = context.rest.create_resource(
        {'resource': 'release', 'deployment_id': deployment_id, 'build_id': build_id, 'build_num': build_num})
    data = response.json()
    assert data['id'] == '%s:%s' % (deployment_id, build_num)

@given(
    'create deployment at "{dep_target_id}" for "{service}" tagged "{tag}" with defaults "{defaults}" via rest')
def step_impl(context, dep_target_id, service, tag, defaults):
    response = context.rest.create_resource(
        {'resource': 'deployment', 'deployment_target_id': dep_target_id, 'service_id': service,
         'tag': tag, 'defaults': defaults}
    )
    data = response.json()
    assert data['id'] == '%s:%s:%s' % (dep_target_id, service, tag)
    new_dep = context.rest.get_instance('deployment', data['id'])
    assert new_dep['defaults'] == defaults
    assert new_dep['tag'] == tag


@then(
    'service_config_template "{service_config_template}" can be created for service "{service}" via rest')
def step_impl(context, service_config_template, service):
    response = context.rest.create_resource(
        {'resource': 'service_config_template', 'name': service_config_template, 'service_id': service, 'template': ''}
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


@then(
    'create config for resource "{resource}" named "{name}" from template "{config_template_id}" can be created for "{resource_id}" tagged "{tag}" via rest')
@given(
    'create config for resource "{resource}" named "{name}" from template "{config_template_id}" can be created for "{resource_id}" tagged "{tag}" via rest')
def step_impl(context, resource, name, config_template_id, resource_id, tag):
    payload = {'resource': "%s_config" % resource, 'name': name, 'config_template_id': config_template_id,
               '%s_id' % resource: resource_id, 'tag': tag}
    cfg = context.rest.create_resource(payload)
    data = cfg.json()
    assert data['config_template_id'] == config_template_id


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
