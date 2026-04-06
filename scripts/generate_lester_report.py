#!/usr/bin/env python3
"""
Aggregate Michael, Franklin, Tony, and Trevor reports into a single Lester report.

This script looks for markdown files under `reports/` with expected names and
concatenates them into a consolidated executive summary file.

Run:
  python scripts/generate_lester_report.py
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / 'reports'
OUT = REPORTS / 'report_lester_week_sample.md'

SOURCES = [
    'franklin_report_from_weekly.md',
    'report_michael_week_sample.md',
    'report_tony_week_sample.md',
    'report_trevor_week_sample.md',
    'report_lamar_week_sample.md',
]


def gather():
    parts = []
    parts.append('# Lester Consolidated Weekly Report')
    parts.append('')
    parts.append('## Executive Summary')
    parts.append('- Combined insights from Franklin, Michael, Tony, Trevor, and Lamar.')
    parts.append('')

    for name in SOURCES:
        path = REPORTS / name
        if not path.exists():
            parts.append(f'### {name} — Missing')
            parts.append(f'- Report `{name}` not found.')
            parts.append('')
            continue

        parts.append(f'### Source: {name}')
        parts.append('')
        content = path.read_text(encoding='utf-8')
        parts.append(content)
        parts.append('')

    parts.append('## Consolidated Action Items')
    parts.append('- Review Franklin vehicle recommendations and exclude Removed vehicles.')
    parts.append("- Prioritize Michael's high net-lift Bonus activities where cost < expected lift.")
    parts.append('- Tony: verify nightclub cash flow spikes and warehouse stock with ops team.')
    parts.append('- Trevor: schedule top entertainment picks if acceptable risk profile.')
    parts.append('')

    OUT.write_text('\n'.join(parts), encoding='utf-8')
    print(f'Lester report written to {OUT}')


if __name__ == '__main__':
    gather()
