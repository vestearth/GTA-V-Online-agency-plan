#!/usr/bin/env python3
"""
Generate Lamar's crew and salvage yard report from weekly activity JSON.
Writes Markdown report to `reports/report_lamar_week_sample.md`.

Run:
  python scripts/generate_lamar_report.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WEEKLY = ROOT / 'data' / 'weekly_activity_apr2-9.json'
OUT = ROOT / 'reports' / 'report_lamar_week_sample.md'


def load(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def analyze_salvage(weekly):
    salvage = weekly.get('salvage_yard_robberies', [])
    if not salvage:
        return ['- No Salvage Yard Robberies data available this week.']

    lines = ['- Salvage Yard Robberies detected:']
    high_value = []
    for entry in salvage:
        robbery = entry.get('robbery', 'Unknown robbery')
        vehicle = entry.get('vehicle', 'Unknown vehicle')
        lines.append(f"  - {robbery}: {vehicle}")
        high_value.append(vehicle)

    lines.append('- Recommended vehicle watch list:')
    for vehicle in high_value:
        lines.append(f"  - {vehicle} — check value, crew transport use, and grab it if it fits the run.")

    lines.append('- Watch for salvage captures that can boost crew flexibility or squad style.')
    return lines


def get_mvp(weekly):
    crew = weekly.get('crew_summary', {})
    mvp = crew.get('mvp')
    if mvp and mvp != 'Unknown':
        return f"- This week’s MVP looks like {mvp}. Keep them in the rotation and give them props."
    return ['- MVP not explicitly set in the data; infer from mission/crew activity performance.']


def generate():
    weekly = load(WEEKLY)
    crew = weekly.get('crew_summary', {})
    salvage_lines = analyze_salvage(weekly)
    treasures = weekly.get('luxury_autos', [])

    lines = []
    lines.append(f"# Lamar's Crew & Salvage Yard Report — {weekly.get('week')}")
    lines.append("")
    lines.append("## Crew Snapshot")
    lines.append(f"- Active crew members: {crew.get('members_active', 'Unknown')}")
    lines.append(f"- Crew cohesion score: {crew.get('team_cohesion', 'Unknown')}/10")
    lines.append(f"- Crew MVP: {crew.get('mvp', 'Unknown')}")
    lines.append("- Crew conflicts detected: " + (', '.join(crew.get('conflicts', [])) if crew.get('conflicts') else 'None detected'))
    lines.append("")
    lines.append("## Salvage Yard Vehicle Watch")
    lines.extend(salvage_lines)

    if treasures:
        lines.append("")
        lines.append("## Luxury Auto Watchlist")
        for auto in treasures:
            lines.append(f"- {auto} — monitor if the crew wants a prestige ride or a valuable flip.")

    lines.append("")
    lines.append("## Crew Vibe & Recommendations")
    lines.append("- Keep the energy focused. Salvage vehicles are a good excuse to regroup and secure loot together.")
    lines.append("- If crew cohesion is low, plan a quick salvage run or neighborhood event to rebuild momentum.")
    lines.append("- High-value salvage vehicles should be assessed for utility first: transport, show, or sell.")
    lines.append("")
    lines.append("## MVP Notes")
    if isinstance(get_mvp(weekly), list):
        lines.extend(get_mvp(weekly))
    else:
        lines.append(get_mvp(weekly))

    lines.append("")
    lines.append("---")
    lines.append("Lamar (Social, Crew & Vehicle Watch Analyst) — Monitoring crew dynamics and salvage vehicle opportunities.")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text('\n'.join(lines), encoding='utf-8')
    print(f"Lamar report written to {OUT}")


if __name__ == '__main__':
    generate()
