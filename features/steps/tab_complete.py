import os
from io import StringIO
from unittest.mock import patch

import argcomplete
from behave import given, when, then


_ENV = 'tcenv'
_PTYPE = 'tcptype'
_PROV = 'tcprov'
_REGION = 'tcregion'
_PART = 'tcpart'
_TT = 'tck8s'
_DT = 'tcdt'
_APP = 'tcapp'
_STACK = 'tcstack'
_SVC = 'tcsvc'
_REPOTYPE = 'tcrepotype'

_PROVIDER_ID = f'{_ENV}:{_PTYPE}:{_PROV}'
_REGION_ID = f'{_PROVIDER_ID}:{_REGION}'
_PARTITION_ID = f'{_REGION_ID}:{_PART}'
_TARGET_ID = f'{_PARTITION_ID}:{_TT}:{_DT}'
_SERVICE_ID = f'{_APP}:{_STACK}:{_SVC}'
_DEPLOYMENT_ID = f'{_TARGET_ID}:{_SERVICE_ID}:default'


def _zone_id(name):
    return f'{_REGION_ID}:{name}'


def _repo_id(name):
    return f'{_REPOTYPE}:{name}'


def _get_completions(parser, comp_line):
    with patch.dict(os.environ, {
        '_ARGCOMPLETE': '1',
        'COMP_LINE': comp_line,
        'COMP_POINT': str(len(comp_line)),
    }):
        out = StringIO()
        argcomplete.autocomplete(parser, output_stream=out, exit_method=lambda _: None)
    return [c.rstrip() for c in out.getvalue().split('\013') if c.strip()]


@given('a live environment for tab completion tests')
def step_setup_env(context):
    if not getattr(context.feature, '_env_fixtures_exist', False):
        context.feature._env_fixtures_exist = True
        rest = context.rest
        rest.create_resource({'id': _ENV, 'resource': 'environment', 'deployment_url': 'http://test', 'defaults': '{}'})
        rest.create_resource({'id': _PTYPE, 'resource': 'provider_type'})
        rest.create_resource({'environment_id': _ENV, 'provider_type_id': _PTYPE, 'native_id': _PROV, 'resource': 'provider'})
        rest.create_resource({'name': _REGION, 'provider_id': _PROVIDER_ID, 'resource': 'region'})
        rest.create_resource({'name': _PART, 'region_id': _REGION_ID, 'resource': 'partition'})
        rest.create_resource({'id': _TT, 'resource': 'deployment_target_type'})
        rest.create_resource({'name': _DT, 'deployment_target_type_id': _TT, 'partition_id': _PARTITION_ID, 'resource': 'deployment_target'})
        rest.create_resource({'id': _APP, 'resource': 'application', 'defaults': '{}'})
        rest.create_resource({'name': _STACK, 'application_id': _APP, 'resource': 'stack', 'defaults': '{}'})
        rest.create_resource({'name': _SVC, 'stack_id': f'{_APP}:{_STACK}', 'resource': 'service', 'defaults': '{}'})
        rest.create_resource({'id': _REPOTYPE, 'resource': 'repo_type'})


@given('a deployment with zones "{zone1}" and "{zone2}" assigned and "{zone3}" unassigned')
def step_setup_zones(context, zone1, zone2, zone3):
    rest = context.rest
    for name in (zone1, zone2, zone3):
        rest.create_resource({'name': name, 'region_id': _REGION_ID, 'resource': 'zone', 'defaults': '{}'})
    r = rest.create_resource({
        'resource': 'deployment',
        'service_id': _SERVICE_ID,
        'deployment_target_id': _TARGET_ID,
        'tag': 'default',
        'defaults': '{}',
    })
    assert r.status_code in (200, 201), f'deployment creation failed: {r.status_code} {r.text}'
    rest.add_to_many_to_many('deployment', _DEPLOYMENT_ID, 'zone', 'zones', _zone_id(zone1))
    rest.add_to_many_to_many('deployment', _DEPLOYMENT_ID, 'zone', 'zones', _zone_id(zone2))


@given('a service with repos "{repo1}" and "{repo2}" assigned and "{repo3}" unassigned')
def step_setup_repos(context, repo1, repo2, repo3):
    rest = context.rest
    for name in (repo1, repo2, repo3):
        rest.create_resource({'name': name, 'repo_type_id': _REPOTYPE, 'resource': 'repo'})
    rest.add_to_many_to_many('service', _SERVICE_ID, 'repo', 'repos', _repo_id(repo1))
    rest.add_to_many_to_many('service', _SERVICE_ID, 'repo', 'repos', _repo_id(repo2))


@when('tab-completing "{comp_line}"')
def step_tab_complete(context, comp_line):
    parser = context.args.assign_args()
    context.completions = _get_completions(parser, comp_line)


@then('"{item}" is in completions')
def step_in_completions(context, item):
    assert item in context.completions, \
        f'{item!r} not in completions: {context.completions}'


@then('"{item}" is not in completions')
def step_not_in_completions(context, item):
    assert item not in context.completions, \
        f'{item!r} unexpectedly in completions: {context.completions}'