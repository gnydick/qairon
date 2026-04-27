import sys
import os
from datetime import datetime, timezone

from behave import given, when, then

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'fixtures', 'social_network'))

from generate_monitoring_data import DeploymentSchedule, DeploymentWindow


def _dt(iso_str: str) -> datetime:
    return datetime.fromisoformat(iso_str).replace(tzinfo=timezone.utc)


def _make_window(stack, service, env, region, start_iso, end_iso):
    start = _dt(start_iso)
    end = _dt(end_iso)
    release_id = f'{env}:aws:111111111111:{region}:platform:eks:main:social:{stack}:{service}:default:1'
    deployment_id = f'{env}:aws:111111111111:{region}:platform:eks:main:social:{stack}:{service}:default'
    return DeploymentWindow(
        deployment_id=deployment_id,
        release_id=release_id,
        stack=stack,
        service=service,
        env=env,
        region=region,
        start_time=start,
        end_time=end,
        throughput_factor=0.75,
        error_rate_boost=0.03,
        latency_multiplier=1.35,
    )


@given('an empty deployment schedule')
def step_empty_schedule(context):
    context.schedule = DeploymentSchedule()


@given('a deployment schedule with a release for "{stack}" "{service}" in "{env}" "{region}" created at "{created_at}" with id "{release_id}"')
def step_schedule_with_release(context, stack, service, env, region, created_at, release_id):
    if not hasattr(context, 'schedule') or context.schedule is None:
        context.schedule = DeploymentSchedule()
    key = (env, region, stack, service)
    timeline = context.schedule._release_timelines.setdefault(key, [])
    timeline.append((_dt(created_at), release_id, 1))
    timeline.sort(key=lambda x: x[0])


@given('a release for "{stack}" "{service}" in "{env}" "{region}" created at "{created_at}" with id "{release_id}"')
def step_add_release(context, stack, service, env, region, created_at, release_id):
    key = (env, region, stack, service)
    timeline = context.schedule._release_timelines.setdefault(key, [])
    timeline.append((_dt(created_at), release_id, len(timeline) + 1))
    timeline.sort(key=lambda x: x[0])


@given('a deployment schedule with a deployment window for "{stack}" "{service}" in "{env}" "{region}" from "{start_iso}" to "{end_iso}"')
def step_schedule_with_window(context, stack, service, env, region, start_iso, end_iso):
    if not hasattr(context, 'schedule') or context.schedule is None:
        context.schedule = DeploymentSchedule()
    key = (stack, service, env, region)
    windows = context.schedule._deployment_windows.setdefault(key, [])
    windows.append(_make_window(stack, service, env, region, start_iso, end_iso))
    windows.sort(key=lambda w: w.start_time)


@given('a deployment window for "{stack}" "{service}" in "{env}" "{region}" from "{start_iso}" to "{end_iso}"')
def step_add_window(context, stack, service, env, region, start_iso, end_iso):
    key = (stack, service, env, region)
    windows = context.schedule._deployment_windows.setdefault(key, [])
    windows.append(_make_window(stack, service, env, region, start_iso, end_iso))
    windows.sort(key=lambda w: w.start_time)


@when('looking up the active release for "{stack}" "{service}" in "{env}" "{region}" at "{ts_iso}"')
def step_lookup_release(context, stack, service, env, region, ts_iso):
    context.found_release = context.schedule.get_active_release_id(env, region, stack, service, _dt(ts_iso))


@when('checking for a deployment window for "{stack}" "{service}" in "{env}" "{region}" at "{ts_iso}"')
def step_check_window(context, stack, service, env, region, ts_iso):
    context.found_window = context.schedule.get_active_deployment_window(stack, service, env, region, _dt(ts_iso))


@when('the schedule is serialized and deserialized')
def step_round_trip(context):
    context.schedule = DeploymentSchedule.from_serializable(context.schedule.to_serializable())


@then('no active release is found')
def step_no_release(context):
    assert context.found_release is None, \
        f'Expected no release, got {context.found_release!r}'


@then('the active release id is "{expected_id}"')
def step_release_found(context, expected_id):
    assert context.found_release == expected_id, \
        f'Expected release {expected_id!r}, got {context.found_release!r}'


@then('no deployment window is active')
def step_no_window(context):
    assert context.found_window is None, \
        'Expected no active deployment window'


@then('a deployment window is active')
def step_window_active(context):
    assert context.found_window is not None, \
        'Expected an active deployment window'


@then('the deployment window throughput_factor is less than 1.0')
def step_window_throughput(context):
    assert context.found_window.throughput_factor < 1.0, \
        f'Expected throughput_factor < 1.0, got {context.found_window.throughput_factor}'


@then('the deployment window latency_multiplier is greater than 1.0')
def step_window_latency(context):
    assert context.found_window.latency_multiplier > 1.0, \
        f'Expected latency_multiplier > 1.0, got {context.found_window.latency_multiplier}'


@then('the deployment window error_rate_boost is greater than 0.0')
def step_window_error_boost(context):
    assert context.found_window.error_rate_boost > 0.0, \
        f'Expected error_rate_boost > 0.0, got {context.found_window.error_rate_boost}'


@then('looking up the active release for "{stack}" "{service}" in "{env}" "{region}" at "{ts_iso}" returns "{expected_id}"')
def step_lookup_after_round_trip(context, stack, service, env, region, ts_iso, expected_id):
    result = context.schedule.get_active_release_id(env, region, stack, service, _dt(ts_iso))
    assert result == expected_id, \
        f'Expected {expected_id!r} after round-trip, got {result!r}'


@then('a deployment window is active for "{stack}" "{service}" in "{env}" "{region}" at "{ts_iso}"')
def step_window_active_after_round_trip(context, stack, service, env, region, ts_iso):
    result = context.schedule.get_active_deployment_window(stack, service, env, region, _dt(ts_iso))
    assert result is not None, \
        f'Expected an active deployment window after round-trip for {stack}:{service} at {ts_iso}'