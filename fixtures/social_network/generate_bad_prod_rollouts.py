#!/usr/bin/env python3
"""Generate bad_prod_rollouts.md from deployment_schedule.json.

Reads the serialized QaironModel (deployment_schedule.json), finds all bad
production deployment windows (error_rate_boost >= 0.08, env == "prod"),
groups them by (stack, service, release_num), and writes a markdown file
matching the format of bad_prod_rollouts.md.

Usage:
    python generate_bad_prod_rollouts.py <deployment_schedule.json> [--output bad_prod_rollouts.md]
"""

import argparse
import json
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List


def generate_bad_prod_rollouts(schedule_path: Path, output_path: Path) -> int:
    """Generate bad_prod_rollouts.md from deployment_schedule.json.

    Returns the number of bad rollouts found.
    """
    with open(schedule_path) as f:
        data = json.load(f)

    windows_by_dep = data.get("windows", {})

    # Collect all bad prod windows
    bad_windows = []
    for dep_id, window_list in windows_by_dep.items():
        for w in window_list:
            if w["env"] == "prod" and w["error_rate_boost"] >= 0.08:
                bad_windows.append(w)

    if not bad_windows:
        output_path.write_text("# Bad Production Rollouts\n\nNo bad production rollouts found.\n")
        return 0

    # Group by (stack, service, release_num) — each group is one "bad rollout"
    groups: Dict[tuple, List[dict]] = defaultdict(list)
    for w in bad_windows:
        release_num = w["release_id"].rsplit(":", 1)[-1]
        key = (w["stack"], w["service"], release_num)
        groups[key].append(w)

    # Sort groups chronologically by earliest window start_time
    sorted_groups = sorted(
        groups.items(),
        key=lambda item: min(w["start_time"] for w in item[1])
    )

    lines = []
    lines.append("# Bad Production Rollouts")
    lines.append("")
    lines.append("Extracted from `deployment_schedule.json`. Each entry is a bad release "
                 "(error_rate_boost > 8%) rolling across prod regions.")
    lines.append("")
    lines.append("Good demo candidates are services with downstream dependents — "
                 "**feed:timeline**, **content:posts**, **content:media**, and "
                 "**messaging:realtime** — since their failures cascade to callers "
                 "and show up across multiple dashboards.")
    lines.append("")

    # Summary table
    lines.append("## Summary")
    lines.append("")
    lines.append("| # | Service | Release | Date | Avg Error Boost | Avg Latency |")
    lines.append("|---|---------|---------|------|-----------------|-------------|")

    for idx, ((stack, service, release_num), windows) in enumerate(sorted_groups, 1):
        earliest = min(w["start_time"] for w in windows)
        date_str = datetime.fromisoformat(earliest).strftime("%Y-%m-%d")
        avg_boost = sum(w["error_rate_boost"] for w in windows) / len(windows)
        avg_latency = sum(w["latency_multiplier"] for w in windows) / len(windows)
        lines.append(
            f"| {idx} | {stack}:{service} | {release_num} | {date_str} "
            f"| {avg_boost:.0%} | {avg_latency:.1f}x |"
        )

    lines.append("")

    # Detail sections
    lines.append("## Detail")
    lines.append("")

    for idx, ((stack, service, release_num), windows) in enumerate(sorted_groups, 1):
        # Sort windows by start_time
        sorted_windows = sorted(windows, key=lambda w: w["start_time"])
        earliest = sorted_windows[0]["start_time"]
        latest_end = max(w["end_time"] for w in sorted_windows)
        date_str = datetime.fromisoformat(earliest).strftime("%Y-%m-%d")

        earliest_fmt = datetime.fromisoformat(earliest).strftime("%Y-%m-%dT%H:%M")
        latest_fmt = datetime.fromisoformat(latest_end).strftime("%Y-%m-%dT%H:%M")

        lines.append(f"### {idx}. social:{stack}:{service} release {release_num} ({date_str})")
        lines.append("")
        lines.append(f"Time range: {earliest_fmt} to {latest_fmt}")
        lines.append("")
        lines.append("| Region | Start | End | Error Boost | Latency |")
        lines.append("|--------|-------|-----|-------------|---------|")

        for w in sorted_windows:
            region = w["region"]
            start_fmt = datetime.fromisoformat(w["start_time"]).strftime("%Y-%m-%dT%H:%M")
            end_fmt = datetime.fromisoformat(w["end_time"]).strftime("%Y-%m-%dT%H:%M")
            boost_pct = f"{w['error_rate_boost']:.0%}"
            latency = f"{w['latency_multiplier']:.1f}x"
            lines.append(f"| {region} | {start_fmt} | {end_fmt} | {boost_pct} | {latency} |")

        lines.append("")

    output_path.write_text("\n".join(lines))
    return len(sorted_groups)


def main():
    parser = argparse.ArgumentParser(description="Generate bad_prod_rollouts.md from deployment_schedule.json")
    parser.add_argument("schedule", type=Path, help="Path to deployment_schedule.json")
    parser.add_argument("--output", type=Path, default=None,
                        help="Output path (default: bad_prod_rollouts.md in same directory)")
    args = parser.parse_args()

    if not args.schedule.exists():
        print(f"Error: {args.schedule} not found", file=sys.stderr)
        sys.exit(1)

    output = args.output or args.schedule.parent / "bad_prod_rollouts.md"
    count = generate_bad_prod_rollouts(args.schedule, output)
    print(f"  Wrote {count} bad prod rollouts to {output}")


if __name__ == "__main__":
    main()
