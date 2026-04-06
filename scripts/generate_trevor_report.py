#!/usr/bin/env python3
"""Generate Trevor's gear and combat-value report from schema v2 JSON."""

from __future__ import annotations

import argparse

from schema_v2_runtime import (
    build_report_payload,
    load_weekly,
    recommendation,
    week_label,
    write_agent_outputs,
)


OUT_MD = "report_trevor_week_sample.md"
OUT_JSON = "trevor_report.json"


URGENCY_SCORE = {
    "must_claim": 10,
    "good_pick": 7,
    "optional": 4,
    "skip": 1,
}


def gear_score(entry, gta_plus_enabled):
    score = URGENCY_SCORE.get(entry.get("urgency"), 0) + (entry.get("discount_percent") or 0) / 10.0
    if entry.get("gta_plus_only") and not gta_plus_enabled:
        score -= 5
    if "vehicle_disable" in entry.get("combat_role_tags", []):
        score += 1
    return score


def vehicle_score(entry):
    evaluation = entry.get("evaluation_inputs", {})
    score = (entry.get("discount_percent") or 0) / 10.0
    if evaluation.get("weaponized"):
        score += 4
    if evaluation.get("service_vehicle"):
        score += 2
    if "combat" in evaluation.get("utility_tags", []):
        score += 2
    return score


def generate_report(payload):
    gta_plus_enabled = bool(payload.get("player_context", {}).get("gta_plus"))
    gear_entries = payload.get("weekly_content", {}).get("weapon_and_gear_opportunities", [])
    vehicle_entries = payload.get("weekly_content", {}).get("vehicle_opportunities", [])
    warnings = []
    insufficient = []

    ranked = []
    for entry in gear_entries:
        score = gear_score(entry, gta_plus_enabled)
        ranked.append(
            {
                "id": entry["id"],
                "name": entry["name"],
                "kind": "gear",
                "score": score,
                "notes": entry.get("notes"),
                "plus_only": entry.get("gta_plus_only", False),
            }
        )
        if entry.get("gta_plus_only") and not gta_plus_enabled:
            warnings.append(f"{entry['id']}: GTA+ only reward on a non-GTA+ account.")

    for entry in vehicle_entries:
        score = vehicle_score(entry)
        if score <= 0:
            continue
        ranked.append(
            {
                "id": entry["id"],
                "name": entry["vehicle_name"],
                "kind": "vehicle",
                "score": score,
                "notes": entry.get("acquisition", {}).get("claim_path"),
                "plus_only": entry.get("gta_plus_only", False),
            }
        )

    if not gear_entries:
        insufficient.append("No weapon_and_gear_opportunities were provided.")

    ranked.sort(key=lambda item: item["score"], reverse=True)
    top_items = ranked[:5]
    recommendations = []
    for item in top_items:
        action = "claim_now" if item["kind"] == "gear" and item["score"] >= 9 else "consider"
        recommendations.append(
            recommendation(
                item["id"],
                action,
                item["notes"] or "High combat value for this week.",
                confidence="high" if item["score"] >= 8 else "medium",
                score=item["score"],
            )
        )

    summary = "Claim the free gun-van items first, then spend on the highest-value combat gear or service/combat vehicles."
    report_payload = build_report_payload(
        "trevor",
        payload,
        summary,
        recommendations,
        warnings=warnings[:6],
        insufficient_data=insufficient,
        extra={"ranked_candidates": top_items, "gta_plus_enabled": gta_plus_enabled},
    )

    lines = [
        f"# Trevor's Gear Report — {week_label(payload)}",
        "",
        "## Must-Claim And Best-Buy Picks",
    ]
    if top_items:
        for item in top_items:
            gate = " (GTA+)" if item["plus_only"] else ""
            lines.append(f"- {item['name']} — {item['kind']} — score {item['score']:.1f}{gate}")
    else:
        lines.append("- No combat-value opportunities available.")

    lines.extend(["", "## Warnings"])
    if warnings:
        for warning in warnings[:6]:
            lines.append(f"- {warning}")
    else:
        lines.append("- No major gating problems detected.")

    if insufficient:
        lines.extend(["", "## Insufficient Data"])
        for item in insufficient:
            lines.append(f"- {item}")

    lines.extend(["", "---", "Trevor (Weapons, Gear & Combat Value Analyst) — schema v2 planning report."])
    return report_payload, lines


def main():
    parser = argparse.ArgumentParser(description="Generate Trevor report from schema v2 payload.")
    parser.add_argument("--weekly", help="Path to schema v2 JSON", default=None)
    args = parser.parse_args()
    _, payload = load_weekly(args.weekly)
    report_payload, markdown_lines = generate_report(payload)
    md_path, json_path = write_agent_outputs("trevor", payload, report_payload, markdown_lines, OUT_MD, OUT_JSON)
    print(f"Trevor report written to {md_path}")
    print(f"Trevor structured report written to {json_path}")


if __name__ == "__main__":
    main()
