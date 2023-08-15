from behave import *


@given('create "{resource}" "{res_id}" via rest')
def step_impl(context, resource, res_id):
    res = context.rest.create_resource(
        {'id': res_id, 'resource': resource})
    data = res.json()
    assert data['data']['id'] == res_id


@then(
    'create build_artifact for "{build_id}" from "{input_repo_id}" uploaded to "{output_repo_id}" named "{name}" in path "{upload_path}" via rest')
def step_impl(context, build_id, input_repo_id, output_repo_id, name, upload_path):
    res = context.rest.create_resource(
        {'resource': 'build_artifact', 'build_id': build_id, 'input_repo_id': input_repo_id,
         'output_repo_id': output_repo_id, 'name': name, 'upload_path': upload_path}
    )
    data = res.json()
    assert data['data']['id'] == ':'.join([build_id, name])


@then(
    'create release_artifact for "{release_id}" from "{input_repo_id}" uploaded to "{output_repo_id}" named "{name}" in path "{upload_path}" via rest')
def step_impl(context, release_id, input_repo_id, output_repo_id, name, upload_path):
    res = context.rest.create_resource(
        {'resource': 'release_artifact', 'release_id': release_id, 'input_repo_id': input_repo_id,
         'output_repo_id': output_repo_id, 'name': name, 'upload_path': upload_path}
    )
    data = res.json()
    assert data['data']['id'] == ':'.join([release_id, name])


@then('create "{resource}" with parent id "{parent_id}" in parent field "{parent_field}" named "{name}" via rest')
def step_impl(context, resource, parent_id, parent_field, name):
    res = context.rest.create_resource(
        {'resource': resource, parent_field: parent_id, 'name': name}
    )
    data = res.json()
    assert data['data']['id'] == ':'.join([parent_id, name])


@then(
    'create provider in env "{environment_id}" of type "{provider_type_id}" with native_id "{native_id}" via rest')
def step_impl(context, environment_id, provider_type_id, native_id):
    res = context.rest.create_resource(
        {'environment_id': environment_id, 'provider_type_id': provider_type_id, 'resource': 'provider',
         'native_id': native_id}
    )
    data = res.json()
    assert data['data']['id'] == ':'.join([environment_id, provider_type_id, native_id])


@then('allocate subnet "{network_id}" "{additional_mask_bits}" "{subnet_name}" via rest')
def step_impl(context, network_id, additional_mask_bits, subnet_name):
    res = context.rest.allocate_subnet(network_id, additional_mask_bits, subnet_name)
    data = res.json()
    assert data['data']['id'] == '%s:%s' % (network_id, subnet_name)


@then('create "{field}" "{field_val}" "{resource}" "{res_name}" under "{parent_fk_field}" "{parent_id}" via rest')
def step_impl(context, field, field_val, resource, res_name, parent_fk_field, parent_id):
    res = context.rest.create_resource(
        {'name': res_name, parent_fk_field: parent_id, 'resource': resource, field: field_val}
    )
    data = res.json()
    assert data['data']['id'] == '%s:%s' % (parent_id, res_name)


@then('create "{resource}" "{res_name}" under "{parent_fk_field}" "{parent_id}" via rest')
def step_impl(context, resource, res_name, parent_fk_field, parent_id):
    res = context.rest.create_resource(
        {'name': res_name, parent_fk_field: parent_id, 'resource': resource}
    )
    data = res.json()
    assert data['data']['id'] == '%s:%s' % (parent_id, res_name)


@then(
    'create textresource "{resource}" "{res_name}" under "{parent_fk_field}" "{parent_id}" with doc "{doc}" via rest')
def step_impl(context, resource, res_name, parent_fk_field, parent_id, doc):
    res = context.rest.create_resource(
        {'id': res_name, parent_fk_field: parent_id, 'resource': resource, 'doc': doc}
    )
    data = res.json()
    assert data['data']['id'] == res_name


# use_step_matcher("re")
@given('provider "{provider}" can be created via rest')
def step_impl(context, provider):
    prov = context.rest.create_resource(
        {'id': provider, 'resource': 'provider'})
    data = prov.json()
    assert data['data']['id'] == provider


@given('region "{region}" can be created for provider "{provider}" via rest')
def step_impl(context, region, provider):
    new_region = context.rest.create_resource(
        {'name': region, 'provider_id': provider, 'resource': 'region'})
    data = new_region.json()
    assert data['data']['id'] == '%s:%s' % (provider, region)


