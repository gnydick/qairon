#!/usr/bin/env python3
"""Convert TSV fixtures to JSON:API format."""

import argparse
import json
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent

# Define mappings: (filename, resource_type, column_names)
# Column names in order they appear in the TSV file
MAPPINGS = [
    ("01_environments.txt", "environment", ["id"]),
    ("02_provider_types.txt", "provider_type", ["id"]),
    ("03_deployment_target_types.txt", "deployment_target_type", ["id"]),
    ("04_allocation_types.txt", "allocation_type", ["id", "unit"]),
    ("05_repo_types.txt", "repo_type", ["id"]),
    ("06_languages.txt", "language", ["id"]),
    ("07_providers.txt", "provider", ["environment_id", "provider_type_id", "native_id"]),
    ("08_regions.txt", "region", ["provider_id", "name"]),
    ("09_zones.txt", "zone", ["region_id", "name", "native_id"]),
    ("10_partitions.txt", "partition", ["region_id", "name", "native_id"]),
    ("11_networks.txt", "network", ["partition_id", "name", "cidr"]),
    ("12_subnets.txt", "subnet", ["network_id", "name", "cidr", "native_id"]),
    ("13_fleet_types.txt", "fleet_type", ["provider_type_id", "name"]),
    ("14_deployment_targets.txt", "deployment_target", ["partition_id", "deployment_target_type_id", "name"]),
    ("15_fleets.txt", "fleet", ["deployment_target_id", "fleet_type_id", "name"]),
    ("16_capacities.txt", "capacity", ["allocation_type_id", "fleet_id", "value"]),
    ("17_repos.txt", "repo", ["repo_type_id", "name", "url"]),
    ("18_applications.txt", "application", ["id", "defaults"]),
    ("19_stacks.txt", "stack", ["application_id", "name", "defaults"]),
    ("20_services.txt", "service", ["stack_id", "name", "_artifact_name", "defaults"]),
    ("21_procs.txt", "proc", ["service_id", "name", "defaults"]),
    ("22_config_templates.txt", "config_template", ["id", "language_id", "doc"]),
    ("23_deployments.txt", "deployment", ["deployment_target_id", "service_id", "tag", "defaults"]),
    ("24_deployment_procs.txt", "deployment_proc", ["deployment_id", "proc_id", "defaults"]),
    ("25_allocations.txt", "allocation", ["deployment_proc_id", "allocation_type_id", "watermark", "value", "defaults"]),
    ("26_deployment_configs.txt", "deployment_config", ["deployment_id", "config_template_id", "name", "tag", "config", "defaults"]),
    ("27_service_configs.txt", "service_config", ["service_id", "config_template_id", "name", "tag", "config", "defaults"]),
    ("28_stack_configs.txt", "stack_config", ["stack_id", "config_template_id", "name", "tag", "config", "defaults"]),
    # Many-to-many relationships
    ("29_services_repos.txt", "services_repos", ["service_id", "repo_id"]),
    ("30_deployments_zones.txt", "deployments_zones", ["deployment_id", "zone_id"]),
    ("31_subnets_fleets.txt", "subnets_fleets", ["subnet_id", "fleet_id"]),
    ("32_target_fleets.txt", "deployment_targets_fleets", ["deployment_target_id", "fleet_id"]),
]

def convert_value(value, col_name):
    """Convert string value to appropriate type."""
    if not value:
        return None
    if col_name in ('value', 'build_num'):
        try:
            if '.' in value:
                return float(value)
            return int(value)
        except ValueError:
            return value
    return value

def parse_tsv(filepath, columns):
    """Parse TSV file and return list of attribute dicts."""
    records = []
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            cols = line.split('\t')
            attrs = {}
            for i, col_name in enumerate(columns):
                if col_name.startswith('_'):  # Skip columns starting with _
                    continue
                if i < len(cols) and cols[i]:
                    attrs[col_name] = convert_value(cols[i], col_name)

            # Handle tag default
            if 'tag' in columns and 'tag' not in attrs:
                attrs['tag'] = 'default'
            elif 'tag' in attrs and attrs['tag'] is None:
                attrs['tag'] = 'default'

            records.append(attrs)
    return records

def to_jsonapi(resource_type, records):
    """Convert records to JSON:API format."""
    return [
        {
            "data": {
                "type": resource_type,
                "attributes": record
            }
        }
        for record in records
    ]

def main():
    parser = argparse.ArgumentParser(description='Convert TSV fixtures to JSON:API format')
    parser.add_argument('--input-dir', metavar='DIR',
                        default=str(SCRIPT_DIR / "txt"),
                        help='Input directory containing TSV files (default: txt/ subdir)')
    parser.add_argument('--output-dir', metavar='DIR',
                        default=str(SCRIPT_DIR / "json"),
                        help='Output directory for JSON files (default: json/ subdir)')
    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True, parents=True)

    for filename, resource_type, columns in MAPPINGS:
        filepath = input_dir / filename
        if not filepath.exists():
            print(f"Skipping {filename} (not found)")
            continue

        records = parse_tsv(filepath, columns)
        jsonapi_records = to_jsonapi(resource_type, records)

        output_file = output_dir / f"{resource_type}.json"
        with open(output_file, 'w') as f:
            json.dump(jsonapi_records, f, indent=2)

        print(f"Created {output_file.name} with {len(records)} records")

if __name__ == "__main__":
    main()
