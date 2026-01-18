from qairon_qcli.plugins.csv_import.controllers import CSVImportController

COMMANDS = dict(
    import_csv=[
        {'resource_type': {'args': {'help': 'Type of resource to import (e.g., service, deployment, network)'}}},
        {'csv_file': {'args': {'help': 'Path to the CSV file to import'}}},
        {'--dry-run': {'args': {'dest': 'dry_run', 'action': 'store_true', 'default': False, 
                                 'help': 'Validate CSV without creating resources'}}}
    ]
)


def import_csv(resource_type, csv_file, dry_run=False, **kwargs):
    """
    Import resources from a CSV file into Qairon.
    
    The CSV file should have column headers matching the field names for the resource type.
    For example, for services: id, stack_id, defaults (as JSON)
    
    Args:
        resource_type: Type of resource to import (e.g., 'service', 'deployment')
        csv_file: Path to CSV file
        dry_run: If True, validate but don't create resources
    """
    controller = CSVImportController()
    
    print(f"Importing {resource_type} resources from {csv_file}...")
    if dry_run:
        print("DRY RUN MODE - No resources will be created")
    
    successful, failed = controller.import_from_csv(resource_type, csv_file, dry_run)
    controller.print_import_summary(successful, failed, dry_run)
    
    # Exit with error code if there were failures
    if failed:
        exit(1)
