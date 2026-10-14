#!/usr/bin/env python3
"""Curated-first intake: persist candidates; publish only an approved current report set."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

try:
    from scripts.resolve_weekly_update_source import resolve_weekly_update_url
    from scripts.content_safety import (coverage_issues, reset_window, week_id, publication_issues,
                                        insert_freshness, write_json, utc_now, displayed_payload)
except ModuleNotFoundError:
    from resolve_weekly_update_source import resolve_weekly_update_url
    from content_safety import (coverage_issues, reset_window, week_id, publication_issues,
                                insert_freshness, write_json, utc_now, displayed_payload)

ROOT = Path(__file__).resolve().parents[1]


def current_week_id():
    return week_id(reset_window()[0])


def weekly_payload_path(identifier):
    return ROOT / "data" / f"weekly_planning_{identifier.replace('-', '_').lower()}.json"


def master_plan_path(identifier):
    return ROOT / "reports" / f"weekly_master_plan_{identifier.replace('-', '_').lower()}.md"


def validate_weekly_payload_has_content(payload):
    issues = coverage_issues(payload)
    if issues:
        raise ValueError("; ".join(issues))


def run_step(command, *, allow_failure=False):
    print(f"+ {' '.join(command)}", flush=True)
    completed = subprocess.run(command, cwd=ROOT)
    if completed.returncode and not allow_failure:
        raise subprocess.CalledProcessError(completed.returncode, command)
    return completed.returncode


def mark_retained_dashboards(reason):
    # Keep headers and recommendations together, and make retained data age visible.
    for name in ("dashboard.html", "pixel-dashboard.html"):
        path = ROOT / name
        if path.exists():
            text = path.read_text(encoding="utf-8")
            payload = displayed_payload(ROOT, text, "pixel_header_meta" if name.startswith("pixel") else "header_meta")
            path.write_text(insert_freshness(text, payload, reason), encoding="utf-8")


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", help="Explicit Rockstar weekly article; still date/title/body validated")
    parser.add_argument("--env-var", default="WEEKLY_UPDATE_URL")
    parser.add_argument("--no-overwrite", action="store_true", help="Retain existing candidate")
    parser.add_argument("--publish-reviewed", action="store_true", help="Publish current approved payload without fetching")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    identifier = current_week_id()
    canonical = weekly_payload_path(identifier)
    candidate = canonical.parent / "candidates" / canonical.name
    status_path = ROOT / "data/refresh_status.json"
    status = {"week_id": identifier, "checked_at": utc_now().isoformat(),
              "state": "acquiring", "published": False}
    try:
        if not args.publish_reviewed:
            source = resolve_weekly_update_url(direct_url=args.url, env_var=args.env_var)
            status["source_url"] = source
            command = [sys.executable, "scripts/scrape_weekly_update.py", "--url", source]
            if not args.no_overwrite:
                command.append("--overwrite")
            run_step(command)
            if not candidate.exists():
                raise ValueError("Intake did not create candidate")
            payload = json.loads(candidate.read_text(encoding="utf-8"))
            status["state"] = "needs_review"
            status["candidate"] = str(candidate.relative_to(ROOT)).replace("\\", "/")
            status["issues"] = coverage_issues(payload)
            if canonical.exists():
                approved = json.loads(canonical.read_text(encoding="utf-8"))
                if approved.get("provenance", {}).get("article_sha256") != payload.get("provenance", {}).get("article_sha256"):
                    status["issues"].append("Source changed since approval")
            else:
                approved = {}
            issues = status["issues"] + (publication_issues(approved, ROOT) if approved
                                         else ["Current approved payload and three-report handoff missing"])
            if issues:
                status["issues"] = list(dict.fromkeys(issues))
                mark_retained_dashboards("needs_review · new candidate pending")
                print("needs_review: candidate saved; publication withheld", flush=True)
                return 0
        else:
            if not canonical.exists():
                raise ValueError("No current reviewed payload; run intake and review first")
            approved = json.loads(canonical.read_text(encoding="utf-8"))
            issues = publication_issues(approved, ROOT)
            if issues:
                raise ValueError("; ".join(issues))
        status["state"] = "generating"
        run_step([sys.executable, "scripts/update_vehicle_prices.py", "--weekly", str(canonical)])
        status["price_exit_code"] = run_step(
            [sys.executable, "scripts/fetch_gtacar_prices.py", "--weekly", str(canonical),
             "--summary", "data/price_refresh_status.json"], allow_failure=True)
        staged = []
        for script, name in (("generate_dashboard.py", "dashboard.html"),
                             ("generate_pixel_dashboard.py", "pixel-dashboard.html")):
            output = ROOT / (name + ".tmp")
            run_step([sys.executable, f"scripts/{script}", "--weekly", str(canonical), "--output", str(output)])
            staged.append((output, ROOT / name))
        for output, target in staged:
            output.replace(target)
        status.update(state="published", published=True, published_at=utc_now().isoformat())
        return 0
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        status.update(state="failed", issues=[str(exc)])
        mark_retained_dashboards("needs_review · refresh failed")
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    finally:
        write_json(status_path, status)
        print(json.dumps(status, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    raise SystemExit(main())
