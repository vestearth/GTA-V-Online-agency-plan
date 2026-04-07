#!/usr/bin/env python3
"""Generate Agent 14's operations report from schema v2 JSON."""

from __future__ import annotations

import argparse

from schema_v2_runtime import (
    build_report_payload,
    cayo_reference_summary,
    detect_cayo_perico_entry,
    load_weekly,
    load_agent14_reference,
    missing_requirements,
    recommendation,
    session_plan_player_count,
    week_label,
    write_agent_outputs,
)


OUT_MD = "report_agent14_week_sample.md"
OUT_JSON = "agent14_report.json"


def party_match_score(session_plan, recommended_party_size):
    if not session_plan:
        return 0.0
    wanted = recommended_party_size or "any"
    score = 0.0
    for block in session_plan:
        party = block.get("party_size")
        hours = float(block.get("hours") or 0)
        if wanted == "solo" and party == "solo":
            score = max(score, 2 + hours)
        elif wanted == "solo_or_duo" and party in {"solo", "1_2_friends"}:
            score = max(score, 2 + hours)
        elif wanted == "small_group" and party in {"1_2_friends", "full_crew"}:
            score = max(score, 1.5 + hours)
        elif wanted == "any":
            score = max(score, 1 + hours)
    return score


def activity_score(payload, entry):
    session_plan = payload.get("planning_context", {}).get("session_plan", [])
    blockers = missing_requirements(payload, entry.get("requirements", []))
    score = 0.0
    score += party_match_score(session_plan, entry.get("recommended_party_size"))
    score += 2 if entry.get("content_type") == "repeatable" else 0.5
    score += 2 if entry.get("timebox_minutes") and entry["timebox_minutes"] <= 20 else 0
    score += 1 if "limited_reward" in entry.get("value_tags", []) else 0
    score -= len(blockers) * 4
    return score, blockers


def business_score(payload, entry):
    session_plan = payload.get("planning_context", {}).get("session_plan", [])
    blockers = missing_requirements(payload, entry.get("requirements", []))
    total_hours = sum(float(block.get("hours") or 0) for block in session_plan)
    score = 0.0
    if "active_grind" in entry.get("estimated_value_tags", []):
        score += min(total_hours, 4)
    if "passive_income" in entry.get("estimated_value_tags", []):
        score += 2
    score += len(entry.get("bonus", {}))
    score -= len(blockers) * 4
    return score, blockers


