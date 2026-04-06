#!/usr/bin/env python3
"""Shared helpers for schema v2 report generators."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_WEEKLY = ROOT / "data" / "schema_v2_example.json"
REPORTS_DIR = ROOT / "reports"
STRUCTURED_DIR = REPORTS_DIR / "structured"


def load_json(path: Path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def dump_json(path: Path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def load_weekly(path: str | Path | None = None):
    weekly_path = Path(path) if path else DEFAULT_WEEKLY
    payload = load_json(weekly_path)
    return weekly_path, payload


def utc_now_iso():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def week_label(payload):
    week = payload.get("week", {})
    return week.get("label") or week.get("id") or "Unknown Week"


def player_assets(payload):
    owned = payload.get("player_context", {}).get("owned_assets", {})
    return set(owned.get("properties", [])) | set(owned.get("businesses", []))


def missing_requirements(payload, requirements):
    owned = player_assets(payload)
    return [item for item in requirements if item not in owned]


def is_limited(entry):
    availability = entry.get("availability", {})
    return bool(entry.get("limited")) or bool(availability.get("end"))


def top_n(items, size):
    return items[:size] if len(items) > size else items


def build_report_payload(agent, payload, summary, recommendations, warnings=None, insufficient_data=None, extra=None):
    report = {
        "agent": agent,
        "schema_version": payload.get("schema_version", "2.0"),
        "week_id": payload.get("week", {}).get("id"),
        "week_label": week_label(payload),
        "generated_at": utc_now_iso(),
        "summary": summary,
        "top_recommendations": recommendations,
        "warnings": warnings or [],
        "insufficient_data": insufficient_data or [],
    }
    if extra:
        report.update(extra)
    return report


def write_agent_outputs(agent, payload, report_payload, markdown_lines, markdown_name, json_name):
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    STRUCTURED_DIR.mkdir(parents=True, exist_ok=True)
    markdown_path = REPORTS_DIR / markdown_name
    json_path = STRUCTURED_DIR / json_name
    markdown_path.write_text("\n".join(markdown_lines) + "\n", encoding="utf-8")
    dump_json(json_path, report_payload)
    return markdown_path, json_path


def recommendation(target_id, action, reason, confidence="medium", score=None, blockers=None):
    item = {
        "target_id": target_id,
        "action": action,
        "reason": reason,
        "confidence": confidence,
    }
    if score is not None:
        item["score"] = round(score, 2)
    if blockers:
        item["blockers"] = blockers
    return item
