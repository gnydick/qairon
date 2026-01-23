#!/usr/bin/env python3
"""
Import metrics from JSONL to VictoriaMetrics.

Usage:
    python import_to_victoriametrics.py metrics.jsonl [--url http://localhost:8428] [--workers 8]

VictoriaMetrics must be running. Start with:
    docker run -d --cpus=12 -p 8428:8428 -v vm-data:/victoria-metrics-data victoriametrics/victoria-metrics -retentionPeriod=2y
"""

import argparse
import json
import sys
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from threading import Lock


def transform_metric(line: dict) -> dict:
    """Transform our metric format to VictoriaMetrics JSON import format.

    Input:  {"metric": "name", "ts": 123.45, "value": 1.0, "tags": {"k": "v"}}
    Output: {"metric": {"__name__": "name", "k": "v"}, "values": [1.0], "timestamps": [123450]}
    """
    metric_labels = {"__name__": line["metric"]}
    metric_labels.update(line["tags"])

    # Split release_id into composite IDs and single-word filter tags
    # release_id format: {env}:{provider}:{account}:{region}:{partition}:{target_type}:{target}:{app}:{stack}:{service}:{tag}:{release_num}
    if "release_id" in metric_labels:
        release_id = metric_labels["release_id"]
        parts = release_id.split(":")

        if len(parts) >= 12:
            env, provider, account, region, partition, target_type, target, app, stack, service, tag = parts[:11]

            # Single-word tags for global filtering
            metric_labels["environment"] = env
            metric_labels["provider"] = provider
            metric_labels["account"] = account
            metric_labels["region"] = region

            # Composite IDs (all include environment)
            metric_labels["provider_id"] = f"{env}:{provider}:{account}"
            metric_labels["region_id"] = f"{env}:{provider}:{account}:{region}"
            metric_labels["partition_id"] = f"{env}:{provider}:{account}:{region}:{partition}"
            metric_labels["target_id"] = f"{env}:{provider}:{account}:{region}:{partition}:{target_type}:{target}"
            metric_labels["service_id"] = f"{app}:{stack}:{service}"
            metric_labels["deployment_id"] = release_id.rsplit(":", 1)[0]

    return {
        "metric": metric_labels,
        "values": [line["value"]],
        "timestamps": [int(line["ts"] * 1000)]  # Convert seconds to milliseconds
    }


def import_batch(url: str, batch: list) -> bool:
    """Send a batch of metrics to VictoriaMetrics."""
    import_url = f"{url}/api/v1/import"

    # VictoriaMetrics expects newline-delimited JSON
    body = "\n".join(json.dumps(m) for m in batch).encode("utf-8")

    req = urllib.request.Request(
        import_url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status == 204
    except urllib.error.HTTPError as e:
        print(f"HTTP error: {e.code} - {e.read().decode()}", file=sys.stderr)
        return False
    except urllib.error.URLError as e:
        print(f"Connection error: {e.reason}", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(description="Import metrics to VictoriaMetrics")
    parser.add_argument("input_file", type=str, help="Path to metrics.jsonl file")
    parser.add_argument("--url", type=str, default="http://localhost:8428",
                        help="VictoriaMetrics URL (default: http://localhost:8428)")
    parser.add_argument("--batch-size", type=int, default=10000,
                        help="Number of metrics per batch (default: 10000)")
    parser.add_argument("--workers", type=int, default=8,
                        help="Number of parallel workers (default: 8)")

    args = parser.parse_args()

    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"Error: File not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    print(f"Importing metrics from {input_path} to {args.url}")
    print(f"Batch size: {args.batch_size}, Workers: {args.workers}")

    # Read and transform all metrics into batches
    print("Reading and transforming metrics...")
    batches = []
    batch = []
    parse_errors = 0

    with open(input_path, "r") as f:
        for i, line in enumerate(f):
            if not line.strip():
                continue

            try:
                metric = json.loads(line)
                transformed = transform_metric(metric)
                batch.append(transformed)
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Error parsing line {i + 1}: {e}", file=sys.stderr)
                parse_errors += 1
                continue

            if len(batch) >= args.batch_size:
                batches.append(batch)
                batch = []

    # Don't forget the last batch
    if batch:
        batches.append(batch)

    total_metrics = sum(len(b) for b in batches)
    print(f"  Prepared {len(batches)} batches ({total_metrics:,} metrics)")

    # Import batches in parallel
    print("Importing batches in parallel...")
    total_imported = 0
    import_errors = 0
    lock = Lock()

    def import_and_track(batch_data):
        nonlocal total_imported, import_errors
        success = import_batch(args.url, batch_data)
        with lock:
            if success:
                total_imported += len(batch_data)
            else:
                import_errors += len(batch_data)
            # Progress update every 10 batches worth
            if total_imported % (args.batch_size * 10) < args.batch_size:
                print(f"  Imported {total_imported:,} metrics...")
        return success

    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = [executor.submit(import_and_track, b) for b in batches]
        for future in as_completed(futures):
            future.result()  # Raise any exceptions

    print(f"\nDone!")
    print(f"  Total imported: {total_imported:,}")
    if parse_errors:
        print(f"  Parse errors: {parse_errors:,}")
    if import_errors:
        print(f"  Import errors: {import_errors:,}")


if __name__ == "__main__":
    main()