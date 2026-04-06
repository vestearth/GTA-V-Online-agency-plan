#!/usr/bin/env python3
"""Aggregate structured schema v2 specialist outputs into Lester's report."""

from __future__ import annotations

import argparse
from collections import defaultdict

from schema_v2_runtime import (
    REPORTS_DIR,
    STRUCTURED_DIR,
    build_report_payload,
    dump_json,
    load_json,
    load_weekly,
    week_label,
)


OUT_MD = REPORTS_DIR / "report_lester_week_sample.md"
OUT_JSON = STRUCTURED_DIR / "lester_report.json"


def load_structured_reports():
    if not STRUCTURED_DIR.exists():
        return []
    reports = []
    for path in sorted(STRUCTURED_DIR.glob("*.json")):
        if path.name == OUT_JSON.name:
            continue
        reports.append(load_json(path))
    return reports


def build_consensus(reports):
    grouped = defaultdict(list)
    for report in reports:
        for rec in report.get("top_recommendations", []):
            grouped[rec["target_id"]].append(
                {
                    "agent": report.get("agent"),
                    "action": rec.get("action"),
                    "reason": rec.get("reason"),
                }
            )

    consensus = []
    divergence = []
    for target_id, positions in grouped.items():
        actions = {position["action"] for position in positions}
        if len(actions) == 1 and len(positions) >= 2:
            consensus.append(
                {
                    "target_id": target_id,
                    "agents": [position["agent"] for position in positions],
                    "action": next(iter(actions)),
                    "confidence": "high" if len(positions) >= 3 else "medium",
                }
            )
        elif len(actions) > 1:
            divergence.append({"target_id": target_id, "positions": positions})
    return consensus, divergence


def generate_report(payload):
    reports = load_structured_reports()
    warnings = []
    insufficient = []
    if not reports:
        insufficient.append("No structured specialist reports found. Generate agent reports first.")

    for report in reports:
        for item in report.get("warnings", []):
            warnings.append(f"{report.get('agent')}: {item}")
        for item in report.get("insufficient_data", []):
            insufficient.append(f"{report.get('agent')}: {item}")

    consensus, divergence = build_consensus(reports)
    priority_actions = []
    if consensus:
        for item in consensus[:5]:
            priority_actions.append(
                {
                    "target_id": item["target_id"],
                    "action": item["action"],
                    "reason": f"Agreed by {', '.join(item['agents'])}",
                    "confidence": item["confidence"],
                }
            )
    else:
        for report in reports[:3]:
            if report.get("top_recommendations"):
                priority_actions.append(report["top_recommendations"][0])

    summary = "Use specialist consensus to narrow the week down to the few actions that multiple agents support."
    report_payload = build_report_payload(
        "lester",
        payload,
        summary,
        priority_actions,
        warnings=warnings[:10],
        insufficient_data=insufficient[:10],
        extra={
            "included_agents": [report.get("agent") for report in reports],
            "consensus_targets": consensus,
            "divergence_targets": divergence,
        },
    )

    lines = [
        f"# Lester Consolidated Weekly Report — {week_label(payload)}",
        "",
        "## Executive Summary",
        f"- Included agents: {', '.join(report_payload.get('included_agents', [])) or 'none'}",
        f"- Consensus targets: {len(consensus)}",
        f"- Divergence targets: {len(divergence)}",
        "",
        "## Priority Actions",
    ]
    if priority_actions:
        for item in priority_actions:
            lines.append(f"- {item['target_id']} — {item['action']} — {item['reason']}")
    else:
        lines.append("- No priority actions available yet.")

    lines.extend(["", "## Warnings"])
    if warnings:
        for item in warnings[:10]:
            lines.append(f"- {item}")
    else:
        lines.append("- No warnings surfaced by the available structured reports.")

    if divergence:
        lines.extend(["", "## Divergence"])
        for item in divergence[:5]:
            positions = ", ".join(f"{entry['agent']}={entry['action']}" for entry in item["positions"])
            lines.append(f"- {item['target_id']} — {positions}")

    if insufficient:
        lines.extend(["", "## Insufficient Data"])
        for item in insufficient[:10]:
            lines.append(f"- {item}")

    lines.extend(["", "---", "Lester (Master Coordinator) — schema v2 structured aggregation report."])
    return report_payload, lines


def main():
    parser = argparse.ArgumentParser(description="Generate Lester report from structured schema v2 specialist reports.")
    parser.add_argument("--weekly", help="Path to schema v2 JSON", default=None)
    args = parser.parse_args()
    _, payload = load_weekly(args.weekly)
    report_payload, lines = generate_report(payload)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    STRUCTURED_DIR.mkdir(parents=True, exist_ok=True)
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    dump_json(OUT_JSON, report_payload)
    print(f"Lester report written to {OUT_MD}")
    print(f"Lester structured report written to {OUT_JSON}")


if __name__ == "__main__":
    main()
