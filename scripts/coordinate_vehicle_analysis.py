#!/usr/bin/env python3
"""Coordinate Franklin and Lamar using structured schema v2 reports."""

from __future__ import annotations

import argparse
import subprocess

from schema_v2_runtime import REPORTS_DIR, STRUCTURED_DIR, load_json, load_weekly


FRANKLIN_JSON = STRUCTURED_DIR / "franklin_report.json"
LAMAR_JSON = STRUCTURED_DIR / "lamar_report.json"
OUT = REPORTS_DIR / "vehicle_consultation.md"


def run_generators(weekly_path):
    subprocess.run(["python3", str(REPORTS_DIR.parent / "scripts" / "generate_franklin_report.py"), "--weekly", str(weekly_path)], check=True)
    subprocess.run(["python3", str(REPORTS_DIR.parent / "scripts" / "generate_lamar_report.py"), "--weekly", str(weekly_path)], check=True)


def load_targets(path):
    payload = load_json(path) if path.exists() else {}
    return {item["target_id"]: item for item in payload.get("top_recommendations", [])}


def main():
    parser = argparse.ArgumentParser(description="Coordinate Franklin and Lamar on schema v2 weekly input.")
    parser.add_argument("--weekly", help="Path to schema v2 JSON", default=None)
    args = parser.parse_args()

    weekly_path, weekly_payload = load_weekly(args.weekly)
    run_generators(weekly_path)

    franklin = load_targets(FRANKLIN_JSON)
    lamar = load_targets(LAMAR_JSON)

    overlap = sorted(set(franklin) & set(lamar))
    franklin_only = sorted(set(franklin) - set(lamar))
    lamar_only = sorted(set(lamar) - set(franklin))

    lines = [
        f"# Vehicle Consultation — {weekly_payload.get('week', {}).get('label')}",
        "",
        "## Summary",
        f"- Franklin targets: {len(franklin)}",
        f"- Lamar targets: {len(lamar)}",
        f"- Overlap targets: {len(overlap)}",
    ]

    if overlap:
        lines.extend(["", "## Shared Priorities"])
        for target_id in overlap:
            lines.append(
                f"- {target_id} — Franklin: {franklin[target_id]['action']} | Lamar: {lamar[target_id]['action']}"
            )

    if franklin_only:
        lines.extend(["", "## Franklin-Only Targets"])
        for target_id in franklin_only:
            lines.append(f"- {target_id} — {franklin[target_id]['reason']}")

    if lamar_only:
        lines.extend(["", "## Lamar-Only Targets"])
        for target_id in lamar_only:
            lines.append(f"- {target_id} — {lamar[target_id]['reason']}")

    lines.extend(["", "---", "Vehicle consultation generated from structured schema v2 reports."])
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Consultation written to {OUT}")


if __name__ == "__main__":
    main()
