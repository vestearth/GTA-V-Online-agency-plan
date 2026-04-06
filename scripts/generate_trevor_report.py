#!/usr/bin/env python3
"""
Generate a simple Trevor entertainment/risk report from weekly activity JSON.
Writes Markdown report to `reports/report_trevor_week_sample.md`.

Run:
  python scripts/generate_trevor_report.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WEEKLY = ROOT / 'data' / 'weekly_activity_apr2-9.json'
OUT = ROOT / 'reports' / 'report_trevor_week_sample.md'


def load(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def score_activity(a):
    # crude entertainment score: prefer races, test rides, premium
    name = (a.get('name') or '').lower()
    if 'race' in name or 'premium' in name:
        return 8
    if 'test ride' in name or 'time trial' in name:
        return 6
    if 'bonus' in name:
        return 4
    return 3


def format_discount_line(entry):
    if isinstance(entry, dict):
        item = entry.get('item')
        discount = entry.get('discount')
        return f"- {item}: {discount}"
    return f"- {entry}"


def generate():
    weekly = load(WEEKLY)
    activities = weekly.get('activities', [])

    scored = []
    for a in activities:
        s = score_activity(a)
        scored.append((s, a))

    scored.sort(key=lambda x: x[0], reverse=True)

    lines = []
    lines.append(f"# Trevor's Entertainment & Risk Report — {weekly.get('week')}")
    lines.append("")
    lines.append("## Top Entertainment Picks")
    for score, a in scored[:6]:
        lines.append(f"- {a.get('name')} — Entertainment Score: {score} — Notes: {a.get('notes','')}")

    lines.append("")
    lines.append("## Risk Notes & Warnings")
    lines.append("- Watch for high-risk activities with high entertainment score. Balance thrills vs. survival.")

    lines.append("")
    lines.append("## Gun Van Stock & Discounts")
    gun_van = weekly.get('gun_van', {})
    gun_van_discounts = weekly.get('gun_van_discounts', {})

    if gun_van:
        lines.append(f"- Location: {gun_van.get('location', 'Unknown')}")
        stock = gun_van.get('stock', [])
        if stock:
            lines.append("- Current gun van stock:")
            for item in stock:
                item_name = item.get('item')
                discount = item.get('discount')
                gta_plus = item.get('gta_plus_discount')
                if gta_plus and gta_plus != discount:
                    lines.append(f"  - {item_name}: {discount} (GTA+ {gta_plus})")
                else:
                    lines.append(f"  - {item_name}: {discount}")
        else:
            lines.append("- No detailed stock list available.")
    else:
        lines.append("- Gun Van section missing in weekly data.")

    if gun_van_discounts:
        free = gun_van_discounts.get('free', [])
        free_plus = gun_van_discounts.get('free_for_gta_plus_members', [])
        discounts = gun_van_discounts.get('discounts', [])

        if free:
            lines.append("- Free Gun Van items:")
            for item in free:
                lines.append(f"  - {item}")
        if free_plus:
            lines.append("- Free for GTA+ members:")
            for item in free_plus:
                lines.append(f"  - {item}")
        if discounts:
            lines.append("- Discounted Gun Van items:")
            for entry in discounts:
                lines.append(f"  - {entry.get('item')}: {entry.get('discount')}")
    else:
        lines.append("- No gun van discounts listed.")

    lines.append("")
    lines.append("## Gun Van Quick Recommendations")
    lines.append("- Pick up free items first: Nightstick, Baseball Bat. If GTA+ applies, claim the Stun Gun too.")
    lines.append("- Heavy Rifle is top discounted pay item. Buy Body Armor only if GTA+ and if you need survivability.")
    lines.append("- Avoid buying purely cosmetic gear unless you have extra cash after essentials.")

    lines.append("")
    lines.append("---")
    lines.append("Trevor (Chaos & Risk Analyst) — Quick picks and warnings for fun and chaos.")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text('\n'.join(lines), encoding='utf-8')
    print(f"Trevor report written to {OUT}")


if __name__ == '__main__':
    generate()