@given('zone "{zone}" can be created for region "{region}" via rest')
def step_impl(context, zone, region):
    new_zone = context.rest.create_resource(
        {'name': zone, 'region_id': region, 'resource': 'zone', 'defaults': '{}'})
    data = new_zone.json()
    assert data['data']['id'] == '%s:%s' % (region, zone)


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
    assert data['data']['id'] == app_id


@given('stack "{stack}" can be created for app "{app_id}" via rest')
def step_impl(context, stack, app_id):
    new_stack = context.rest.create_resource(
        {'name': stack, 'application_id': app_id, 'resource': 'stack', 'defaults': '{}'})
    data = new_stack.json()
    assert data['data']['id'] == '%s:%s' % (app_id, stack)


@given('service "{service}" can be created for stack "{stack}" via rest')
def step_impl(context, service, stack):
    new_service = context.rest.create_resource(
        {'name': service, 'stack_id': stack, 'resource': 'service', 'defaults': '{}'})
    data = new_service.json()
    assert data['data']['id'] == '%s:%s' % (stack, service)


@given('environment "{environment}" can be created at "{deployment_url}" via rest')
def step_impl(context, environment, deployment_url, role):
    new_env = context.rest.create_resource(
        {'resource': 'environment', 'id': environment, 'deployment_url': deployment_url, 'defaults': '{}'}
    )
    data = new_env.json()
    assert data['data']['id'] == environment


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
    assert data['data']['id'] == '%s:%s' % (service_id, job_number)


@then('create release for "{deployment_id}" from build "{build_id}" from job "{build_num}" via rest')
def step_impl(context, deployment_id, build_id, build_num):
    response = context.rest.create_resource(
        {'resource': 'release', 'deployment_id': deployment_id, 'build_id': build_id, 'build_num': build_num})
    data = response.json()
    assert data['data']['id'] == '%s:%s' % (deployment_id, build_num)


@then(
    'create deployment at "{dep_target_bin_id}" for "{service}" tagged "{tag}" with defaults "{defaults}" via rest')
def step_impl(context, dep_target_bin_id, service, tag, defaults):
    response = context.rest.create_resource(
        {'resource': 'deployment', 'deployment_target_bin_id': dep_target_bin_id, 'service_id': service,
         'tag': tag, 'defaults': defaults}
    )
    data = response.json()
    assert data['data']['id'] == '%s:%s:%s' % (dep_target_bin_id, service, tag)
    new_dep = context.rest.get_instance('deployment', data['data']['id'])
    assert new_dep['attributes']['defaults'] == defaults
    assert new_dep['attributes']['tag'] == tag


# @then(
#     'service_config_template "{service_config_template}" can be created for service "{service}" via rest')
# def step_impl(context, service_config_template, service):
#     response = context.rest.create_resource(
#         {'resource': 'service_config_template', 'name': service_config_template, 'service_id': service, 'template': ''}
#     )
#     new_svc_config = response.json()
#     assert new_svc_config['id'] == '%s:%s' % (service, service_config_template)


@when('add first - "{number}" - "{singular_resource}" to "{plural_resource}" "{item_id}" on "{dest_resource}" "{dest_id}" via rest')
@when('add second - "{number}" - "{singular_resource}" to "{plural_resource}" "{item_id}" on "{dest_resource}" "{dest_id}" via rest')
def step_impl(context, number, singular_resource, plural_resource, item_id, dest_resource, dest_id):
    response = context.rest.add_to_many_to_many(dest_resource, dest_id, singular_resource, plural_resource, item_id)
    assert len(response) == eval(number)


@then(
    'remove first - "{number}" - "{singular_resource}" from "{plural_resource}" "{item_id}" on "{dest_resource}" "{dest_id}" via rest')
@then(
    'remove second - "{number}" - "{singular_resource}" from "{plural_resource}" "{item_id}" on "{dest_resource}" "{dest_id}" via rest')
def step_impl(context, number, singular_resource, plural_resource, item_id, dest_resource, dest_id):
    response = context.rest.del_from_many_to_many(dest_resource, dest_id, singular_resource, plural_resource, item_id)
    assert len(response) == eval(number)

@then(
    'create config for resource "{resource}" named "{name}" from template "{config_template_id}" can be created for "{resource_id}" tagged "{tag}" via rest')
@given(
    'create config for resource "{resource}" named "{name}" from template "{config_template_id}" can be created for "{resource_id}" tagged "{tag}" via rest')
def step_impl(context, resource, name, config_template_id, resource_id, tag):
    payload = {'resource': "%s_config" % resource, 'name': name, 'config_template_id': config_template_id,
               '%s_id' % resource: resource_id, 'tag': tag}
    cfg = context.rest.create_resource(payload)
    data = cfg.json()
    assert data['data']['relationships']['template']['data']['id'] == config_template_id
