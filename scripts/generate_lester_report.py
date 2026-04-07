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


def summarize_specialist_references(reports):
    highlights = []
    for report in reports:
        agent = report.get("agent")
        if agent == "tony":
            catalog_size = report.get("reference_catalog_size")
            ranked = report.get("ranked_candidates", [])[:2]
            if catalog_size:
                names = ", ".join(item.get("name", item.get("id", "unknown")) for item in ranked) or "no ranked goods"
                highlights.append(
                    {
                        "agent": "tony",
                        "summary": f"Nightclub catalog loaded with {catalog_size} goods entries; top passive-income targets: {names}.",
                    }
                )
        elif agent == "franklin":
            brand_count = report.get("brand_reference_loaded")
            ranked = report.get("ranked_candidates", [])[:2]
            real_world = []
            for item in ranked:
                for match in item.get("real_world", []):
                    if match not in real_world:
                        real_world.append(match)
            if brand_count:
                suffix = f" Real-world mappings surfaced: {', '.join(real_world)}." if real_world else ""
                highlights.append(
                    {
                        "agent": "franklin",
                        "summary": f"Vehicle reference loaded with {brand_count} brand mappings.{suffix}",
                    }
                )
        elif agent == "agent14":
            if report.get("cayo_reference_loaded"):
                benchmark_lines = []
                for item in report.get("ranked_candidates", [])[:3]:
                    reason = item.get("reason") or ""
                    if "Cayo benchmark" in reason:
                        benchmark_lines.append(item.get("name", item.get("id", "unknown")))
                summary = "Cayo benchmark reference is active"
                if benchmark_lines:
                    summary += f"; surfaced in: {', '.join(benchmark_lines)}"
                highlights.append({"agent": "agent14", "summary": summary + "."})
        elif agent == "michael":
            signals = report.get("reference_signals", {})
            if signals.get("tony_reference_loaded") or signals.get("agent14_cayo_benchmark"):
                parts = []
                if signals.get("tony_catalog_max_value"):
                    parts.append(f"Tony passive-income ceiling {signals['tony_catalog_max_value']}")
                if signals.get("agent14_cayo_benchmark"):
                    benchmark = signals["agent14_cayo_benchmark"]
                    parts.append(
                        f"Cayo benchmark {benchmark.get('player_count')}p leader net {benchmark.get('leader_net')}"
                    )
                highlights.append(
                    {
                        "agent": "michael",
                        "summary": "Michael integrated specialist references: " + "; ".join(parts) + ".",
                    }
                )
    return highlights


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
    specialist_highlights = summarize_specialist_references(reports)
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

    if specialist_highlights:
        summary = "Use specialist consensus and reference-backed agent signals to narrow the week down to the few actions that multiple agents support."
    else:
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
            "specialist_reference_highlights": specialist_highlights,
        },
    )

    lines = [
        f"# Lester Consolidated Weekly Report — {week_label(payload)}",
        "",
        "## Executive Summary",
        f"- Included agents: {', '.join(report_payload.get('included_agents', [])) or 'none'}",
        f"- Consensus targets: {len(consensus)}",
        f"- Divergence targets: {len(divergence)}",
        f"- Specialist reference highlights: {len(specialist_highlights)}",
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

    if specialist_highlights:
        lines.extend(["", "## Specialist Reference Signals"])
        for item in specialist_highlights[:6]:
            lines.append(f"- {item['agent']}: {item['summary']}")

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
