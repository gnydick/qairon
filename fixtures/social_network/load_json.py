#!/usr/bin/env python3
"""Simple JSON fixture loader using requests."""

import json
import os
import sys
import requests
from pathlib import Path

API_URL = os.getenv("QAIRON_ENDPOINT", "http://127.0.0.1:5001") + "/api/rest/v1"
JSON_DIR = Path(__file__).parent / "json"

RESOURCES = [
    "environment",
    "provider_type",
    "deployment_target_type",
    "allocation_type",
    "repo_type",
    "language",
    "provider",
    "region",
    "zone",
    "partition",
    "network",
    "subnet",
    "fleet_type",
    "deployment_target",
    "fleet",
    "capacity",
    "repo",
    "application",
    "stack",
    "service",
    "proc",
    "config_template",
    "build",
    "deployment",
    "deployment_proc",
    "release",
    "allocation",
    "build_artifact",
    "release_artifact",
    "deployment_config",
    "service_config",
    "stack_config",
    # Many-to-many relationships (handled specially)
    "services_repos",
    "deployments_zones",
    "subnets_fleets",
    "deployment_targets_fleets",
]

# Many-to-many mapping: resource_name -> (owner_resource, owner_id_field, collection_name, related_type, related_id_field)
MANY_TO_MANY = {
    "services_repos": ("service", "service_id", "repos", "repo", "repo_id"),
    "deployments_zones": ("deployment", "deployment_id", "zones", "zone", "zone_id"),
    "subnets_fleets": ("subnet", "subnet_id", "fleets", "fleet", "fleet_id"),
    "deployment_targets_fleets": ("deployment_target", "deployment_target_id", "fleets", "fleet", "fleet_id"),
}

session = requests.Session()
session.headers.update({
    'Content-Type': 'application/vnd.api+json',
    'Accept': 'application/vnd.api+json'
})

def add_to_collection(owner_res, owner_id, collection_name, related_type, item_id):
    """Add a single item to a collection (like qcli add_to_collection)."""
    # GET existing collection
    url = f"{API_URL}/{owner_res}/{owner_id}/{collection_name}"
    resp = session.get(url)

    if resp.status_code != 200:
        return False, f"GET failed: {resp.status_code}"

    # Build new collection with existing items + new item
    existing = resp.json().get('data', [])
    collection = {'data': []}
    for item in existing:
        collection['data'].append({'id': item['id'], 'type': related_type})

    # Check if item already exists
    if any(item['id'] == item_id for item in existing):
        return True, "duplicate"

    # Add new item
    collection['data'].append({'type': related_type, 'id': item_id})

    # PATCH to /{resource}/{id}/relationships/{collection}
    rel_url = f"{API_URL}/{owner_res}/{owner_id}/relationships/{collection_name}"
    resp = session.patch(rel_url, json=collection)
    if resp.status_code == 204:
        return True, "success"
    else:
        return False, f"PATCH failed: {resp.status_code} - {resp.text[:100]}"

def load_many_to_many(resource, records):
    """Load many-to-many relationships one item at a time."""
    owner_res, owner_id_field, collection_name, related_type, related_id_field = MANY_TO_MANY[resource]

    success = errors = duplicates = 0
    for record in records:
        attrs = record['data']['attributes']
        owner_id = attrs[owner_id_field]
        item_id = attrs[related_id_field]

        ok, status = add_to_collection(owner_res, owner_id, collection_name, related_type, item_id)
        if ok:
            if status == "duplicate":
                duplicates += 1
            else:
                success += 1
        else:
            errors += 1
            if errors <= 3:
                print(f"\n  ERROR: {status}")

    return success, duplicates, errors

def main():
    from_idx = 0
    to_idx = len(RESOURCES)

    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == '--from':
            from_idx = int(args[i + 1]) - 1
            i += 2
        elif args[i] == '--to':
            to_idx = int(args[i + 1])
            i += 2
        else:
            i += 1

    print("=" * 50)
    print("JSON Fixture Loader")
    print("=" * 50)
    print(f"API: {API_URL}")
    print()

    total_success = 0
    total_errors = 0
    total_duplicates = 0

    for idx, resource in enumerate(RESOURCES[from_idx:to_idx], start=from_idx + 1):
        json_file = JSON_DIR / f"{resource}.json"
        if not json_file.exists():
            print(f"[{idx:02d}] {resource} - SKIPPED")
            continue

        with open(json_file) as f:
            records = json.load(f)

        print(f"[{idx:02d}] Loading {resource} ({len(records)} records)...", end=" ", flush=True)

        # Handle many-to-many relationships differently
        if resource in MANY_TO_MANY:
            success, duplicates, errors = load_many_to_many(resource, records)
        else:
            success = errors = duplicates = 0
            for record in records:
                resp = session.post(f"{API_URL}/{resource}", json=record)
                if resp.status_code == 201:
                    success += 1
                elif resp.status_code == 400 and 'UniqueViolation' in resp.text:
                    duplicates += 1
                else:
                    errors += 1
                    if errors <= 3:
                        print(f"\n  ERROR: {resp.status_code} - {resp.text[:150]}")

        total_success += success
        total_errors += errors
        total_duplicates += duplicates
        print(f"OK ({success} new, {duplicates} dup, {errors} err)")

    print()
    print("=" * 50)
    print(f"Complete! Success: {total_success}, Duplicates: {total_duplicates}, Errors: {total_errors}")
    print("=" * 50)

if __name__ == "__main__":
    main()
