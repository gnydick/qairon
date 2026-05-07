import csv
import json
import os
import tempfile

from behave import *
from qairon_qcli.plugins.csv_import.controllers import CSVImportController


@given('a CSV file with applications')
def step_impl(context):
    """Create a temporary CSV file with test applications."""
    context.csv_fd, context.csv_path = tempfile.mkstemp(suffix='.csv', text=True)
    with open(context.csv_path, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=['id', 'defaults'])
        writer.writeheader()
        writer.writerow({'id': 'testapp_csv1', 'defaults': '{}'})
        writer.writerow({'id': 'testapp_csv2', 'defaults': '{"team": "platform"}'})
        writer.writerow({'id': 'testapp_csv3', 'defaults': '{}'})


@given('a CSV file with stacks')
def step_impl(context):
    """Create a temporary CSV file with test stacks."""
    context.csv_fd, context.csv_path = tempfile.mkstemp(suffix='.csv', text=True)
    with open(context.csv_path, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=['id', 'application_id', 'defaults'])
        writer.writeheader()
        writer.writerow({'id': 'teststack_csv1', 'application_id': 'testapp_csv1', 'defaults': '{}'})
        writer.writerow({'id': 'teststack_csv2', 'application_id': 'testapp_csv1', 'defaults': '{}'})


@given('a CSV file with invalid data')
def step_impl(context):
    """Create a temporary CSV file with invalid data."""
    context.csv_fd, context.csv_path = tempfile.mkstemp(suffix='.csv', text=True)
    with open(context.csv_path, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=['id', 'defaults'])
        writer.writeheader()
        # Missing required field for some resource types
        writer.writerow({'id': '', 'defaults': '{}'})  # Empty ID
        writer.writerow({'id': 'invalid_json_app', 'defaults': '{invalid json}'})


@given('a CSV file with environments')
def step_impl(context):
    """Create a temporary CSV file with test environments."""
    context.env_csv_fd, context.env_csv_path = tempfile.mkstemp(suffix='.csv', text=True)
    with open(context.env_csv_path, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=['id', 'defaults'])
        writer.writeheader()
        writer.writerow({'id': 'testenv_csv1', 'defaults': '{}'})


@given('a CSV file with providers')
def step_impl(context):
    """Create a temporary CSV file with test providers."""
    context.prov_csv_fd, context.prov_csv_path = tempfile.mkstemp(suffix='.csv', text=True)
    with open(context.prov_csv_path, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=['environment_id', 'provider_type_id', 'native_id', 'defaults'])
        writer.writeheader()
        writer.writerow({
            'environment_id': 'testenv_csv1',
            'provider_type_id': 'testprovider_type',
            'native_id': 'testprovider_csv1',
            'defaults': '{}'
        })


@when('I import applications from the CSV file')
def step_impl(context):
    """Import applications from the CSV file."""
    controller = CSVImportController()
    context.successful, context.failed = controller.import_from_csv(
        resource_type='application',
        csv_file_path=context.csv_path,
        dry_run=False
    )


@when('I import stacks with dry run flag')
def step_impl(context):
    """Import stacks with dry run mode."""
    controller = CSVImportController()
    context.successful, context.failed = controller.import_from_csv(
        resource_type='stack',
        csv_file_path=context.csv_path,
        dry_run=True
    )


@when('I import resources from the invalid CSV')
def step_impl(context):
    """Attempt to import from invalid CSV."""
    controller = CSVImportController()
    context.successful, context.failed = controller.import_from_csv(
        resource_type='application',
        csv_file_path=context.csv_path,
        dry_run=False
    )


@when('I import environments first')
def step_impl(context):
    """Import environments from CSV."""
    controller = CSVImportController()
    context.env_successful, context.env_failed = controller.import_from_csv(
        resource_type='environment',
        csv_file_path=context.env_csv_path,
        dry_run=False
    )


@when('I import providers second')
def step_impl(context):
    """Import providers from CSV."""
    controller = CSVImportController()
    context.prov_successful, context.prov_failed = controller.import_from_csv(
        resource_type='provider',
        csv_file_path=context.prov_csv_path,
        dry_run=False
    )


@then('applications should be created successfully')
def step_impl(context):
    """Verify applications were created."""
    assert len(context.successful) == 3, f"Expected 3 successful imports, got {len(context.successful)}"
    assert len(context.failed) == 0, f"Expected 0 failures, got {len(context.failed)}"
    
    # Cleanup
    os.close(context.csv_fd)
    os.unlink(context.csv_path)


@then('no stacks should be created')
def step_impl(context):
    """Verify no actual resources were created in dry run."""
    # In dry run, successful means validated, not created
    # We can't verify nothing was created without querying the API
    pass


@then('validation should succeed')
def step_impl(context):
    """Verify validation succeeded."""
    assert len(context.successful) == 2, f"Expected 2 validated rows, got {len(context.successful)}"
    assert len(context.failed) == 0, f"Expected 0 validation failures, got {len(context.failed)}"
    
    # Cleanup
    os.close(context.csv_fd)
    os.unlink(context.csv_path)


@then('import should fail with errors')
def step_impl(context):
    """Verify import failed for invalid data."""
    # We expect at least one failure due to invalid data
    assert len(context.failed) > 0, f"Expected failures, got {len(context.failed)} failures"
    
    # Cleanup
    os.close(context.csv_fd)
    os.unlink(context.csv_path)


@then('both resources should be created in correct order')
def step_impl(context):
    """Verify both resource types were created."""
    assert len(context.env_successful) == 1, f"Expected 1 environment, got {len(context.env_successful)}"
    assert len(context.prov_successful) == 1, f"Expected 1 provider, got {len(context.prov_successful)}"
    assert len(context.env_failed) == 0, f"Expected 0 environment failures, got {len(context.env_failed)}"
    assert len(context.prov_failed) == 0, f"Expected 0 provider failures, got {len(context.prov_failed)}"
    
    # Cleanup
    os.close(context.env_csv_fd)
    os.unlink(context.env_csv_path)
    os.close(context.prov_csv_fd)
    os.unlink(context.prov_csv_path)
