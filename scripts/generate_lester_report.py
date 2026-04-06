#!/usr/bin/env python3
"""
Aggregate available weekly agent reports into a single Lester report.

This script looks for markdown files under `reports/`, excluding its own output,
and concatenates them into a consolidated weekly summary file.

Run:
  python scripts/generate_lester_report.py
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / 'reports'
OUT = REPORTS / 'report_lester_week_sample.md'


def list_report_sources():
    return sorted([p for p in REPORTS.glob('*.md') if p.name != OUT.name])


def gather():
    sources = list_report_sources()
    parts = []
    parts.append('# Lester Consolidated Weekly Report')
    parts.append('')
    parts.append('## Executive Summary')
    parts.append('- Consolidated insights from all available agent reports.')
    if sources:
        parts.append(f'- Reports included: {", ".join([p.name for p in sources])}.')
    else:
        parts.append('- No agent reports found in the reports directory.')
    parts.append('')

    if sources:
        parts.append('## Report Sources')
        for p in sources:
            parts.append(f'- {p.name}')
        parts.append('')

    for path in sources:
        parts.append(f'### Source: {path.name}')
        parts.append('')
        content = path.read_text(encoding='utf-8')
        parts.append(content)
        parts.append('')

    parts.append('## Consolidated Action Items')
    if sources:
        parts.append('- Review Franklin vehicle recommendations and exclude Removed vehicles.')
        parts.append("- Prioritize Michael's high net-lift Bonus activities where cost < expected lift.")
        parts.append('- Tony: verify nightclub cash flow spikes and warehouse stock with ops team.')
        parts.append('- Trevor: schedule top entertainment picks if acceptable risk profile.')
        parts.append('- Lamar: use Salvage Yard Robberies to boost crew cohesion and vehicle utility.')
    else:
        parts.append('- No agent reports available. Generate all individual reports first.')
    parts.append('')

    OUT.write_text('\n'.join(parts), encoding='utf-8')
    print(f'Lester report written to {OUT}')


if __name__ == '__main__':
    gather()
