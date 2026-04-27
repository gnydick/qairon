import sys
import os
from datetime import datetime, timezone

from behave import given, when, then

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'fixtures', 'social_network'))

from generate_monitoring_data import (
    MonitoringDataGenerator, ServiceAction, User, Persona,
    uniform_hours, uniform_week,
)

_REQUIRED_STRING_FIELDS = [
    'timestamp', 'level', 'service', 'stack', 'action',
    'user_id', 'request_id', 'message', 'release_id', 'trace_id', 'span_id',
]
_REQUIRED_BOOL_FIELDS = ['success']

_ERROR_FIELDS = ['error_code', 'error_message', 'error_source', 'error_type']


def _minimal_persona():
    return Persona(
        name='test',
        description='test persona',
        user_percentage=1.0,
        activity_multiplier=1.0,
        action_weights={'read': 1.0},
        hourly_weights=uniform_hours(),
        daily_weights=uniform_week(),
        success_rate=0.99,
        latency_multiplier=1.0,
    )


def _minimal_user():
    return User(
        user_id='user_test',
        persona=_minimal_persona(),
        created_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
    )


@given('a monitoring data generator with seed {seed:d}')
def step_create_generator(context, seed):
    context.generator = MonitoringDataGenerator(total_events=1, total_users=1, seed=seed)
    context.user = _minimal_user()


@given('an action "{action_name}" on "{service_id}" that is a read')
def step_read_action(context, action_name, service_id):
    application, stack, service = service_id.split(':')
    context.action = ServiceAction(
        category='read',
        service=service,
        stack=stack,
        action=action_name,
        application=application,
        weight=1.0,
        base_latency_ms=100.0,
        latency_stddev_ms=10.0,
        base_payload_bytes=1024,
        payload_stddev_bytes=100,
        has_target_user=False,
        has_object_id=True,
        object_type='post',
        is_write=False,
    )


@given('an action "{action_name}" on "{service_id}" that is a write')
def step_write_action(context, action_name, service_id):
    application, stack, service = service_id.split(':')
    context.action = ServiceAction(
        category='write',
        service=service,
        stack=stack,
        action=action_name,
        application=application,
        weight=1.0,
        base_latency_ms=150.0,
        latency_stddev_ms=15.0,
        base_payload_bytes=2048,
        payload_stddev_bytes=200,
        has_target_user=False,
        has_object_id=True,
        object_type='post',
        is_write=True,
    )


@when('a successful log entry is generated')
def step_gen_success_log(context):
    context.log_entry = context.generator.generate_log(
        action=context.action,
        user=context.user,
        timestamp=datetime(2025, 1, 1, tzinfo=timezone.utc),
        request_id='req_test',
        success=True,
        target_user_id=None,
        object_id='post_123',
        release_id='prod:aws:111111111111:us-east-1:platform:eks:main:social:content:posts:default:1',
        trace_id='a' * 32,
        span_id='b' * 16,
    )


@when('a successful log entry is generated as a root span')
def step_gen_root_span_log(context):
    context.log_entry = context.generator.generate_log(
        action=context.action,
        user=context.user,
        timestamp=datetime(2025, 1, 1, tzinfo=timezone.utc),
        request_id='req_test',
        success=True,
        target_user_id=None,
        object_id=None,
        release_id='prod:aws:111111111111:us-east-1:platform:eks:main:social:content:posts:default:1',
        trace_id='a' * 32,
        span_id='b' * 16,
        parent_span_id=None,
    )


@when('a successful log entry is generated as a child of span "{parent_span_id}"')
def step_gen_child_span_log(context, parent_span_id):
    context.log_entry = context.generator.generate_log(
        action=context.action,
        user=context.user,
        timestamp=datetime(2025, 1, 1, tzinfo=timezone.utc),
        request_id='req_test',
        success=True,
        target_user_id=None,
        object_id=None,
        release_id='prod:aws:111111111111:us-east-1:platform:eks:main:social:content:posts:default:1',
        trace_id='a' * 32,
        span_id='b' * 16,
        parent_span_id=parent_span_id,
    )


