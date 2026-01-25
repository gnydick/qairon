#!/usr/bin/env python3
"""
Export traces from log files to Tempo via OTLP HTTP.

Reads log files, groups by trace_id, and sends as OTLP traces.

Usage:
    python export_traces_to_tempo.py logs_0.jsonl --tempo-url http://localhost:4318
"""

import argparse
import json
import sys
from pathlib import Path
from collections import defaultdict
from typing import Dict, List
import urllib.request
import urllib.error
import time
from datetime import datetime


def parse_timestamp(ts_str: str) -> int:
    """Convert ISO timestamp to nanoseconds since epoch."""
    dt = datetime.fromisoformat(ts_str.replace('Z', '+00:00'))
    return int(dt.timestamp() * 1_000_000_000)


def logs_to_otlp_traces(logs: List[Dict]) -> Dict:
    """Convert grouped logs to OTLP trace format."""
    # Group by trace_id
    traces = defaultdict(list)
    for log in logs:
        trace_id = log.get("trace_id")
        if trace_id:
            traces[trace_id].append(log)

    resource_spans = []

    for trace_id, spans in traces.items():
        # Group spans by service
        by_service = defaultdict(list)
        for span in spans:
            service_key = f"{span.get('stack', 'unknown')}:{span.get('service', 'unknown')}"
            by_service[service_key].append(span)

        for service_key, service_spans in by_service.items():
            stack, service = service_key.split(':')

            otlp_spans = []
            for span in service_spans:
                start_time = parse_timestamp(span["timestamp"])
                # Estimate duration from latency if available, else 1ms
                duration_ns = int(span.get("latency_ms", 1) * 1_000_000)

                otlp_span = {
                    "traceId": span["trace_id"],
                    "spanId": span["span_id"],
                    "name": span.get("action", "unknown"),
                    "kind": 2 if span.get("parent_span_id") else 1,  # SPAN_KIND_CLIENT : SPAN_KIND_SERVER
                    "startTimeUnixNano": str(start_time),
                    "endTimeUnixNano": str(start_time + duration_ns),
                    "attributes": [
                        {"key": "service.name", "value": {"stringValue": service}},
                        {"key": "stack", "value": {"stringValue": stack}},
                        {"key": "user_id", "value": {"stringValue": span.get("user_id", "")}},
                        {"key": "success", "value": {"boolValue": span.get("success", True)}},
                        {"key": "request_id", "value": {"stringValue": span.get("request_id", "")}},
                    ],
                    "status": {
                        "code": 1 if span.get("success", True) else 2,  # OK : ERROR
                    }
                }

                if span.get("parent_span_id"):
                    otlp_span["parentSpanId"] = span["parent_span_id"]

                if span.get("error_message"):
                    otlp_span["status"]["message"] = span["error_message"]
                    otlp_span["attributes"].append({
                        "key": "error.type",
                        "value": {"stringValue": span.get("error_type", "unknown")}
                    })

                otlp_spans.append(otlp_span)

            resource_spans.append({
                "resource": {
                    "attributes": [
                        {"key": "service.name", "value": {"stringValue": service}},
                        {"key": "service.namespace", "value": {"stringValue": stack}},
                    ]
                },
                "scopeSpans": [{
                    "scope": {"name": "qairon-generator"},
                    "spans": otlp_spans
                }]
            })

    return {"resourceSpans": resource_spans}


def send_to_tempo(tempo_url: str, otlp_data: Dict) -> bool:
    """Send OTLP traces to Tempo."""
    url = f"{tempo_url}/v1/traces"
    payload = json.dumps(otlp_data).encode('utf-8')

    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.status == 200
    except (urllib.error.HTTPError, urllib.error.URLError) as e:
        print(f"Error sending to Tempo: {e}", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(description="Export traces to Tempo")
    parser.add_argument("input_file", type=str, help="Path to logs.jsonl")
    parser.add_argument("--tempo-url", type=str, default="http://localhost:4318",
                        help="Tempo OTLP HTTP URL (default: http://localhost:4318)")
    parser.add_argument("--batch-size", type=int, default=1000,
                        help="Number of logs to process per batch (default: 1000)")
    parser.add_argument("--limit", type=int, default=None,
                        help="Limit number of logs to process (for testing)")
    args = parser.parse_args()

    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"Error: {input_path} not found", file=sys.stderr)
        sys.exit(1)

    print(f"Exporting traces from {input_path} to {args.tempo_url}")
    print(f"Batch size: {args.batch_size}")
    print("=" * 60)

    total_logs = 0
    total_traces = 0
    batch = []
    start_time = time.time()

    with open(input_path) as f:
        for line in f:
            if args.limit and total_logs >= args.limit:
                break

            log = json.loads(line)
            if log.get("trace_id"):  # Only process logs with trace_id
                batch.append(log)
                total_logs += 1

            if len(batch) >= args.batch_size:
                otlp_data = logs_to_otlp_traces(batch)
                trace_count = len(set(log["trace_id"] for log in batch))

                if send_to_tempo(args.tempo_url, otlp_data):
                    total_traces += trace_count
                    elapsed = time.time() - start_time
                    rate = total_logs / elapsed if elapsed > 0 else 0
                    print(f"  Exported {total_logs:,} logs, {total_traces:,} traces ({rate:.0f}/sec)...")
                else:
                    print(f"  Failed to send batch", file=sys.stderr)

                batch = []

    # Send remaining batch
    if batch:
        otlp_data = logs_to_otlp_traces(batch)
        trace_count = len(set(log["trace_id"] for log in batch))
        if send_to_tempo(args.tempo_url, otlp_data):
            total_traces += trace_count

    elapsed = time.time() - start_time
    print("=" * 60)
    print(f"Done in {elapsed:.1f} seconds!")
    print(f"  Total logs: {total_logs:,}")
    print(f"  Total traces: {total_traces:,}")
    print(f"  Rate: {total_logs / elapsed:.0f} logs/sec")


if __name__ == "__main__":
    main()
