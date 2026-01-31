#!/usr/bin/env python3
"""
VictoriaLogs Importer (streaming version)

Imports logs.jsonl to VictoriaLogs with streaming to avoid memory issues.

Usage:
    python import_to_victorialogs.py logs.jsonl --workers 24
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict
from queue import Queue
from threading import Thread, Lock
import urllib.request
import urllib.error
import time


def transform_log(log: Dict) -> Dict:
    """Transform our log format to VictoriaLogs format."""
    release_id = log.get("release_id", "")
    parts = release_id.split(":")

    vl_log = {
        "_time": log["timestamp"],
        "_msg": log["message"],
        "level": log["level"],
        "service": log["service"],
        "stack": log["stack"],
        "action": log["action"],
        "success": str(log["success"]).lower(),
    }

    if log.get("user_id"):
        vl_log["user_id"] = log["user_id"]
    if log.get("request_id"):
        vl_log["request_id"] = log["request_id"]
    if log.get("target_user_id"):
        vl_log["target_user_id"] = log["target_user_id"]
    if log.get("object_type"):
        vl_log["object_type"] = log["object_type"]
    if log.get("object_id"):
        vl_log["object_id"] = log["object_id"]
    if log.get("error_code"):
        vl_log["error_code"] = log["error_code"]
    if log.get("error_message"):
        vl_log["error_message"] = log["error_message"]
    if log.get("error_source"):
        vl_log["error_source"] = log["error_source"]
    if log.get("error_type"):
        vl_log["error_type"] = log["error_type"]

    # Trace/span fields for distributed tracing
    if log.get("trace_id"):
        vl_log["trace_id"] = log["trace_id"]
    if log.get("span_id"):
        vl_log["span_id"] = log["span_id"]
    if log.get("parent_span_id"):
        vl_log["parent_span_id"] = log["parent_span_id"]

    if len(parts) >= 12:
        environment, provider, account, region, partition, target_type, target, application, stack, service, tag, release = parts[:12]

        # Atomic fields (no hierarchy)
        vl_log["environment"] = environment
        vl_log["account"] = account
        vl_log["region"] = region
        vl_log["target_type"] = target_type
        vl_log["application"] = application
        vl_log["tag"] = tag

        # Hierarchical fields using composite values (no _id suffix)
        vl_log["provider"] = f"{environment}:{provider}:{account}"
        vl_log["partition"] = f"{environment}:{provider}:{account}:{region}:{partition}"
        vl_log["deployment_target"] = f"{environment}:{provider}:{account}:{region}:{partition}:{target_type}:{target}"
        vl_log["stack"] = f"{application}:{stack}"
        vl_log["service"] = f"{application}:{stack}:{service}"
        vl_log["deployment"] = release_id.rsplit(":", 1)[0]
        vl_log["release"] = release_id
        vl_log["release_num"] = release

    return vl_log


def import_batch(url: str, batch: list) -> tuple:
    """Send a batch of logs to VictoriaLogs. Returns (success_count, error_count)."""
    vl_logs = [transform_log(log) for log in batch]
    payload = "\n".join(json.dumps(log) for log in vl_logs).encode("utf-8")

    req = urllib.request.Request(
        f"{url}/insert/jsonline",
        data=payload,
        headers={"Content-Type": "application/x-ndjson"},
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            return (len(batch), 0)
    except (urllib.error.HTTPError, urllib.error.URLError) as e:
        return (0, len(batch))


def main():
    parser = argparse.ArgumentParser(description="Import logs to VictoriaLogs (streaming)")
    parser.add_argument("input_file", type=str, help="Path to logs.jsonl")
    parser.add_argument("--url", type=str, default="http://localhost:9428",
                        help="VictoriaLogs URL (default: http://localhost:9428)")
    parser.add_argument("--batch-size", type=int, default=10000,
                        help="Logs per batch (default: 10000)")
    parser.add_argument("--workers", type=int, default=8,
                        help="Parallel workers (default: 8)")

    args = parser.parse_args()

    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"Error: {input_path} not found")
        sys.exit(1)

    print(f"Importing logs from {input_path} to {args.url}")
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

    # Bounded queue - only keep workers*2 batches in memory
    batch_queue = Queue(maxsize=args.workers * 2)
    done_reading = False

    def reader_thread():
        """Read file and produce batches."""
        nonlocal total_read, parse_errors, done_reading
        batch = []

        with open(input_path, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue

                try:
                    log = json.loads(line)
                    batch.append(log)
                    total_read += 1
                except json.JSONDecodeError:
                    parse_errors += 1
                    continue

                if len(batch) >= args.batch_size:
                    batch_queue.put(batch)
                    batch = []

                    if total_read % 1000000 == 0:
                        print(f"  Read {total_read:,} logs...")
                        sys.stdout.flush()

        if batch:
            batch_queue.put(batch)

        done_reading = True

    def worker_thread():
        """Consume batches and import them."""
        nonlocal total_imported, total_errors

        while True:
            try:
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
                    print(f"  Imported {total_imported:,} logs ({rate:,.0f}/sec)...")
                    sys.stdout.flush()

            batch_queue.task_done()

    # Start reader
    reader = Thread(target=reader_thread, daemon=True)
    reader.start()

    # Start workers
    workers = [Thread(target=worker_thread, daemon=True) for _ in range(args.workers)]
    for w in workers:
        w.start()

    reader.join()
    batch_queue.join()

    for w in workers:
        w.join(timeout=5)

    elapsed = time.time() - start_time
    rate = total_imported / elapsed if elapsed > 0 else 0

    print("=" * 60)
    print(f"Done in {elapsed:.1f} seconds!")
    print(f"  Total read: {total_read:,}")
    print(f"  Total imported: {total_imported:,}")
    print(f"  Rate: {rate:,.0f} logs/sec")
    if parse_errors:
        print(f"  Parse errors: {parse_errors:,}")
    if total_errors:
        print(f"  Import errors: {total_errors:,}")
    sys.stdout.flush()


if __name__ == "__main__":
    main()
