from behave import *


@step('execute completer 1 and 2 add_service_config_for_service_completer "{service_id}"')
def step_impl(context, service_id):
    parser = context.args.assign_args(context.rest)
    parsed_args, unknown_args = parser.parse_known_args(['service', 'add_svc_config', service_id, 'mock'])
    filtered_service_config_templates = context.rest.add_service_config_for_service_completer(None, parsed_args)
    assert 'testservice_config1' not in filtered_service_config_templates
    assert 'testservice_config2' not in filtered_service_config_templates
    assert 'testservice_config3' in filtered_service_config_templates


@step('execute completer just 1 add_service_config_for_service_completer "{service_id}"')
def step_impl(context, service_id):
    parser = context.args.assign_args(context.rest)
    parsed_args, unknown_args = parser.parse_known_args(['service', 'add_svc_config', service_id, 'mock'])
    filtered_service_config_templates = context.rest.add_service_config_for_service_completer(None, parsed_args)
    assert 'testservice_config1' not in filtered_service_config_templates
    assert 'testservice_config2' in filtered_service_config_templates
    assert 'testservice_config3' in filtered_service_config_templates


@step('execute completer 1 and 2 add_zone_for_deployment_completer "{deployment_id}"')
def step_impl(context, deployment_id):
    parser = context.args.assign_args(context.rest)
    parsed_args, unknown_args = parser.parse_known_args(['deployment', 'addzone', deployment_id, 'mock'])
    filtered_zones = context.rest.add_zone_for_deployment_completer(None, parsed_args)
    assert 'testprov:testregion:testzone1' not in filtered_zones
    assert 'testprov:testregion:testzone2' not in filtered_zones
    assert 'testprov:testregion:testzone3' in filtered_zones


@step('execute completer just 1 add_zone_for_deployment_completer "{deployment_id}"')
def step_impl(context, deployment_id):
    parser = context.args.assign_args(context.rest)
    parsed_args, unknown_args = parser.parse_known_args(['deployment', 'addzone', deployment_id, 'mock'])
    filtered_zones = context.rest.add_zone_for_deployment_completer(None, parsed_args)
    assert 'testprov:testregion:testzone1' not in filtered_zones
    assert 'testprov:testregion:testzone2' in filtered_zones
    assert 'testprov:testregion:testzone3' in filtered_zones


########################


@step('execute completer 1 and 2 del_service_config_for_service_completer "{service_id}"')
def step_impl(context, service_id):
    parser = context.args.assign_args(context.rest)
    parsed_args, unknown_args = parser.parse_known_args(['service', 'add_svc_config', service_id, 'mock'])
    filtered_service_config_templates = context.rest.del_service_config_for_service_completer(None, parsed_args)
    assert 'testservice_config1' in filtered_service_config_templates
    assert 'testservice_config2' in filtered_service_config_templates
    assert 'testservice_config3' not in filtered_service_config_templates


@step('execute completer just 1 del_service_config_for_service_completer "{service_id}"')
def step_impl(context, service_id):
    parser = context.args.assign_args(context.rest)
    parsed_args, unknown_args = parser.parse_known_args(['service', 'add_svc_config', service_id, 'mock'])
    filtered_service_config_templates = context.rest.del_service_config_for_service_completer(None, parsed_args)
    assert 'testservice_config1' in filtered_service_config_templates
    assert 'testservice_config2' not in filtered_service_config_templates
    assert 'testservice_config3' not in filtered_service_config_templates


@step('execute completer 1 and 2 del_zone_for_deployment_completer "{deployment_id}"')
def step_impl(context, deployment_id):
    parser = context.args.assign_args(context.rest)
    parsed_args, unknown_args = parser.parse_known_args(['deployment', 'addzone', deployment_id, 'mock'])
    filtered_zones = context.rest.del_zone_for_deployment_completer(None, parsed_args)
    assert 'testprov:testregion:testzone1' in filtered_zones
    assert 'testprov:testregion:testzone2' in filtered_zones
    assert 'testprov:testregion:testzone3' not in filtered_zones


@step('execute completer just 1 del_zone_for_deployment_completer "{deployment_id}"')
def step_impl(context, deployment_id):
    parser = context.args.assign_args(context.rest)
    parsed_args, unknown_args = parser.parse_known_args(['deployment', 'addzone', deployment_id, 'mock'])
    filtered_zones = context.rest.del_zone_for_deployment_completer(None, parsed_args)
    assert 'testprov:testregion:testzone1' in filtered_zones
    assert 'testprov:testregion:testzone2' not in filtered_zones
    assert 'testprov:testregion:testzone3' not in filtered_zones


@step('execute completer "{resource}" "{command}"')
def step_impl(context, resource, command):
    parser = context.args.assign_args(context.rest)
    parsed_args, unknown_args = parser.parse_known_args([resource, command, 'mock'])
    results = context.rest.resource_get_search(None, parsed_args)