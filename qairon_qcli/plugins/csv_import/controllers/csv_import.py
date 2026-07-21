import csv
import json
import sys
from typing import Dict, List, Any, Tuple

from qairon_qcli.controllers import RestController


class CSVImportError(Exception):
    """Base exception for CSV import errors."""
    pass


class CSVFileNotFoundError(CSVImportError):
    """Raised when CSV file is not found."""
    pass


class CSVParsingError(CSVImportError):
    """Raised when CSV file cannot be parsed."""
    pass


class CSVImportController:
    """Controller for importing CSV data into Qairon resources."""

    def __init__(self):
        self.rest = RestController()

    def import_from_csv(self, resource_type: str, csv_file_path: str, dry_run: bool = False) -> Tuple[List[Dict], List[Dict]]:
        """
        Import data from a CSV file into Qairon resources.
        
        Args:
            resource_type: The type of resource to create (e.g., 'service', 'deployment')
            csv_file_path: Path to the CSV file
            dry_run: If True, validate but don't create resources
            
        Returns:
            Tuple of (successful_imports, failed_imports)
        """
        successful_imports = []
        failed_imports = []
        
        try:
            with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                
                if not reader.fieldnames:
                    raise CSVParsingError("CSV file is empty or has no headers")
                
                for row_num, row in enumerate(reader, start=2):  # start=2 because row 1 is headers
                    # Skip empty rows
                    if not any(row.values()):
                        continue
                    
                    # Clean up the row data (remove empty strings, strip whitespace)
                    cleaned_row = self._clean_row(row)
                    
                    if not cleaned_row:
                        continue
                    
                    # Prepare the resource data
                    resource_data = {
                        'resource': resource_type,
                        **cleaned_row
                    }
                    
                    # Attempt to create the resource
                    if not dry_run:
                        try:
                            response = self.rest.create_resource(resource_data)
                            if response.status_code in [200, 201]:
                                response_data = response.json()
                                if 'data' in response_data:
                                    successful_imports.append({
                                        'row': row_num,
                                        'data': response_data['data']
                                    })
                                elif 'errors' in response_data:
                                    failed_imports.append({
                                        'row': row_num,
                                        'input': cleaned_row,
                                        'error': response_data['errors']
                                    })
                                else:
                                    successful_imports.append({
                                        'row': row_num,
                                        'data': response_data
                                    })
                            else:
                                failed_imports.append({
                                    'row': row_num,
                                    'input': cleaned_row,
                                    'error': f"HTTP {response.status_code}: {response.text}"
                                })
                        except Exception as e:
                            failed_imports.append({
                                'row': row_num,
                                'input': cleaned_row,
                                'error': str(e)
                            })
                    else:
                        # Dry run - just validate the data structure
                        successful_imports.append({
                            'row': row_num,
                            'data': resource_data
                        })
                        
        except FileNotFoundError:
            raise CSVFileNotFoundError(f"CSV file not found: {csv_file_path}")
        except csv.Error as e:
            raise CSVParsingError(f"Error reading CSV file: {e}")
            
        return successful_imports, failed_imports

    def _clean_row(self, row: Dict[str, str]) -> Dict[str, Any]:
        """
        Clean and prepare a CSV row for import.
        
        - Remove empty values
        - Strip whitespace
        - Parse JSON fields (if they start with { or [)
        - Validate JSON size to prevent memory issues
        
        Args:
            row: Raw CSV row as a dictionary
            
        Returns:
            Cleaned dictionary ready for API submission
        """
        cleaned = {}
        max_json_size = 1024 * 1024  # 1MB limit for JSON fields
        
        for key, value in row.items():
            # Skip empty values
            if value is None or value == '':
                continue
            
            # Strip whitespace
            key = key.strip()
            value = value.strip()
            
            # Try to parse JSON values
            if value.startswith('{') or value.startswith('['):
                # Check JSON size before parsing
                if len(value) > max_json_size:
                    # Don't parse, keep as string but log a warning
                    print(f"Warning: JSON value for '{key}' exceeds size limit ({len(value)} bytes), treating as string", file=sys.stderr)
                else:
                    try:
                        value = json.loads(value)
                    except json.JSONDecodeError:
                        # If JSON parsing fails, keep as string
                        pass
            
            cleaned[key] = value
            
        return cleaned

    def print_import_summary(self, successful_imports: List[Dict], failed_imports: List[Dict], dry_run: bool = False):
        """
        Print a summary of the import operation.
        
        Args:
            successful_imports: List of successfully imported resources
            failed_imports: List of failed imports with error details
            dry_run: Whether this was a dry run
        """
        mode = "Dry run" if dry_run else "Import"
        
        print(f"\n{mode} Summary:")
        print(f"{'=' * 50}")
        print(f"Total successful: {len(successful_imports)}")
        print(f"Total failed: {len(failed_imports)}")
        
        if failed_imports:
            print(f"\nFailed imports:")
            for failure in failed_imports:
                print(f"  Row {failure['row']}: {failure['error']}")
                if 'input' in failure:
                    print(f"    Input: {failure['input']}")
        
        if dry_run and successful_imports:
            print(f"\nDry run - no resources were created")
            print(f"Validated {len(successful_imports)} rows successfully")
