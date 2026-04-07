#!/usr/bin/env python3
"""Shared helpers for schema v2 report generators."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_WEEKLY = ROOT / "data" / "schema_v2_example.json"
REPORTS_DIR = ROOT / "reports"
STRUCTURED_DIR = REPORTS_DIR / "structured"
AGENT_DOCS_DIR = ROOT / "agents" / "docs"
AGENT_DATA_DIR = ROOT / "agents" / "data"


def load_json(path: Path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def load_yaml(path: Path):
    with open(path, "r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def dump_json(path: Path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def load_weekly(path: str | Path | None = None):
    weekly_path = Path(path) if path else DEFAULT_WEEKLY
    payload = load_json(weekly_path)
    return weekly_path, payload


def normalize_lookup_key(value):
    if value is None:
        return ""
    return re.sub(r"[^a-z0-9]+", "_", str(value).casefold()).strip("_")


def load_agent_doc(name: str):
    path = AGENT_DOCS_DIR / f"{name}.yaml"
    if not path.exists():
        return None
    return load_yaml(path)


def load_agent_data(name: str):
    path = AGENT_DATA_DIR / f"{name}.json"
    if not path.exists():
        return None
    return load_json(path)


def validate_records_against_schema(records, schema):
    errors = []
    if not isinstance(records, list):
        return ["Reference dataset is not a list."]
    if not isinstance(schema, dict):
        return ["Schema file is missing or invalid."]

    properties = schema.get("properties", {})
    required = schema.get("required", [])
    type_checks = {
        "string": str,
        "array": list,
        "object": dict,
    }

    for index, record in enumerate(records, start=1):
        if not isinstance(record, dict):
            errors.append(f"Record {index}: expected object, got {type(record).__name__}.")
            continue
        for field in required:
            if field not in record:
                errors.append(f"Record {index}: missing required field '{field}'.")
        for field, value in record.items():
            definition = properties.get(field)
            if not definition:
                continue
            expected_type = definition.get("type")
            if expected_type in type_checks and not isinstance(value, type_checks[expected_type]):
                errors.append(
                    f"Record {index}: field '{field}' should be {expected_type}, got {type(value).__name__}."
                )
                continue
            enum = definition.get("enum")
            if enum and value not in enum:
                errors.append(f"Record {index}: field '{field}' has unsupported value '{value}'.")
    return errors


def load_franklin_brand_reference():
    brands_doc = load_agent_doc("franklin") or {}
    schema = load_agent_doc("brand.schema") or {}
    brands = brands_doc.get("brands", []) if isinstance(brands_doc, dict) else []
    validation_errors = validate_records_against_schema(brands, schema)
    return {
        "brands": brands,
        "schema": schema,
        "validation_errors": validation_errors,
    }


def match_vehicle_brand(vehicle_name, brands):
    vehicle_key = str(vehicle_name or "").casefold()
    best_match = None
    for entry in brands:
        brand_name = str(entry.get("name") or "").strip()
        if not brand_name:
            continue
        if vehicle_key.startswith(brand_name.casefold()):
            if best_match is None or len(brand_name) > len(best_match.get("name", "")):
                best_match = entry
    return best_match


def load_tony_support_data():
    reference_doc = load_agent_doc("tony") or {}
    runtime_data = load_agent_data("tony") or {}
    goods = runtime_data.get("goods", []) if isinstance(runtime_data, dict) else []
    catalog = {}
    for entry in goods:
        normalized_keys = {
            normalize_lookup_key(entry.get("id")),
            normalize_lookup_key(entry.get("name")),
        }
        normalized_keys.discard("")
        for key in normalized_keys:
            catalog[key] = entry
    return {
        "reference": reference_doc,
        "runtime": runtime_data,
        "goods_catalog": catalog,
        "goods": goods,
    }


def lookup_tony_goods_entry(catalog, goods_type):
    return catalog.get(normalize_lookup_key(goods_type))


def load_agent14_reference():
    return load_agent_doc("agent14-cayo") or {}


def detect_cayo_perico_entry(entry):
    haystack = " ".join(
        str(entry.get(key) or "")
        for key in ("id", "name", "notes")
    ).casefold()
    return "cayo" in haystack or "perico" in haystack


def session_plan_player_count(payload):
    session_plan = payload.get("planning_context", {}).get("session_plan", [])
    if any(block.get("party_size") == "full_crew" for block in session_plan):
        return 4
    if any(block.get("party_size") == "1_2_friends" for block in session_plan):
        return 2
    return 1


def cayo_reference_summary(reference_doc, player_count):
    cayo = reference_doc.get("cayo_perico", {}) if isinstance(reference_doc, dict) else {}
    if not cayo:
        return None
    maximum = cayo.get("maximum", {})
    players = maximum.get("players", {})
    player_entry = players.get(player_count) or players.get(str(player_count))
    if not player_entry:
        return None
    return {
        "player_count": player_count,
        "leader_net": player_entry.get("leader_net"),
        "team_net": player_entry.get("net"),
        "setup_fee": cayo.get("setup_fee"),
        "safe": maximum.get("safe"),
        "primary": maximum.get("primary"),
    }


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
