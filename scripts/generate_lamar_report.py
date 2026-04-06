#!/usr/bin/env python3
"""Generate Lamar's crew and salvage report from schema v2 JSON."""

from __future__ import annotations

import argparse

from schema_v2_runtime import (
    build_report_payload,
    load_weekly,
    recommendation,
    week_label,
    write_agent_outputs,
)


OUT_MD = "report_lamar_week_sample.md"
OUT_JSON = "lamar_report.json"


def featured_score(entry, party_size):
    score = 0.0
    if entry.get("recommended_party_size") in {"small_group", "solo_or_duo"}:
        score += 2
    if party_size in {"duo", "small_group"} and entry.get("recommended_party_size") in {"solo_or_duo", "small_group"}:
        score += 2
    if "crew_fun" in entry.get("value_tags", []):
        score += 3
    if "limited_reward" in entry.get("value_tags", []):
        score += 1
    return score


def salvage_score(entry):
    return 5.0 if entry.get("claimable") else 2.0


def generate_report(payload):
    crew = payload.get("crew_context", {})
    featured = payload.get("weekly_content", {}).get("featured_activities", [])
    salvage = payload.get("weekly_content", {}).get("salvage_yard_targets", [])
    warnings = []
    insufficient = []
    ranked = []

    party_size = crew.get("usual_party_size", "solo")
    if not crew.get("active_members"):
        insufficient.append("No active_members list; recommendations are generic for solo/public-lobby play.")

    for entry in featured:
        score = featured_score(entry, party_size)
        if score <= 0:
            continue
        ranked.append(
            {
                "id": entry["id"],
                "name": entry["name"],
                "kind": "activity",
                "score": score,
                "notes": entry.get("notes"),
            }
        )

    for entry in salvage:
        ranked.append(
            {
                "id": entry["id"],
                "name": entry["vehicle_name"],
                "kind": "salvage",
                "score": salvage_score(entry),
                "notes": entry.get("robbery_name"),
            }
        )

    if not salvage:
        warnings.append("No salvage_yard_targets available; vehicle-watch guidance is limited.")

    ranked.sort(key=lambda item: item["score"], reverse=True)
    top_items = ranked[:5]
    recommendations = []
    for item in top_items:
        action = "prioritize" if item["kind"] == "salvage" or item["score"] >= 4 else "consider"
        recommendations.append(
            recommendation(
                item["id"],
                action,
                item["notes"] or "Good crew-fit content for this week's sessions.",
                confidence="medium",
                score=item["score"],
            )
        )

    summary = "Keep the crew around salvage targets and short crew-friendly activities that match the actual party size."
    report_payload = build_report_payload(
        "lamar",
        payload,
        summary,
        recommendations,
        warnings=warnings,
        insufficient_data=insufficient,
        extra={"crew_snapshot": crew, "ranked_candidates": top_items},
    )

    lines = [
        f"# Lamar Crew Report — {week_label(payload)}",
        "",
        "## Crew Snapshot",
        f"- Crew name: {crew.get('crew_name') or 'Unknown'}",
        f"- Party size: {party_size}",
        f"- Coordination level: {crew.get('coordination_level', 'unknown')}",
        "",
        "## Best Crew-Fit Picks",
    ]
    if top_items:
        for item in top_items:
            lines.append(f"- {item['name']} — {item['kind']} — score {item['score']:.1f}")
    else:
        lines.append("- No crew-fit opportunities were detected.")

    if warnings:
        lines.extend(["", "## Warnings"])
        for warning in warnings:
            lines.append(f"- {warning}")

    if insufficient:
        lines.extend(["", "## Insufficient Data"])
        for item in insufficient:
            lines.append(f"- {item}")

    lines.extend(["", "---", "Lamar (Crew, Vibe & Vehicle Watch Analyst) — schema v2 planning report."])
    return report_payload, lines


def main():
    parser = argparse.ArgumentParser(description="Generate Lamar report from schema v2 payload.")
    parser.add_argument("--weekly", help="Path to schema v2 JSON", default=None)
    args = parser.parse_args()
    _, payload = load_weekly(args.weekly)
    report_payload, markdown_lines = generate_report(payload)
    md_path, json_path = write_agent_outputs("lamar", payload, report_payload, markdown_lines, OUT_MD, OUT_JSON)
    print(f"Lamar report written to {md_path}")
    print(f"Lamar structured report written to {json_path}")


if __name__ == "__main__":
    main()
