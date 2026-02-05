# CSV Import for Qairon

## Overview

The CSV import plugin allows you to bulk import resources into Qairon from CSV files. This is particularly useful for:
- Migrating existing infrastructure data from spreadsheets
- Bulk creation of resources
- Initial system setup and bootstrapping

## Installation

The CSV import functionality is included as a plugin in qcli. No additional installation is required beyond the standard Qairon setup.

## Usage

### Basic Command

```bash
qcli csv_import import_csv <resource_type> <csv_file>
```

### Dry Run Mode

Validate your CSV file without creating resources:

```bash
qcli csv_import import_csv <resource_type> <csv_file> --dry-run
```

## CSV File Format

### General Requirements

1. **Header Row**: The first row must contain column headers matching the field names for the resource type
2. **Field Names**: Column headers should match the exact field names expected by the Qairon API
3. **Encoding**: CSV files should be UTF-8 encoded
4. **Empty Rows**: Empty rows are automatically skipped

### Field Types

- **Simple Fields**: Plain text values (strings, numbers)
- **JSON Fields**: Complex fields like `defaults` should be valid JSON strings
  - Example: `{"key": "value", "nested": {"data": 123}}`
- **Empty Values**: Empty cells are ignored (fields are omitted from the request)

## Examples

### Example 1: Importing Applications

**CSV File** (`applications.csv`):
```csv
id,defaults
ecommerce,{}
platform,{"team": "infrastructure", "criticality": "high"}
analytics,{"team": "data"}
```

**Command**:
```bash
qcli csv_import import_csv application applications.csv
```

### Example 2: Importing Stacks

**CSV File** (`stacks.csv`):
```csv
id,application_id,defaults
payments,ecommerce,{"priority": "high"}
checkout,ecommerce,{}
api-gateway,platform,{"replicas": 3}
```

**Command**:
```bash
qcli csv_import import_csv stack stacks.csv
```

### Example 3: Importing Services

**CSV File** (`services.csv`):
```csv
id,stack_id,defaults
payment-processor,ecommerce:payments,{"language": "go"}
order-service,ecommerce:checkout,{"language": "python"}
auth-service,platform:api-gateway,{"language": "rust"}
```

**Command**:
```bash
qcli csv_import import_csv service services.csv
```

### Example 4: Importing Networks

**CSV File** (`networks.csv`):
```csv
partition_id,name,cidr,defaults
prod:aws:123456789012:us-east-1:us-east-1a,main-vpc,10.0.0.0/16,{}
prod:aws:123456789012:us-west-2:us-west-2a,backup-vpc,10.1.0.0/16,{"purpose": "disaster-recovery"}
```

**Command**:
```bash
qcli csv_import import_csv network networks.csv
```

## Resource Types

The CSV import plugin supports all Qairon resource types. Common examples include:

- `application` - Applications
- `stack` - Stacks within applications
- `service` - Services within stacks
- `deployment` - Deployments of services
- `deployment_target` - Where deployments run
- `network` - Networks
- `fleet` - Compute fleets
- `build` - Build records
- `release` - Release records
- `environment` - Environments (prod, staging, etc.)
- `provider` - Cloud providers
- `region` - Provider regions
- `partition` - Availability zones/data centers

For a complete list of resource types and their required fields, refer to the Qairon API documentation or run:
```bash
qcli <resource_type> create --help
```

## Best Practices

### 1. Start with a Dry Run

Always validate your CSV file first:
```bash
qcli csv_import import_csv application applications.csv --dry-run
```

### 2. Import in Hierarchical Order

Respect the dependency order when importing related resources:

1. Base infrastructure (environments, providers, regions, partitions)
2. Applications and stacks
3. Services
4. Deployment targets
5. Deployments
6. Configurations

### 3. Handle JSON Fields Carefully

For complex fields like `defaults`, ensure valid JSON:
```csv
id,defaults
app1,{}
app2,{"key": "value"}
```

**Note**: Quotes inside JSON strings must be properly escaped in CSV format.

### 4. Use Descriptive IDs

Since IDs are hierarchical in Qairon, use clear, descriptive names:
```csv
id,stack_id
payment-processor,ecommerce:payments
```

### 5. Keep CSV Files in Version Control

Store your CSV files in git alongside your infrastructure-as-code:
```
infrastructure/
├── csv/
│   ├── applications.csv
│   ├── stacks.csv
│   └── services.csv
└── terraform/
```

## Error Handling

### Import Summary

After import, a summary is displayed:
```
Import Summary:
==================================================
Total successful: 5
Total failed: 2

Failed imports:
  Row 3: HTTP 400: Field 'stack_id' is required
    Input: {'id': 'test-service'}
  Row 7: HTTP 409: Resource already exists
    Input: {'id': 'duplicate-app'}
```

### Exit Codes

- `0` - All imports successful
- `1` - One or more imports failed

### Common Errors

1. **Missing Required Fields**: Ensure all required fields are present in CSV
2. **Invalid JSON**: Check JSON syntax in complex fields
3. **Duplicate Resources**: Resource IDs must be unique
4. **Invalid References**: Parent resources (e.g., stack_id) must exist before importing children

## Migration from Spreadsheets

If you're migrating from an existing spreadsheet:

1. **Export to CSV**: Use your spreadsheet tool's "Export to CSV" function
2. **Map Column Names**: Rename columns to match Qairon field names
3. **Convert Complex Data**: Format complex fields as JSON strings
4. **Test Import**: Use `--dry-run` to validate
5. **Import**: Run the actual import
6. **Verify**: Use `qcli <resource> list` to verify imported data

## Troubleshooting

### Issue: "CSV file not found"
- Check the file path is correct
- Use absolute paths or ensure you're in the correct directory

### Issue: "Field 'X' is required"
- Add the missing column to your CSV
- Check the Qairon schema for required fields

### Issue: "Invalid JSON in field 'defaults'"
- Validate JSON syntax (use a JSON validator)
- Ensure proper CSV escaping of quotes
- Consider using `{}` for empty defaults

### Issue: "Resource already exists"
- Check if resources were partially imported
- Use unique IDs or delete existing resources first
- Consider using update operations instead

## Advanced Usage

### Programmatic Import

You can also use the CSV import functionality programmatically:

```python
from qairon_qcli.plugins.csv_import.controllers import CSVImportController

controller = CSVImportController()
successful, failed = controller.import_from_csv(
    resource_type='application',
    csv_file_path='applications.csv',
    dry_run=False
)

controller.print_import_summary(successful, failed)
```

## Limitations

1. **No Update Support**: Currently only supports creating new resources, not updating existing ones
2. **No Relationship Management**: Many-to-many relationships (like service repos) must be set after import
3. **Single Resource Type**: Each CSV file can only contain one resource type
4. **Sequential Processing**: Resources are created one at a time (not batched)
5. **JSON Detection**: Fields that start with `{` or `[` are automatically treated as JSON. For literal strings starting with these characters, they will be parsed as JSON (or kept as string if invalid)

## Future Enhancements

Potential future improvements:
- Support for updating existing resources
- Batch processing for better performance
- Relationship management in CSV
- Multi-resource-type CSV files
- Export to CSV functionality
- CSV validation without API calls
- File size limits for very large CSV files
- Configuration to specify which fields contain JSON
- Use of Python logging module for better log control
- Input parameter validation