def generate_report(payload):
    cayo_reference = load_agent14_reference()
    benchmark_party_size = session_plan_player_count(payload)
    cayo_benchmark = cayo_reference_summary(cayo_reference, benchmark_party_size)
    featured = payload.get("weekly_content", {}).get("featured_activities", [])
    businesses = payload.get("weekly_content", {}).get("business_opportunities", [])
    crew = payload.get("crew_context", {})
    warnings = []
    insufficient = []
    ranked = []

    if not payload.get("planning_context", {}).get("session_plan"):
        insufficient.append("No session_plan provided; execution-readiness recommendations are less precise.")
    if not crew.get("coordination_level"):
        insufficient.append("No crew coordination data provided.")

    for entry in featured:
        score, blockers = activity_score(payload, entry)
        reference_note = None
        if detect_cayo_perico_entry(entry) and cayo_benchmark:
            score += 2.0
            reference_note = (
                f"Cayo benchmark for {cayo_benchmark['player_count']} player(s): "
                f"leader net {cayo_benchmark['leader_net']}, team net {cayo_benchmark['team_net']}, setup fee {cayo_benchmark['setup_fee']}."
            )
        if blockers:
            warnings.append(f"{entry['id']}: operational blockers {', '.join(blockers)}")
        ranked.append(
            {
                "id": entry["id"],
                "name": entry["name"],
                "kind": "activity",
                "score": score,
                "blockers": blockers,
                "reason": " ".join(
                    part for part in [entry.get("notes") or "Operationally relevant featured activity.", reference_note] if part
                ),
            }
        )

    for entry in businesses:
        score, blockers = business_score(payload, entry)
        reference_note = None
        if detect_cayo_perico_entry(entry) and cayo_benchmark:
            score += 2.0
            reference_note = (
                f"Cayo benchmark for {cayo_benchmark['player_count']} player(s): "
                f"leader net {cayo_benchmark['leader_net']}, team net {cayo_benchmark['team_net']}, setup fee {cayo_benchmark['setup_fee']}."
            )
        if blockers:
            warnings.append(f"{entry['id']}: business access blockers {', '.join(blockers)}")
        ranked.append(
            {
                "id": entry["id"],
                "name": entry["name"],
                "kind": "business",
                "score": score,
                "blockers": blockers,
                "reason": " ".join(
                    part for part in [entry.get("notes") or "Operationally relevant business opportunity.", reference_note] if part
                ),
            }
        )

    ranked.sort(key=lambda item: item["score"], reverse=True)
    top_items = ranked[:5]
    recommendations = []
    for item in top_items:
        recommendations.append(
            recommendation(
                item["id"],
                "prepare" if item["blockers"] else "prioritize",
                item["reason"],
                confidence="medium" if item["blockers"] else "high",
                score=item["score"],
                blockers=item["blockers"] or None,
            )
        )

    summary = "Prioritize the activities that fit the actual session windows and have the fewest operational blockers."
    report_payload = build_report_payload(
        "agent14",
        payload,
        summary,
        recommendations,
        warnings=warnings[:6],
        insufficient_data=insufficient,
        extra={
            "ranked_candidates": top_items,
            "crew_coordination_level": crew.get("coordination_level"),
            "cayo_reference_loaded": bool(cayo_reference),
        },
    )

    lines = [
        f"# Agent 14 Operations Report — {week_label(payload)}",
        "",
        "## Operational Priorities",
    ]
    if top_items:
        for item in top_items:
            suffix = f" — blockers: {', '.join(item['blockers'])}" if item["blockers"] else ""
            lines.append(f"- {item['name']} — score {item['score']:.1f}{suffix}")
    else:
        lines.append("- No operational targets found.")

    lines.extend(["", "## Readiness Notes"])
    lines.append(f"- Crew coordination level: {crew.get('coordination_level', 'unknown')}")
    lines.append(f"- Session blocks captured: {len(payload.get('planning_context', {}).get('session_plan', []))}")
    lines.append(f"- Cayo benchmark reference loaded: {'yes' if cayo_reference else 'no'}")

    if cayo_benchmark:
        lines.extend(["", "## Cayo Benchmark"])
        lines.append(
            f"- {cayo_benchmark['player_count']} player(s): leader net {cayo_benchmark['leader_net']}, team net {cayo_benchmark['team_net']}, setup fee {cayo_benchmark['setup_fee']}"
        )

    if warnings:
        lines.extend(["", "## Warnings"])
        for warning in warnings[:6]:
            lines.append(f"- {warning}")

    if insufficient:
        lines.extend(["", "## Insufficient Data"])
        for item in insufficient:
            lines.append(f"- {item}")

    lines.extend(["", "---", "Agent 14 (Operations & Efficiency Analyst) — schema v2 planning report."])
    return report_payload, lines


def main():
    parser = argparse.ArgumentParser(description="Generate Agent 14 report from schema v2 payload.")
    parser.add_argument("--weekly", help="Path to schema v2 JSON", default=None)
    args = parser.parse_args()
    _, payload = load_weekly(args.weekly)
    report_payload, markdown_lines = generate_report(payload)
    md_path, json_path = write_agent_outputs("agent14", payload, report_payload, markdown_lines, OUT_MD, OUT_JSON)
    print(f"Agent 14 report written to {md_path}")
    print(f"Agent 14 structured report written to {json_path}")


if __name__ == "__main__":
    main()
