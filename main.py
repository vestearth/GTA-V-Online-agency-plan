"""
GTA V AI Agent Orchestrator
============================
Runs all (or selected) character agents against a week's activity data and
produces a structured weekly report.

Usage
-----
  python main.py                          # uses data/sample_week.json
  python main.py --data path/to/data.json
  python main.py --agents lester,michael  # run specific agents only
  python main.py --output reports/        # save report to directory

Environment variables
---------------------
  OPENAI_API_KEY   – your OpenAI key (leave blank for offline/demo mode)
  LLM_MODEL        – model name (default: gpt-4o-mini)
  LLM_TEMPERATURE  – temperature 0-2 (default: 0.7)
  ENABLED_AGENTS   – comma-separated agent names or "all"
  REPORTS_DIR      – directory to save reports (default: reports)
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from agents import (
    Agent14Agent,
    EnglishDaveAgent,
    FranklinAgent,
    LamarAgent,
    LesterAgent,
    MichaelAgent,
    RonAgent,
    TrevorAgent,
)
from agents.base_agent import BaseAgent
from config import ENABLED_AGENTS, REPORTS_DIR

# --------------------------------------------------------------------- #
# Registry: maps slug → agent class                                     #
# --------------------------------------------------------------------- #
AGENT_REGISTRY: dict[str, type[BaseAgent]] = {
    "michael": MichaelAgent,
    "trevor": TrevorAgent,
    "franklin": FranklinAgent,
    "lester": LesterAgent,
    "ron": RonAgent,
    "lamar": LamarAgent,
    "english_dave": EnglishDaveAgent,
    "agent14": Agent14Agent,
}

# Recommended order: coordinator first, then specialists, then narrator last
DEFAULT_ORDER: list[str] = [
    "lester",
    "michael",
    "franklin",
    "trevor",
    "lamar",
    "english_dave",
    "agent14",
    "ron",
]


# --------------------------------------------------------------------- #
# Helpers                                                                #
# --------------------------------------------------------------------- #

def load_weekly_data(path: str) -> dict[str, Any]:
    """Load weekly activity JSON from *path*."""
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def resolve_agents(requested: list[str]) -> list[BaseAgent]:
    """Return instantiated agents, filtered and ordered."""
    use_all = not requested or requested == ["all"]
    order = DEFAULT_ORDER if use_all else requested

    agents: list[BaseAgent] = []
    for slug in order:
        if slug not in AGENT_REGISTRY:
            print(f"[WARNING] Unknown agent '{slug}' – skipping.", file=sys.stderr)
            continue
        if not use_all and slug not in requested:
            continue
        agents.append(AGENT_REGISTRY[slug]())
    return agents


def run_agents(
    agents: list[BaseAgent],
    weekly_data: dict[str, Any],
) -> dict[str, str]:
    """Run each agent and collect its analysis."""
    results: dict[str, str] = {}
    for agent in agents:
        print(f"  → {agent.name} กำลังวิเคราะห์…")
        results[agent.name] = agent.analyze(weekly_data)
    return results


def format_report(
    weekly_data: dict[str, Any],
    results: dict[str, str],
) -> str:
    """Assemble the full report as a Markdown string."""
    week_label = weekly_data.get("week", "N/A")
    lines: list[str] = [
        f"# รายงานประจำสัปดาห์ GTA V Online",
        f"**สัปดาห์:** {week_label}  ",
        f"**สร้างเมื่อ:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "---",
        "",
    ]

    for agent_name, analysis in results.items():
        lines += [
            f"## 🎮 {agent_name}",
            "",
            analysis,
            "",
            "---",
            "",
        ]

    return "\n".join(lines)


def save_report(content: str, output_dir: str, week_label: str) -> str:
    """Write the report to *output_dir* and return the file path."""
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    safe_week = week_label.replace(" ", "_").replace("/", "-")
    filename = f"report_{safe_week}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    filepath = os.path.join(output_dir, filename)
    with open(filepath, "w", encoding="utf-8") as fh:
        fh.write(content)
    return filepath


# --------------------------------------------------------------------- #
# CLI                                                                    #
# --------------------------------------------------------------------- #

def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="GTA V AI Agent – Weekly Activity Analyzer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--data",
        default="data/sample_week.json",
        help="Path to the weekly activity JSON file (default: data/sample_week.json)",
    )
    parser.add_argument(
        "--agents",
        default=",".join(ENABLED_AGENTS),
        help=(
            "Comma-separated agent slugs to run, or 'all'. "
            f"Available: {', '.join(AGENT_REGISTRY)}. "
            "(default: all)"
        ),
    )
    parser.add_argument(
        "--output",
        default=REPORTS_DIR,
        help="Directory to save the Markdown report (default: reports)",
    )
    parser.add_argument(
        "--no-save",
        action="store_true",
        help="Print the report to stdout instead of saving to a file",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    # ── Load data ──────────────────────────────────────────────────────
    if not os.path.exists(args.data):
        print(f"[ERROR] Data file not found: {args.data}", file=sys.stderr)
        print("  Create it or point --data at a valid JSON file.", file=sys.stderr)
        return 1

    print(f"📂 โหลดข้อมูลจาก: {args.data}")
    weekly_data = load_weekly_data(args.data)
    week_label = weekly_data.get("week", "unknown")
    print(f"📅 สัปดาห์: {week_label}")

    # ── Resolve agents ──────────────────────────────────────────────────
    requested = [a.strip() for a in args.agents.split(",") if a.strip()]
    agents = resolve_agents(requested)
    if not agents:
        print("[ERROR] ไม่พบ agent ที่ต้องการ", file=sys.stderr)
        return 1

    print(f"\n🤖 เริ่มวิเคราะห์ด้วย {len(agents)} agents:\n")

    # ── Run agents ──────────────────────────────────────────────────────
    results = run_agents(agents, weekly_data)

    # ── Format & output ─────────────────────────────────────────────────
    report = format_report(weekly_data, results)

    if args.no_save:
        print("\n" + report)
    else:
        filepath = save_report(report, args.output, week_label)
        print(f"\n✅ บันทึกรายงานไปที่: {filepath}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