@when('a failed log entry is generated with error_type "{error_type}"')
def step_gen_failed_log(context, error_type):
    error_codes_by_type = {'client': '404', 'server': '500', 'database': '500',
                           'cache': '503', 'queue': '503', 'internal': '500'}
    error_code = error_codes_by_type.get(error_type, '500')
    context.log_entry = context.generator.generate_log(
        action=context.action,
        user=context.user,
        timestamp=datetime(2025, 1, 1, tzinfo=timezone.utc),
        request_id='req_test',
        success=False,
        target_user_id=None,
        object_id=None,
        release_id='prod:aws:111111111111:us-east-1:platform:eks:main:social:content:posts:default:1',
        trace_id='a' * 32,
        span_id='b' * 16,
        error_info={
            'error_type': error_type,
            'error_code': error_code,
            'error_message': 'test error',
            'error_source': None,
            'downstream_request_id': None,
        },
    )


@when('a failed log entry is generated with code "{error_code}" and type "{error_type}"')
def step_gen_failed_log_with_code(context, error_type, error_code):
    context.log_entry = context.generator.generate_log(
        action=context.action,
        user=context.user,
        timestamp=datetime(2025, 1, 1, tzinfo=timezone.utc),
        request_id='req_test',
        success=False,
        target_user_id=None,
        object_id=None,
        release_id='prod:aws:111111111111:us-east-1:platform:eks:main:social:content:posts:default:1',
        trace_id='a' * 32,
        span_id='b' * 16,
        error_info={
            'error_type': error_type,
            'error_code': error_code,
            'error_message': 'test error',
            'error_source': None,
            'downstream_request_id': None,
        },
    )


@then('the log level is "{expected_level}"')
def step_check_log_level(context, expected_level):
    assert context.log_entry.level == expected_level, \
        f'Expected level {expected_level!r}, got {context.log_entry.level!r}'


@then('the log message contains "{fragment}"')
def step_check_log_message(context, fragment):
    assert fragment in context.log_entry.message, \
        f'Expected message to contain {fragment!r}, got {context.log_entry.message!r}'


@then('the log entry has all required fields')
def step_check_required_fields(context):
    entry_dict = context.log_entry.__dict__
    for field in _REQUIRED_STRING_FIELDS:
        val = entry_dict.get(field)
        assert val is not None and val != '', \
            f'Required string field {field!r} is missing, None, or empty (got {val!r})'
    for field in _REQUIRED_BOOL_FIELDS:
        assert field in entry_dict and isinstance(entry_dict[field], bool), \
            f'Required bool field {field!r} is missing or not a bool (got {entry_dict.get(field)!r})'


@then('the log entry error fields are all None')
def step_check_error_fields_none(context):
    entry_dict = context.log_entry.__dict__
    for field in _ERROR_FIELDS:
        assert entry_dict.get(field) is None, \
            f'Expected {field!r} to be None on success, got {entry_dict.get(field)!r}'


@then('the log entry error_code is "{expected}"')
def step_check_error_code(context, expected):
    assert context.log_entry.error_code == expected, \
        f'Expected error_code {expected!r}, got {context.log_entry.error_code!r}'


@then('the log entry error_type is "{expected}"')
def step_check_error_type(context, expected):
    assert context.log_entry.error_type == expected, \
        f'Expected error_type {expected!r}, got {context.log_entry.error_type!r}'


@then('the log entry error_message is not None')
def step_check_error_message_set(context):
    assert context.log_entry.error_message is not None, \
        'Expected error_message to be set on failure'


@then('the log entry parent_span_id is None')
def step_check_parent_none(context):
    assert context.log_entry.parent_span_id is None, \
        f'Expected parent_span_id to be None, got {context.log_entry.parent_span_id!r}'


@then('the log entry parent_span_id is "{expected}"')
def step_check_parent_id(context, expected):
    assert context.log_entry.parent_span_id == expected, \
        f'Expected parent_span_id {expected!r}, got {context.log_entry.parent_span_id!r}'