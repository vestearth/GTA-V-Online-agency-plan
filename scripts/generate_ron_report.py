#!/usr/bin/env python3
"""Generate Ron's narrative planning report from schema v2 JSON."""

from __future__ import annotations

import argparse

from schema_v2_runtime import (
    build_report_payload,
    is_limited,
    load_weekly,
    recommendation,
    week_label,
    write_agent_outputs,
)


OUT_MD = "report_ron_week_sample.md"
OUT_JSON = "ron_report.json"


def narrative_score(entry):
    score = 0.0
    if is_limited(entry):
        score += 3
    if "new_content" in entry.get("value_tags", []):
        score += 3
    if "limited_reward" in entry.get("value_tags", []):
        score += 2
    if "crew_fun" in entry.get("value_tags", []):
        score += 2
    return score


def generate_report(payload):
    featured = payload.get("weekly_content", {}).get("featured_activities", [])
    vehicles = payload.get("weekly_content", {}).get("vehicle_opportunities", [])
    crew = payload.get("crew_context", {})
    warnings = []
    insufficient = []
    ranked = []

    if not featured:
        insufficient.append("No featured_activities were provided.")
    if not crew.get("active_members"):
        warnings.append("No active_members list; narrative is based on planning intent rather than a named crew cast.")

    for entry in featured:
        score = narrative_score(entry)
        ranked.append(
            {
                "id": entry["id"],
                "name": entry["name"],
                "score": score,
                "reason": entry.get("notes") or "Strong story beat for the week.",
            }
        )

    for entry in vehicles:
        if entry.get("opportunity_type") in {"prize_ride", "podium", "new_release"}:
            ranked.append(
                {
                    "id": entry["id"],
                    "name": entry["vehicle_name"],
                    "score": 4.0 if entry.get("limited") else 2.0,
                    "reason": entry.get("acquisition", {}).get("challenge")
                    or entry.get("acquisition", {}).get("claim_path")
                    or "Vehicle beat with narrative weight.",
                }
            )

    ranked.sort(key=lambda item: item["score"], reverse=True)
    top_items = ranked[:5]
    recommendations = []
    for item in top_items:
        recommendations.append(
            recommendation(
                item["id"],
                "feature_in_plan",
                item["reason"],
                confidence="medium",
                score=item["score"],
            )
        )

    summary = "This week reads best as a mix of limited unlocks, new content, and a few standout beats worth building the plan around."
    report_payload = build_report_payload(
        "ron",
        payload,
        summary,
        recommendations,
        warnings=warnings[:6],
        insufficient_data=insufficient,
        extra={
            "ranked_candidates": top_items,
            "crew_name": crew.get("crew_name"),
            "theme": "limited unlocks and momentum-building sessions",
        },
    )

    lines = [
        f"# Ron Narrative Report — {week_label(payload)}",
        "",
        "## Theme",
        "- Limited unlocks, new content, and a small crew trying to turn a normal week into a memorable run.",
        "",
        "## Big Story Beats",
    ]
    if top_items:
        for item in top_items:
            lines.append(f"- {item['name']} — score {item['score']:.1f} — {item['reason']}")
    else:
        lines.append("- No narrative beats found.")

    if warnings:
        lines.extend(["", "## Warnings"])
        for warning in warnings[:6]:
            lines.append(f"- {warning}")

    if insufficient:
        lines.extend(["", "## Insufficient Data"])
        for item in insufficient:
            lines.append(f"- {item}")

    lines.extend(["", "---", "Ron (Weekly Story & Momentum Narrator) — schema v2 planning report."])
    return report_payload, lines


def main():
    parser = argparse.ArgumentParser(description="Generate Ron report from schema v2 payload.")
    parser.add_argument("--weekly", help="Path to schema v2 JSON", default=None)
    args = parser.parse_args()
    _, payload = load_weekly(args.weekly)
    report_payload, markdown_lines = generate_report(payload)
    md_path, json_path = write_agent_outputs("ron", payload, report_payload, markdown_lines, OUT_MD, OUT_JSON)
    print(f"Ron report written to {md_path}")
    print(f"Ron structured report written to {json_path}")


if __name__ == "__main__":
    main()
