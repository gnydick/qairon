#!/usr/bin/env python3
"""
Import metrics from JSONL to VictoriaMetrics (streaming version).

Uses streaming to avoid loading all metrics into memory.

Usage:
    python import_to_victoriametrics.py metrics.jsonl [--url http://localhost:8428] [--workers 24]
"""

import argparse
import json
import sys
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from queue import Queue
from threading import Thread, Lock
import time


def transform_metric(line: dict) -> dict:
    """Transform our metric format to VictoriaMetrics JSON import format."""
    metric_labels = {"__name__": line["metric"]}
    metric_labels.update(line["tags"])

    if "release_id" in metric_labels:
        release_id = metric_labels["release_id"]
        parts = release_id.split(":")

        if len(parts) >= 12:
            environment, provider, account, region, partition, target_type, target, application, stack, service, tag, release = parts[:12]

            # Atomic fields (no hierarchy)
            metric_labels["environment"] = environment
            metric_labels["account"] = account
            metric_labels["target_type"] = target_type
            metric_labels["application"] = application
            metric_labels["tag"] = tag

            # Hierarchical fields using composite values (no _id suffix)
            metric_labels["provider"] = f"{environment}:{provider}:{account}"
            metric_labels["region"] = f"{environment}:{provider}:{account}:{region}"
            metric_labels["partition"] = f"{environment}:{provider}:{account}:{region}:{partition}"
            metric_labels["deployment_target"] = f"{environment}:{provider}:{account}:{region}:{partition}:{target_type}:{target}"
            metric_labels["stack"] = f"{application}:{stack}"
            metric_labels["service"] = f"{application}:{stack}:{service}"
            metric_labels["deployment"] = release_id.rsplit(":", 1)[0]
            metric_labels["release"] = release_id
            metric_labels["release_num"] = release

    return {
        "metric": metric_labels,
        "values": [line["value"]],
        "timestamps": [int(line["ts"] * 1000)]
    }


def import_batch(url: str, batch: list) -> tuple:
    """Send a batch of metrics to VictoriaMetrics. Returns (success_count, error_count)."""
    import_url = f"{url}/api/v1/import"
    body = "\n".join(json.dumps(m) for m in batch).encode("utf-8")

    req = urllib.request.Request(
        import_url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            if resp.status == 204:
                return (len(batch), 0)
            return (0, len(batch))
    except (urllib.error.HTTPError, urllib.error.URLError) as e:
        return (0, len(batch))


def main():
    parser = argparse.ArgumentParser(description="Import metrics to VictoriaMetrics (streaming)")
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
    print("=" * 60)
    sys.stdout.flush()

    # Stats
    total_read = 0
    total_imported = 0
    total_errors = 0
    parse_errors = 0
    lock = Lock()
    start_time = time.time()

    # Use a bounded queue to limit memory - only keep ~workers*2 batches in memory
    batch_queue = Queue(maxsize=args.workers * 2)
    done_reading = False

    def reader_thread():
        """Read file and produce batches."""
        nonlocal total_read, parse_errors, done_reading
        batch = []

        with open(input_path, "r") as f:
            for i, line in enumerate(f):
                if not line.strip():
                    continue

                try:
                    metric = json.loads(line)
                    transformed = transform_metric(metric)
                    batch.append(transformed)
                    total_read += 1
                except (json.JSONDecodeError, KeyError) as e:
                    parse_errors += 1
                    continue

                if len(batch) >= args.batch_size:
                    batch_queue.put(batch)  # Blocks if queue is full
                    batch = []

                    if total_read % 1000000 == 0:
                        print(f"  Read {total_read:,} metrics...")
                        sys.stdout.flush()

        # Last batch
        if batch:
            batch_queue.put(batch)

        done_reading = True

    def worker_thread():
        """Consume batches and import them."""
        nonlocal total_imported, total_errors

        while True:
            try:
                # Try to get a batch, timeout to check if reading is done
                batch = batch_queue.get(timeout=1)
            except:
                if done_reading and batch_queue.empty():
                    break
                continue

            success, errors = import_batch(args.url, batch)

            with lock:
                total_imported += success
                total_errors += errors

                if total_imported % 100000 < args.batch_size:
                    elapsed = time.time() - start_time
                    rate = total_imported / elapsed if elapsed > 0 else 0
                    print(f"  Imported {total_imported:,} metrics ({rate:,.0f}/sec)...")
                    sys.stdout.flush()

            batch_queue.task_done()

    # Start reader thread
    reader = Thread(target=reader_thread, daemon=True)
    reader.start()

    # Start worker threads
    workers = [Thread(target=worker_thread, daemon=True) for _ in range(args.workers)]
    for w in workers:
        w.start()

    # Wait for reader to finish
    reader.join()

    # Wait for all batches to be processed
    batch_queue.join()

    # Signal workers to stop and wait
    for w in workers:
        w.join(timeout=5)

    elapsed = time.time() - start_time
    rate = total_imported / elapsed if elapsed > 0 else 0

    print("=" * 60)
    print(f"Done in {elapsed:.1f} seconds!")
    print(f"  Total read: {total_read:,}")
    print(f"  Total imported: {total_imported:,}")
    print(f"  Rate: {rate:,.0f} metrics/sec")
    if parse_errors:
        print(f"  Parse errors: {parse_errors:,}")
    if total_errors:
        print(f"  Import errors: {total_errors:,}")
    sys.stdout.flush()


if __name__ == "__main__":
    main()
