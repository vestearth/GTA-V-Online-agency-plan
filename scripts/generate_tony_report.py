#!/usr/bin/env python3
"""Generate Tony's passive-income report from schema v2 JSON."""

from __future__ import annotations

import argparse

from schema_v2_runtime import (
    build_report_payload,
    load_weekly,
    recommendation,
    week_label,
    write_agent_outputs,
)


OUT_MD = "report_tony_week_sample.md"
OUT_JSON = "tony_report.json"


def goods_score(stock):
    value = float(stock.get("estimated_value") or 0)
    fill = float(stock.get("stock_percent") or 0)
    return (value / 50000.0) + (fill / 25.0)


def feeder_repair_score(entry):
    if not entry.get("owned"):
        return 0.0
    score = 0.0
    if not entry.get("operational"):
        score += 8
    supply = entry.get("supply_level_percent")
    stock = entry.get("stock_level_percent")
    if supply is not None and supply < 40:
        score += 3
    if stock is not None and stock < 35:
        score += 2
    return score


def generate_report(payload):
    nightclub = payload.get("business_state", {}).get("nightclub", {})
    feeders = payload.get("business_state", {}).get("feeder_businesses", [])
    business_opportunities = payload.get("weekly_content", {}).get("business_opportunities", [])
    warnings = []
    insufficient = []
    recommendations = []
    ranked = []

    if not nightclub.get("owned"):
        insufficient.append("Nightclub is not owned; Tony should be treated as not_applicable or acquisition_readiness.")
        report_payload = build_report_payload(
            "tony",
            payload,
            "Nightclub loop is not available on this account yet.",
            [
                recommendation(
                    "nightclub_passive_cycle",
                    "not_applicable",
                    "Nightclub is not owned on this account.",
                    confidence="high",
                )
            ],
            warnings=[],
            insufficient_data=insufficient,
            extra={"nightclub_owned": False},
        )
        lines = [
            f"# Tony Passive Income Report — {week_label(payload)}",
            "",
            "## Status",
            "- Nightclub is not owned, so passive-income optimization is not applicable yet.",
            "",
            "---",
            "Tony (Nightclub & Passive Income Analyst) — schema v2 planning report.",
        ]
        return report_payload, lines

    goods_stock = nightclub.get("goods_stock", [])
    if not goods_stock:
        insufficient.append("No nightclub goods_stock provided.")
    if nightclub.get("technicians_total") is None:
        insufficient.append("No technician count provided.")

    for stock in goods_stock:
        ranked.append(
            {
                "id": f"nightclub_goods_{stock.get('goods_type')}",
                "name": stock.get("goods_type"),
                "score": goods_score(stock),
                "reason": f"Stock {stock.get('stock_percent')}% with estimated value {stock.get('estimated_value')}",
            }
        )

    for feeder in feeders:
        score = feeder_repair_score(feeder)
        if score <= 0:
            continue
        ranked.append(
            {
                "id": f"feeder_{feeder.get('business_type')}",
                "name": feeder.get("business_type"),
                "score": score,
                "reason": "Feeder business needs repair, supply, or stock attention.",
            }
        )

    for opportunity in business_opportunities:
        if opportunity.get("business_type") == "nightclub":
            ranked.append(
                {
                    "id": opportunity["id"],
                    "name": opportunity["name"],
                    "score": 5.0,
                    "reason": opportunity.get("notes") or "Relevant passive-income opportunity.",
                }
            )

    ranked.sort(key=lambda item: item["score"], reverse=True)
    top_items = ranked[:5]
    for item in top_items:
        recommendations.append(
            recommendation(
                item["id"],
                "repair" if item["id"].startswith("feeder_") else "maintain",
                item["reason"],
                confidence="medium",
                score=item["score"],
            )
        )

    if nightclub.get("popularity_percent") is not None and nightclub["popularity_percent"] < 60:
        warnings.append("Nightclub popularity is below 60%; safe income is underperforming.")
    if nightclub.get("technicians_total") and len(nightclub.get("technician_assignments", [])) < nightclub["technicians_total"]:
        warnings.append("Some technicians are unassigned.")

    summary = "Keep the Nightclub loop healthy by fixing weak feeder businesses and protecting the highest-value goods streams."
    report_payload = build_report_payload(
        "tony",
        payload,
        summary,
        recommendations,
        warnings=warnings[:6],
        insufficient_data=insufficient,
        extra={"nightclub_owned": True, "ranked_candidates": top_items},
    )

    lines = [
        f"# Tony Passive Income Report — {week_label(payload)}",
        "",
        "## Nightclub Snapshot",
        f"- Popularity: {nightclub.get('popularity_percent', 'unknown')}%",
        f"- Safe cash: {nightclub.get('safe_cash', 'unknown')}",
        f"- Technicians: {nightclub.get('technicians_total', 'unknown')}",
        "",
        "## Priority Maintenance",
    ]
    if top_items:
        for item in top_items:
            lines.append(f"- {item['name']} — score {item['score']:.1f} — {item['reason']}")
    else:
        lines.append("- No passive-income targets found.")

    if warnings:
        lines.extend(["", "## Warnings"])
        for warning in warnings[:6]:
            lines.append(f"- {warning}")

    if insufficient:
        lines.extend(["", "## Insufficient Data"])
        for item in insufficient:
            lines.append(f"- {item}")

    lines.extend(["", "---", "Tony (Nightclub & Passive Income Analyst) — schema v2 planning report."])
    return report_payload, lines


def main():
    parser = argparse.ArgumentParser(description="Generate Tony report from schema v2 payload.")
    parser.add_argument("--weekly", help="Path to schema v2 JSON", default=None)
    args = parser.parse_args()
    _, payload = load_weekly(args.weekly)
    report_payload, markdown_lines = generate_report(payload)
    md_path, json_path = write_agent_outputs("tony", payload, report_payload, markdown_lines, OUT_MD, OUT_JSON)
    print(f"Tony report written to {md_path}")
    print(f"Tony structured report written to {json_path}")


if __name__ == "__main__":
    main()
