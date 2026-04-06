#!/usr/bin/env python3
"""Generate Michael's planning report from schema v2 JSON."""

from __future__ import annotations

import argparse

from schema_v2_runtime import (
    build_report_payload,
    is_limited,
    load_weekly,
    missing_requirements,
    recommendation,
    week_label,
    write_agent_outputs,
)


OUT_MD = "report_michael_week_sample.md"
OUT_JSON = "michael_report.json"


def score_activity(payload, entry):
    goals = set(payload.get("player_context", {}).get("goals_this_week", []))
    policy = payload.get("planning_context", {}).get("decision_policy", {})
    tags = set(entry.get("value_tags", []))
    bonus = entry.get("bonus", {})
    blockers = missing_requirements(payload, entry.get("requirements", []))
    score = 0.0
    score += bonus.get("gta_cash_multiplier", 1) * 2
    score += bonus.get("gta_plus_cash_multiplier", 0)
    score += bonus.get("rp_multiplier", 0) * 0.5
    if "money" in tags and ("make_money" in goals or payload.get("planning_context", {}).get("primary_objective") == "profit"):
        score += 4
    if "passive_income" in tags and "passive_income" in goals:
        score += 3
    if "limited_reward" in tags and policy.get("prioritize_limited_time_content"):
        score += 2
    if is_limited(entry) and policy.get("prioritize_limited_time_content"):
        score += 1
    if entry.get("timebox_minutes") and entry["timebox_minutes"] <= 20:
        score += 1
    score -= len(blockers) * 4
    return score, blockers


def score_business(payload, entry):
    goals = set(payload.get("player_context", {}).get("goals_this_week", []))
    tags = set(entry.get("estimated_value_tags", []))
    blockers = missing_requirements(payload, entry.get("requirements", []))
    score = 0.0
    if "active_grind" in tags and "make_money" in goals:
        score += 4
    if "passive_income" in tags and "passive_income" in goals:
        score += 5
    if "limited_reward" in tags:
        score += 2
    score += len(entry.get("bonus", {}))
    score -= len(blockers) * 4
    return score, blockers


def generate_report(payload):
    ranked = []
    warnings = []
    insufficient = []

    for entry in payload.get("weekly_content", {}).get("featured_activities", []):
        score, blockers = score_activity(payload, entry)
        if blockers:
            warnings.append(f"{entry['id']}: missing requirements {', '.join(blockers)}")
        ranked.append(
            {
                "id": entry["id"],
                "name": entry["name"],
                "kind": "activity",
                "score": score,
                "blockers": blockers,
                "notes": entry.get("notes"),
            }
        )

    for entry in payload.get("weekly_content", {}).get("business_opportunities", []):
        score, blockers = score_business(payload, entry)
        if blockers:
            warnings.append(f"{entry['id']}: business access missing {', '.join(blockers)}")
        ranked.append(
            {
                "id": entry["id"],
                "name": entry["name"],
                "kind": "business",
                "score": score,
                "blockers": blockers,
                "notes": entry.get("notes"),
            }
        )

    if not payload.get("player_context", {}).get("cash_on_hand") and not payload.get("player_context", {}).get("bank_balance"):
        insufficient.append("No liquid-cash snapshot; buy recommendations should be budget-checked manually.")

    ranked.sort(key=lambda item: item["score"], reverse=True)
    top_items = ranked[:5]
    recommendations = []
    for item in top_items:
        action = "prepare" if item["blockers"] else "prioritize"
        reason = item["notes"] or "Strong planning value based on weekly bonuses, goals, and access fit."
        recommendations.append(
            recommendation(
                item["id"],
                action,
                reason,
                confidence="medium" if item["blockers"] else "high",
                score=item["score"],
                blockers=item["blockers"] or None,
            )
        )

    summary = "Focus on the highest-value weekly bonuses and owned-business opportunities that fit the player's time budget."
    report_payload = build_report_payload(
        "michael",
        payload,
        summary,
        recommendations,
        warnings=warnings[:6],
        insufficient_data=insufficient,
        extra={"ranked_candidates": top_items},
    )

    lines = [
        f"# Michael's Planning Report — {week_label(payload)}",
        "",
        "## Executive View",
        "- Michael focuses on planning value, access requirements, and weekly bonus leverage.",
        "- This report is planning-oriented and avoids inventing payout numbers when the payload does not provide them.",
        "",
        "## Ranked Opportunities",
    ]
    for item in top_items:
        if item["blockers"]:
            lines.append(f"- {item['name']} — score {item['score']:.1f} — prepare first ({', '.join(item['blockers'])})")
        else:
            lines.append(f"- {item['name']} — score {item['score']:.1f} — priority fit for this week")
    if not top_items:
        lines.append("- No opportunities available in the payload.")

    lines.extend(["", "## Warnings"])
    if warnings:
        for warning in warnings[:6]:
            lines.append(f"- {warning}")
    else:
        lines.append("- No major access blockers detected.")

    if insufficient:
        lines.extend(["", "## Insufficient Data"])
        for item in insufficient:
            lines.append(f"- {item}")

    lines.extend(
        [
            "",
            "---",
            "Michael (Strategic & Financial Analyst) — schema v2 planning report.",
        ]
    )
    return report_payload, lines


def main():
    parser = argparse.ArgumentParser(description="Generate Michael report from schema v2 payload.")
    parser.add_argument("--weekly", help="Path to schema v2 JSON", default=None)
    args = parser.parse_args()
    _, payload = load_weekly(args.weekly)
    report_payload, markdown_lines = generate_report(payload)
    md_path, json_path = write_agent_outputs("michael", payload, report_payload, markdown_lines, OUT_MD, OUT_JSON)
    print(f"Michael report written to {md_path}")
    print(f"Michael structured report written to {json_path}")


if __name__ == "__main__":
    main()
