#!/usr/bin/env python3
"""
Generate a Franklin report from weekly activity and sample Franklin data.
Writes Markdown report to `reports/franklin_report_from_weekly.md`.

Usage:
  python scripts/generate_franklin_report.py
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WEEKLY = ROOT / 'data' / 'weekly_activity_apr2-9.json'
SAMPLE = ROOT / 'data' / 'sample_franklin_week.json'
OUT = ROOT / 'reports' / 'franklin_report_from_weekly.md'


def load(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def normalize_name(name):
    return re.sub(r'[^a-z0-9]+', ' ', name.lower()).strip()


def match_samples_to_weekly(weekly, sample):
    matches = []
    weekly_names = []
    # collect all weekly discount vehicle names
    disc = weekly.get('discounts', {})
    for key in ('law_enforcement_vehicle_discounts', 'general_vehicle_discounts'):
        block = disc.get(key) or {}
        vehicles = block.get('vehicles') or []
        weekly_names.extend(vehicles)

    for entry in sample.get('discount', []):
        sku = entry['sku']
        sample_name = entry.get('name', '')
        sample_norm = normalize_name(sample_name)
        found = []
        for w in weekly_names:
            weekly_norm = normalize_name(w)
            if sample_norm in weekly_norm or weekly_norm in sample_norm:
                found.append(w)
        matches.append({'entry': entry, 'matched_weekly': found})
    return matches, weekly_names


def weekly_discounts_with_sample_data(weekly, sample):
    weekly_names = []
    disc = weekly.get('discounts', {})
    for key in ('law_enforcement_vehicle_discounts', 'general_vehicle_discounts'):
        block = disc.get(key) or {}
        vehicles = block.get('vehicles') or []
        weekly_names.extend(vehicles)

    sample_entries = sample.get('discount', [])
    sample_map = {}
    for entry in sample_entries:
        sample_map[normalize_name(entry.get('name', ''))] = entry

    evaluations = []
    for name in weekly_names:
        norm = normalize_name(name)
        matched_entry = None
        if norm in sample_map:
            matched_entry = sample_map[norm]
        else:
            # fallback: try matching by subset of tokens
            for sample_norm, entry in sample_map.items():
                if sample_norm in norm or norm in sample_norm:
                    matched_entry = entry
                    break
        evaluations.append({'name': name, 'sample': matched_entry})
    return evaluations


def compute_value_score(e, tests):
    # heuristic value: perf*10 + premium_stability*5 - price/100000 - upgrade_cost/10000
    perf = e.get('performance_score', 0)
    price = e.get('price', 0)
    upgrade = e.get('upgrade_cost', 0)
    sku = e.get('sku')
    premium = tests.get(sku, {}).get('premium', {})
    stability = premium.get('stability', 0)
    score = perf * 10 + stability * 5 - (price / 100000.0) - (upgrade / 10000.0)
    return round(score, 2)


def recommendation_from_score(score):
    if score >= 8.0:
        return 'Buy'
    if score >= 5.0:
        return 'Consider'
    return 'Skip'


def extract_premium_test_ride_vehicles(weekly):
    premium_names = []
    for a in weekly.get('activities', []):
        name = a.get('name', '')
        if 'premium test ride' in name.lower():
            if ':' in name:
                premium_names.append(name.split(':', 1)[1].strip())
            else:
                premium_names.append(name.strip())
    return premium_names


def analyze_luxury_autos(weekly):
    luxury_autos = weekly.get('luxury_autos', [])
    if not luxury_autos:
        return ['- No luxury autos listed this week.']

    lines = ['- Franklin flags these luxury autos for review:']
    discounts = weekly.get('discounts', {})
    weekly_discount_names = []
    for key in ('law_enforcement_vehicle_discounts', 'general_vehicle_discounts'):
        block = discounts.get(key) or {}
        weekly_discount_names.extend(block.get('vehicles', []) or [])

    for entry in luxury_autos:
        if 'Removed Vehicle' in entry or 'Removed vehicle' in entry:
            lines.append(f"- {entry} — Note: Removed vehicle, avoid buying.")
            continue
        matching = [name for name in weekly_discount_names if name.lower() in entry.lower() or entry.lower() in name.lower()]
        if matching:
            lines.append(f"- {entry} — Related discount vehicle(s) found: {matching}")
        else:
            lines.append(f"- {entry} — Premium/collectible pick; use only if the crew wants a high-end ride rather than a challenge-target vehicle.")
    return lines


def generate_report():
    weekly = load(WEEKLY)
    sample = load(SAMPLE)
    matches, weekly_names = match_samples_to_weekly(weekly, sample)

    lines = []
    lines.append(f"# Franklin Report — {weekly.get('week')}")
    lines.append("")
    lines.append("## Prize Ride Note")
    # Prize ride vehicle mentioned in activities
    prize_lines = [a for a in weekly.get('activities', []) if 'Prize Ride' in a.get('name', '') or 'Prize Ride' in a.get('notes','')]
    if prize_lines:
        lines.append("- Detected Prize Ride related activities:")
        for a in prize_lines:
            lines.append(f"  - {a.get('name')}: {a.get('notes','')}")
    else:
        lines.append("- No explicit Prize Ride activity detected in weekly activities.")

    # Detect removed vehicles mentioned in activities (notes contain 'Removed vehicle')
    removed = []
    for a in weekly.get('activities', []):
        notes = (a.get('notes') or '').lower()
        if 'removed vehicle' in notes:
            # try to extract vehicle name after colon in activity name
            name = a.get('name', '')
            if ':' in name:
                veh = name.split(':', 1)[1].strip()
            else:
                veh = name
            removed.append(veh)

    if removed:
        lines.append("")
        lines.append("## Removed Vehicles (sold / removed from game this week)")
        for v in removed:
            lines.append(f"- {v}")

    lines.append("")
    lines.append("## Discount Vehicles Found in Weekly Data")
    for n in weekly_names:
        lines.append(f"- {n}")

    weekly_evals = weekly_discounts_with_sample_data(weekly, sample)
    if weekly_evals:
        lines.append("")
        lines.append("## Weekly Discount Vehicles Evaluation")
        for eval in weekly_evals:
            sample_entry = eval['sample']
            if sample_entry:
                score = compute_value_score(sample_entry, sample.get('test_rides', {}))
                rec = recommendation_from_score(score)
                lines.append(f"- {eval['name']} — {rec} (ValueScore: {score}) — matched sample: {sample_entry['name']}")
            else:
                lines.append(f"- {eval['name']} — No sample vehicle data available for valuation; manual review recommended.")

    premium_test_rides = extract_premium_test_ride_vehicles(weekly)
    if premium_test_rides:
        lines.append("")
        lines.append("## Premium Test Ride Vehicles Found")
        for v in premium_test_rides:
            lines.append(f"- {v}")

    lines.append("")
    lines.append("## Luxury Autos Analysis")
    lines.extend(analyze_luxury_autos(weekly))

    lines.append("")
    lines.append("## Matched Sample Vehicles & Valuation (heuristic)")
    for m in matches:
        e = m['entry']
        sku = e['sku']
        matched = m['matched_weekly']
        is_removed = False
        # mark as removed if any matched weekly name appears in removed list
        for w in matched:
            for rv in removed:
                if rv and rv.lower() in w.lower():
                    is_removed = True
        if matched:
            score = compute_value_score(e, sample.get('test_rides', {}))
            rec = recommendation_from_score(score)
            premium = sample.get('test_rides', {}).get(sku, {}).get('premium', {})
            lines.append(f"- {e['name']} (sku: {sku}) — Matched weekly names: {matched}")
            lines.append(f"  - Price: ${e['price']:,} — Perf: {e.get('performance_score')} — UpgradeCost: ${e.get('upgrade_cost'):,}")
            if premium:
                lines.append(f"  - Premium test: lap_time {premium.get('lap_time_sec')}s, stability {premium.get('stability')}")
            if is_removed:
                lines.append(f"  - STATUS: Removed this week — skip purchase (was removed from game this week)")
            else:
                lines.append(f"  - ValueScore: {score} — Recommendation: {rec}")
        else:
            lines.append(f"- {e['name']} (sku: {sku}) — No direct match in weekly discount names (manual review suggested)")

    lines.append("")
    lines.append("## Discount Vehicle Recommendations")
    for m in matches:
        e = m['entry']
        sku = e['sku']
        matched = m['matched_weekly']
        score = compute_value_score(e, sample.get('test_rides', {}))
        rec = recommendation_from_score(score)
        if matched:
            lines.append(f"- {e['name']} — {rec} (matched: {matched})")
        else:
            lines.append(f"- {e['name']} — {rec} (no strong weekly discount match)")

    lines.append("")
    lines.append("## Quick Recommendations")
    # simple picks from sample
    for m in matches:
        e = m['entry']
        sku = e['sku']
        matched = m['matched_weekly']
        if matched:
            # avoid recommending removed vehicles
            is_removed = any(rv and any(rv.lower() in w.lower() for w in matched) for rv in removed)
            score = compute_value_score(e, sample.get('test_rides', {}))
            rec = recommendation_from_score(score) if not is_removed else 'Skip (Removed)'
            lines.append(f"- {e['name']}: {rec} (ValueScore {score})")

    lines.append("")
    lines.append("---")
    lines.append("Franklin (Prize Ride & Test Ride Analyst) — Generated from weekly_activity_apr2-9.json and sample_franklin_week.json")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text('\n'.join(lines), encoding='utf-8')
    print(f"Report written to {OUT}")


if __name__ == '__main__':
    generate_report()
