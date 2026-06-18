#!/usr/bin/env python3
"""Run the weekly content refresh pipeline from source URL to dashboard artifacts."""

from __future__ import annotations

import argparse
import datetime as dt
import subprocess
import sys
import json
from pathlib import Path

try:
    from resolve_weekly_update_source import resolve_weekly_update_url
except ModuleNotFoundError:
    from scripts.resolve_weekly_update_source import resolve_weekly_update_url


ROOT = Path(__file__).resolve().parents[1]


def current_week_id() -> str:
    today = dt.date.today()
    days_since_thursday = (today.weekday() - 3) % 7
    start_date = today - dt.timedelta(days=days_since_thursday)
    year, week_num, _ = start_date.isocalendar()
    return f"{year}-W{week_num:02d}"


def weekly_payload_path(week_id: str) -> Path:
    return ROOT / "data" / f"weekly_planning_{week_id.replace('-', '_').lower()}.json"


def master_plan_path(week_id: str) -> Path:
    return ROOT / "reports" / f"weekly_master_plan_{week_id.replace('-', '_').lower()}.md"


def validate_weekly_payload_has_content(payload: dict) -> None:
    weekly_content = payload.get("weekly_content", {}) if isinstance(payload, dict) else {}
    content_fields = (
        "bonuses",
        "events",
        "discounts",
        "vehicle_opportunities",
        "salvage_yard_robberies",
    )
    if not any(weekly_content.get(field) for field in content_fields):
        raise ValueError(
            "Scraped weekly payload has no detected bonuses, events, discounts, vehicles, or robberies"
        )


def run_step(command: list[str], *, allow_failure: bool = False) -> int:
    print(f"+ {' '.join(command)}", flush=True)
    completed = subprocess.run(command, cwd=ROOT)
    if completed.returncode and not allow_failure:
        raise subprocess.CalledProcessError(completed.returncode, command)
    return completed.returncode


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Refresh GTA Online weekly content artifacts.")
    parser.add_argument("--url", help="Explicit Rockstar Newswire article URL.")
    parser.add_argument("--env-var", default="WEEKLY_UPDATE_URL", help="Environment variable fallback for the article URL.")
    parser.add_argument("--newswire-url", default="https://www.rockstargames.com/newswire", help="Newswire listing URL for auto-discovery.")
    parser.add_argument("--no-overwrite", action="store_true", help="Do not overwrite an existing weekly payload.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        source_url = resolve_weekly_update_url(
            direct_url=args.url,
            env_var=args.env_var,
            newswire_url=args.newswire_url,
        )
        print(f"weekly source: {source_url}", flush=True)
        week_id = current_week_id()
        weekly_path = weekly_payload_path(week_id)
        previous_payload = weekly_path.read_bytes() if weekly_path.exists() else None

        scrape_command = ["python3", "scripts/scrape_weekly_update.py", "--url", source_url]
        if not args.no_overwrite:
            scrape_command.append("--overwrite")
        run_step(scrape_command)

        if not weekly_path.exists():
            raise FileNotFoundError(f"Expected weekly payload was not generated: {weekly_path}")
        try:
            validate_weekly_payload_has_content(json.loads(weekly_path.read_text(encoding="utf-8")))
        except ValueError:
            if previous_payload is None:
                weekly_path.unlink(missing_ok=True)
            else:
                weekly_path.write_bytes(previous_payload)
            raise

        run_step(["python3", "scripts/generate_weekly_report.py", str(weekly_path.relative_to(ROOT))])
        run_step(["python3", "scripts/update_vehicle_prices.py", "--weekly", str(weekly_path.relative_to(ROOT))])
        run_step(["python3", "scripts/fetch_gtacar_prices.py", "--fail-on-skipped"])
        master_path = master_plan_path(week_id)
        if not master_path.exists():
            raise FileNotFoundError(
                "Expected weekly master plan before dashboard refresh: "
                f"{master_path.relative_to(ROOT)}"
            )

        run_step(["python3", "scripts/generate_dashboard.py", "--weekly", str(weekly_path.relative_to(ROOT))])
        run_step(["python3", "scripts/generate_pixel_dashboard.py", "--weekly", str(weekly_path.relative_to(ROOT))])
    except (FileNotFoundError, subprocess.CalledProcessError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
