#!/usr/bin/env python3
"""
Generate Michael's financial report from weekly activity JSON.
Detects Bonus Activities, counts multipliers, estimates incremental value, and ranks them.
Writes Markdown report to `reports/report_michael_week_sample.md`.

Run:
  python scripts/generate_michael_report.py
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WEEKLY = ROOT / 'data' / 'weekly_activity_apr2-9.json'
OUT = ROOT / 'reports' / 'report_michael_week_sample.md'

MULT_RE = re.compile(r'([0-9]+)\s*[xX]')


def load(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def parse_multiplier(notes):
    if not notes:
        return None
    m = MULT_RE.search(notes)
    if m:
        try:
            return int(m.group(1))
        except ValueError:
            return None
    return None


def estimate_base_payout_for(activity_name):
    # conservative proxies by known activity keywords
    name = activity_name.lower()
    if 'dispatch' in name:
        return 1000
    if 'wildlife' in name:
        return 200
    if 'firefighter' in name:
        return 800
    if 'vespucci' in name:
        return 1500
    # default proxy
    return 1000


def generate():
    weekly = load(WEEKLY)
    activities = weekly.get('activities', [])

    bonus_items = []
    for a in activities:
        cat = a.get('category', '')
        notes = a.get('notes', '') or ''
        if cat.lower() == 'bonus' or 'x' in notes.lower():
            mult = parse_multiplier(notes)
            # if no multiplier found, try looking for multiplier in notes string like '3X for GTA+ Members'
            bonus_items.append({
                'name': a.get('name'),
                'notes': notes,
                'multiplier': mult or 1,
                'count': 1,
                'base_payout': estimate_base_payout_for(a.get('name'))
            })

    # aggregate by name
    agg = {}
    for b in bonus_items:
        key = b['name']
        if key not in agg:
            agg[key] = dict(b)
        else:
            agg[key]['count'] += b.get('count', 1)

    summary = []
    for name, info in agg.items():
        mult = info.get('multiplier', 1)
        count = info.get('count', 1)
        base = info.get('base_payout', 1000)
        est_gross_lift = base * (mult - 1) * count
        # cost proxy: assume 1 hour per event at $300/hr
        est_cost = 300 * count
        est_net = est_gross_lift - est_cost
        priority = 'Low'
        if est_net > 50000:
            priority = 'Priority'
        elif est_net > 10000:
            priority = 'High'
        elif est_net > 2000:
            priority = 'Moderate'
        summary.append({
            'name': name,
            'multiplier': mult,
            'count': count,
            'base': base,
            'est_gross_lift': est_gross_lift,
            'est_cost': est_cost,
            'est_net': est_net,
            'priority': priority,
            'notes': info.get('notes','')
        })

    # sort by est_net desc
    summary.sort(key=lambda x: x['est_net'], reverse=True)

    # Financial summary from file if present
    fin = weekly.get('financials', {})
    lines = []
    lines.append(f"# Michael's Financial Report — {weekly.get('week')}")
    lines.append("")
    lines.append("## Financial Snapshot")
    lines.append(f"- Total Revenue (reported): {fin.get('earnings_total',0)} {fin.get('currency','GTA$')}")
    lines.append(f"- Total Expenses (reported): {fin.get('expenses_total',0)} {fin.get('currency','GTA$')}")
    lines.append(f"- Net Profit (reported): {fin.get('net_profit',0)} {fin.get('currency','GTA$')}")
    lines.append("")
    lines.append("## Bonus Activities — Detected & Estimated Impact")
    if not summary:
        lines.append("- No bonus activities detected this week.")
    else:
        for s in summary:
            lines.append(f"- {s['name']}")
            lines.append(f"  - Multiplier: {s['multiplier']} — Count: {s['count']} — Base proxy: ${s['base']}")
            lines.append(f"  - Est Gross Lift: ${s['est_gross_lift']:,} — Est Cost: ${s['est_cost']:,} — Est Net: ${s['est_net']:,}")
            lines.append(f"  - Priority: {s['priority']} — Notes: {s['notes']}")

    lines.append("")
    lines.append("## Activity Ranking & Recommendations (bonus-aware)")
    if summary:
        lines.append("- Prioritize bonus activities marked `Priority` or `High`. Consider reallocating time/resources for these.")
    else:
        lines.append("- No bonus-driven priority changes recommended.")

    lines.append("")
    lines.append("---")
    lines.append("Michael (Strategic & Financial Analyst) — Bonus Activity analysis included.")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text('\n'.join(lines), encoding='utf-8')
    print(f"Michael report written to {OUT}")


if __name__ == '__main__':
    generate()
