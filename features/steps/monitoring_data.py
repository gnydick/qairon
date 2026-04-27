import random
import sys
import os
from datetime import datetime, timezone

from behave import given, when, then

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'fixtures', 'social_network'))

from generate_monitoring_data import generate_child_spans_for_event
from qairon_ids import deployment_id_from_release_id

_FAKE_ENV = 'prod:aws:111111111111:us-east-1:platform:eks:main'
_ERROR_CODES = {'server': ['500', '502', '503']}
_ERROR_MESSAGES = {'500': 'Internal Server Error', '502': 'Bad Gateway', '503': 'Service Unavailable'}


def _fake_release(stack, service, ts):
    release_id = f'{_FAKE_ENV}:social:{stack}:{service}:default:1'
    return (release_id, None, None, None)


def _make_root_event(service_id, error_info=None):
    application, stack, service = service_id.split(':')
    release_id = f'{_FAKE_ENV}:{application}:{stack}:{service}:default:1'
    return {
        'application': application,
        'stack': stack,
        'service': service,
        'action_action': 'test_action',
        'action_category': 'read',
        'action_base_latency_ms': 200.0,
        'action_latency_stddev_ms': 20.0,
        'action_base_payload_bytes': 1024,
        'action_payload_stddev_bytes': 256,
        'action_has_target_user': False,
        'action_has_object_id': False,
        'action_object_type': None,
        'action_is_write': False,
        'latency_multiplier': 1.0,
        'timestamp': datetime(2025, 1, 1, tzinfo=timezone.utc),
        'request_id': 'req_root',
        'trace_id': 'a' * 32,
        'span_id': 'b' * 16,
        'parent_span_id': None,
        'success': error_info is None,
        'error_info': error_info,
        'object_id': None,
        'target_user_id': None,
        'user_id': 'user_1',
        'persona_name': 'regular',
        'release_id': release_id,
    }


@given('a predictable release selector')
def step_predictable_release(context):
    context.rng = random.Random(42)


@given('a root event for service "{service_id}"')
def step_root_event(context, service_id):
    context.root_event = _make_root_event(service_id)


@given('the root event blames "{blamed_service_id}" for its error')
def step_root_event_blame(context, blamed_service_id):
    blamed_app, blamed_stack, blamed_service = blamed_service_id.split(':')
    blamed_release_id = f'{_FAKE_ENV}:{blamed_app}:{blamed_stack}:{blamed_service}:default:1'
    blamed_deployment_id = deployment_id_from_release_id(blamed_release_id)
    context.root_event['error_info'] = {
        'error_source': blamed_deployment_id,
        'error_type': 'server',
        'error_code': '503',
        'error_message': 'Service Unavailable',
        'downstream_request_id': 'req_downstream',
    }
    context.root_event['success'] = False


@when('child spans are generated')
def step_generate_spans(context):
    context.child_spans = generate_child_spans_for_event(
        parent_event=context.root_event,
        rng=context.rng,
        select_release_func=_fake_release,
        error_codes=_ERROR_CODES,
        error_messages=_ERROR_MESSAGES,
    )


@then('no child spans are produced')
def step_no_children(context):
    assert context.child_spans == [], \
        f'Expected no child spans, got {len(context.child_spans)}'


@then('child spans are produced')
def step_has_children(context):
    assert len(context.child_spans) > 0, 'Expected child spans but got none'


@then('a span exists for service "{service_id}"')
def step_span_exists(context, service_id):
    application, stack, service = service_id.split(':')
    matches = [
        s for s in context.child_spans
        if s['application'] == application and s['stack'] == stack and s['service'] == service
    ]
    assert matches, f'No span found for {service_id}'


@then('every span has the root trace_id')
def step_all_share_trace_id(context):
    root_trace_id = context.root_event['trace_id']
    bad = [s for s in context.child_spans if s['trace_id'] != root_trace_id]
    assert not bad, f'{len(bad)} span(s) have wrong trace_id: {bad[0]}'


@then('every span has a parent_span_id that matches a known span_id')
def step_all_parents_valid(context):
    known_span_ids = {context.root_event['span_id']} | {s['span_id'] for s in context.child_spans}
    bad = [s for s in context.child_spans if s['parent_span_id'] not in known_span_ids]
    assert not bad, f'{len(bad)} span(s) have dangling parent_span_id: {bad[0]}'


@then('"{service_id}" appears more than once')
def step_appears_multiple_times(context, service_id):
    application, stack, service = service_id.split(':')
    matches = [
        s for s in context.child_spans
        if s['application'] == application and s['stack'] == stack and s['service'] == service
    ]
    assert len(matches) > 1, \
        f'Expected {service_id} to appear more than once, but found {len(matches)} span(s)'


@then('the span for "{service_id}" is a child of "{parent_service_id}"')
def step_span_is_child_of(context, service_id, parent_service_id):
    p_app, p_stack, p_svc = parent_service_id.split(':')
    parent_span_ids = {
        s['span_id'] for s in context.child_spans
        if s['application'] == p_app and s['stack'] == p_stack and s['service'] == p_svc
    }
    assert parent_span_ids, f'No span found for parent {parent_service_id}'

    c_app, c_stack, c_svc = service_id.split(':')
    children = [
        s for s in context.child_spans
        if s['application'] == c_app and s['stack'] == c_stack and s['service'] == c_svc
        and s['parent_span_id'] in parent_span_ids
    ]
    assert children, (
        f'No span for {service_id} has a parent_span_id belonging to {parent_service_id}; '
        f'known parent span_ids: {parent_span_ids}'
    )


@then('a blamed span exists for "{service_id}"')
def step_blamed_span_exists(context, service_id):
    application, stack, service = service_id.split(':')
    blamed = [
        s for s in context.child_spans
        if s['application'] == application and s['stack'] == stack and s['service'] == service
        and not s['success']
        and (s.get('error_info') or {}).get('error_source') is None
    ]
    assert blamed, (
        f'No span for {service_id} has success=False and error_source=None; '
        f'all {service_id} spans: {[s["success"] for s in context.child_spans if s["service"] == service]}'
    )