#!/usr/bin/env python3
"""Generate Franklin's vehicle planning report from schema v2 JSON."""

from __future__ import annotations

import argparse

from schema_v2_runtime import (
    build_report_payload,
    load_weekly,
    load_franklin_brand_reference,
    match_vehicle_brand,
    recommendation,
    week_label,
    write_agent_outputs,
)


OUT_MD = "franklin_report_from_weekly.md"
OUT_JSON = "franklin_report.json"


def vehicle_score(entry):
    evaluation = entry.get("evaluation_inputs", {})
    score = float(evaluation.get("performance_score") or 0)
    score += (entry.get("discount_percent") or 0) / 10.0
    if entry.get("opportunity_type") == "prize_ride":
        score += 2.5
    if entry.get("opportunity_type") in {"premium_test_ride", "podium"}:
        score += 1.5
    if entry.get("limited"):
        score += 1.0
    if entry.get("removed_vehicle"):
        score += 0.5
    if evaluation.get("service_vehicle"):
        score += 0.8
    if evaluation.get("weaponized"):
        score += 0.5
    premium_metrics = evaluation.get("test_metrics", {}).get("premium", {})
    if premium_metrics.get("stability") is not None:
        score += premium_metrics["stability"] * 2
    return score


def recommendation_action(entry, score):
    if entry.get("removed_vehicle") and entry.get("opportunity_type") == "test_ride":
        return "consider"
    if entry.get("opportunity_type") == "prize_ride" or score >= 9:
        return "prioritize"
    if score >= 6:
        return "consider"
    return "skip"

PREFERRED_BRANDS = {"Obey", "Dewbauchee"}


def generate_report(payload):
    brand_reference = load_franklin_brand_reference()
    brands = brand_reference.get("brands", [])
    opportunities = payload.get("weekly_content", {}).get("vehicle_opportunities", [])
    races = payload.get("weekly_content", {}).get("time_trials_and_races", [])
    warnings = []
    insufficient = []
    ranked = []

    if not opportunities:
        insufficient.append("No vehicle_opportunities were provided.")
    if brand_reference.get("validation_errors"):
        warnings.extend(brand_reference["validation_errors"][:4])

    for entry in opportunities:
        score = vehicle_score(entry)
        brand_entry = match_vehicle_brand(entry.get("vehicle_name"), brands)
        if brand_entry and brand_entry.get("name") in PREFERRED_BRANDS:
            score += 1.5
        ranked.append(
            {
                "id": entry["id"],
                "name": entry["vehicle_name"],
                "type": entry.get("opportunity_type"),
                "score": score,
                "brand": brand_entry.get("name") if brand_entry else None,
                "real_world": brand_entry.get("real_world", []) if brand_entry else [],
                "notes": entry.get("acquisition", {}).get("challenge") or entry.get("acquisition", {}).get("claim_path"),
            }
        )
        if entry.get("opportunity_type") == "discount" and entry.get("price") is None:
            warnings.append(f"{entry['id']}: no explicit price captured; budget fit must be checked manually.")

    ranked.sort(key=lambda item: item["score"], reverse=True)
    top_items = ranked[:5]

    recommendations = []
    for item in top_items:
        source_entry = next(entry for entry in opportunities if entry["id"] == item["id"])
        recommendations.append(
            recommendation(
                item["id"],
                recommendation_action(source_entry, item["score"]),
                item["notes"] or "Strong weekly vehicle opportunity based on type, limited status, and explicit evaluation inputs.",
                confidence="high" if source_entry.get("opportunity_type") == "prize_ride" else "medium",
                score=item["score"],
            )
        )

    summary = "Prioritize limited weekly unlocks first, then discounted vehicles with the strongest explicit performance signals."
    report_payload = build_report_payload(
        "franklin",
        payload,
        summary,
        recommendations,
        warnings=warnings[:6],
        insufficient_data=insufficient,
        extra={
            "ranked_candidates": top_items,
            "race_context": races,
            "brand_reference_loaded": len(brands),
        },
    )

    lines = [
        f"# Franklin Vehicle Report — {week_label(payload)}",
        "",
        "## Top Vehicle Priorities",
    ]
    if top_items:
        for item in top_items:
            brand_suffix = f" — brand {item['brand']}" if item.get("brand") else ""
            lines.append(f"- {item['name']} — {item['type']} — score {item['score']:.1f}{brand_suffix}")
    else:
        lines.append("- No vehicle opportunities available.")

    lines.extend(["", "## Race & Trial Fit"])
    if races:
        for entry in races:
            restrictions = ", ".join(entry.get("vehicle_restrictions", []) or ["open class"])
            lines.append(f"- {entry['name']} — restrictions: {restrictions}")
    else:
        lines.append("- No time trial or race context in the payload.")

    lines.extend(["", "## Vehicle Notes"])
    for item in top_items:
        if item["notes"]:
            lines.append(f"- {item['name']}: {item['notes']}")
        if item.get("real_world"):
            lines.append(f"- {item['name']}: real-world match {', '.join(item['real_world'])}")
    if warnings:
        for warning in warnings[:4]:
            lines.append(f"- Warning: {warning}")

    if insufficient:
        lines.extend(["", "## Insufficient Data"])
        for item in insufficient:
            lines.append(f"- {item}")

    lines.extend(["", "---", "Franklin (Vehicle Opportunity Analyst) — schema v2 planning report."])
    return report_payload, lines


def main():
    parser = argparse.ArgumentParser(description="Generate Franklin report from schema v2 payload.")
    parser.add_argument("--weekly", help="Path to schema v2 JSON", default=None)
    args = parser.parse_args()
    _, payload = load_weekly(args.weekly)
    report_payload, markdown_lines = generate_report(payload)
    md_path, json_path = write_agent_outputs("franklin", payload, report_payload, markdown_lines, OUT_MD, OUT_JSON)
    print(f"Franklin report written to {md_path}")
    print(f"Franklin structured report written to {json_path}")


if __name__ == "__main__":
    main()
