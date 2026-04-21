#!/usr/bin/env python3
"""Sync vehicle reference entries from weekly planning data.

This script updates `data/references/vehicle_prices.yaml` by:
1) reading vehicle names from a weekly JSON payload,
2) ensuring every vehicle has a record in the YAML file,
3) auto-adding manufacturer-stripped alias hints,
4) updating `last_verified_at`,
5) printing a null-price report.

It uses only Python standard library.
"""

from __future__ import annotations

import argparse
import datetime as dt
import glob
import json
import re
import sys
from pathlib import Path


def discover_latest_weekly(data_dir: Path) -> Path:
    candidates = [Path(p) for p in glob.glob(str(data_dir / "weekly_planning_*.json"))]
    if not candidates:
        raise FileNotFoundError("No weekly_planning_*.json found in data/")
    return max(candidates, key=lambda p: p.stat().st_mtime)


def load_vehicle_names(weekly_path: Path) -> list[str]:
    payload = json.loads(weekly_path.read_text(encoding="utf-8"))
    opportunities = (
        payload.get("weekly_content", {}).get("vehicle_opportunities", [])
        if isinstance(payload, dict)
        else []
    )
    names: list[str] = []
    for item in opportunities:
        name = (item or {}).get("vehicle_name")
        if isinstance(name, str) and name.strip():
            names.append(name.strip())
    # stable unique
    out: list[str] = []
    seen: set[str] = set()
    for n in names:
        if n not in seen:
            seen.add(n)
            out.append(n)
    return out


def collect_weekly_removed_map(data_dir: Path) -> dict[str, set[str]]:
    removed_map: dict[str, set[str]] = {}
    for p in [Path(x) for x in glob.glob(str(data_dir / "weekly_planning_*.json"))]:
        try:
            payload = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        week_id = (payload.get("week") or {}).get("id")
        if not isinstance(week_id, str) or not week_id:
            continue
        opportunities = (payload.get("weekly_content") or {}).get("vehicle_opportunities") or []
        for item in opportunities:
            name = (item or {}).get("vehicle_name")
            is_removed = bool((item or {}).get("removed_vehicle"))
            if not isinstance(name, str) or not name.strip() or not is_removed:
                continue
            removed_map.setdefault(name.strip(), set()).add(week_id)
    return removed_map


def stripped_alias(name: str) -> str | None:
    parts = name.replace("–", "-").split()
    if len(parts) <= 1:
        return None
    return " ".join(parts[1:])


def infer_vehicle_tier(name: str, removed: bool) -> str:
    lowered = name.lower()
    if removed:
        return "collector"
    utility_tokens = [
        "cruiser",
        "interceptor",
        "pursuit",
        "patrol",
        "police",
        "unmarked",
        "park ranger",
    ]
    special_tokens = ["tank", "trailer", "festival bus", "bus"]
    if any(tok in lowered for tok in utility_tokens):
        return "utility"
    if any(tok in lowered for tok in special_tokens):
        return "special"
    return "unrated"


def load_tier_overrides(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    overrides = payload.get("vehicle_tier_overrides", {})
    if not isinstance(overrides, dict):
        return {}
    allowed = payload.get("allowed_tiers")
    allowed_set: set[str] | None = None
    if isinstance(allowed, list) and all(isinstance(x, str) for x in allowed):
        allowed_set = {x.strip() for x in allowed if x.strip()}
    result: dict[str, str] = {}
    for k, v in overrides.items():
        if isinstance(k, str) and isinstance(v, str) and k.strip() and v.strip():
            tier = v.strip()
            if allowed_set is not None and tier not in allowed_set:
                print(
                    f"warning: tier override for {k.strip()!r} has invalid tier {tier!r} "
                    f"(allowed: {sorted(allowed_set)})",
                    file=sys.stderr,
                )
                continue
            result[k.strip()] = tier
    return result


def normalize_race_class_name(raw: str) -> str:
    s = raw.strip().lower().replace("-", "_")
    s = re.sub(r"\s+", "_", s)
    return s


def load_race_tiers(path: Path) -> dict[str, dict[str, str]]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    race_tiers = payload.get("race_tiers", {})
    if not isinstance(race_tiers, dict):
        return {}
    tier_scale = payload.get("tier_scale")
    allowed_tiers: set[str] | None = None
    if isinstance(tier_scale, list) and all(isinstance(x, str) for x in tier_scale):
        allowed_tiers = {x.strip() for x in tier_scale if x.strip()}
    out: dict[str, dict[str, str]] = {}
    for vehicle_name, class_map in race_tiers.items():
        if not isinstance(vehicle_name, str) or not isinstance(class_map, dict):
            continue
        valid: dict[str, str] = {}
        for class_name, tier in class_map.items():
            if not isinstance(class_name, str) or not isinstance(tier, str):
                continue
            if not class_name.strip() or not tier.strip():
                continue
            norm_class = normalize_race_class_name(class_name)
            t = tier.strip()
            if allowed_tiers is not None and t not in allowed_tiers:
                print(
                    f"warning: race tier for {vehicle_name.strip()!r} class {norm_class!r} "
                    f"has invalid tier {t!r} (allowed: {sorted(allowed_tiers)})",
                    file=sys.stderr,
                )
                continue
            if norm_class != class_name.strip():
                print(
                    f"note: normalized race class {class_name.strip()!r} -> {norm_class!r} "
                    f"for vehicle {vehicle_name.strip()!r}",
                    file=sys.stderr,
                )
            valid[norm_class] = t
        if valid:
            out[vehicle_name.strip()] = valid
    return out


def quote_yaml_string(s: str) -> str:
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def parse_aliases(alias_line: str) -> list[str]:
    # expects: alias_hints: ["A", "B"]
    m = re.search(r"alias_hints:\s*\[(.*)\]\s*$", alias_line)
    if not m:
        return []
    raw = m.group(1).strip()
    if not raw:
        return []
    # split by ", " between quoted values
    values = re.findall(r'"((?:\\.|[^"])*)"', raw)
    return [v.replace('\\"', '"').replace("\\\\", "\\") for v in values]


def format_aliases(values: list[str]) -> str:
    return "alias_hints: [" + ", ".join(quote_yaml_string(v) for v in values) + "]"


def format_race_tiers(class_map: dict[str, str]) -> str:
    if not class_map:
        return "race_tiers: {}"
    ordered = sorted(class_map.items(), key=lambda x: x[0])
    inner = ", ".join(f"{k}: {quote_yaml_string(v)}" for k, v in ordered)
    return "race_tiers: {" + inner + "}"


def ensure_alias_in_block(block: list[str], alias: str) -> list[str]:
    if not alias:
        return block
    for i, line in enumerate(block):
        if "alias_hints:" not in line:
            continue
        existing = parse_aliases(line)
        if alias not in existing:
            existing.insert(0, alias)
            indent = line.split("alias_hints:")[0]
            block[i] = indent + format_aliases(existing)
        return block
    return block


def build_new_record(name: str) -> list[str]:
    alias = stripped_alias(name)
    aliases = [alias] if alias else []
    removed = False
    tier = infer_vehicle_tier(name, removed)
    return [
        f'  - vehicle_name: "{name}"',
        f'    vehicle_tier: "{tier}"',
        "    race_tiers: {}",
        f"    removed_vehicle: {str(removed).lower()}",
        "    removed_vehicle_weeks: []",
        "    base_price: null",
        "    trade_price: null",
        '    source_url: "https://gtacars.net"',
        "    " + format_aliases(aliases),
        "",
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description="Update vehicle_prices reference from weekly data.")
    parser.add_argument("--weekly", type=Path, help="Path to weekly_planning_*.json")
    parser.add_argument(
        "--prices",
        type=Path,
        default=Path("data/references/vehicle_prices.yaml"),
        help="Path to vehicle_prices.yaml",
    )
    parser.add_argument(
        "--tier-overrides",
        type=Path,
        default=Path("data/references/vehicle_tier_overrides.json"),
        help="Path to optional vehicle tier override JSON",
    )
    parser.add_argument(
        "--race-tiers",
        type=Path,
        default=Path("data/references/vehicle_race_tiers.json"),
        help="Path to optional per-class race tier JSON",
    )
    parser.add_argument("--dry-run", action="store_true", help="Show changes without writing files")
    args = parser.parse_args()

    prices_path = args.prices
    if not prices_path.exists():
        print(f"error: missing prices file: {prices_path}", file=sys.stderr)
        return 1

    weekly_path = args.weekly if args.weekly else discover_latest_weekly(Path("data"))
    vehicle_names = load_vehicle_names(weekly_path)
    removed_map = collect_weekly_removed_map(Path("data"))
    tier_overrides = load_tier_overrides(args.tier_overrides)
    race_tiers = load_race_tiers(args.race_tiers)
    if not vehicle_names:
        print(f"warning: no vehicle names found in {weekly_path}")
        return 0

    lines = prices_path.read_text(encoding="utf-8").splitlines()

    # update last_verified_at
    today = dt.date.today().isoformat()
    for i, line in enumerate(lines):
        if line.startswith("last_verified_at: "):
            lines[i] = f'last_verified_at: "{today}"'
            break

    # locate vehicle blocks
    start = None
    for i, line in enumerate(lines):
        if line.strip() == "vehicles:":
            start = i + 1
            break
    if start is None:
        print("error: vehicles section not found", file=sys.stderr)
        return 1

    block_starts: list[int] = []
    for i in range(start, len(lines)):
        if lines[i].startswith("  - vehicle_name: "):
            block_starts.append(i)

    records: dict[str, tuple[int, int]] = {}
    for idx, s in enumerate(block_starts):
        e = block_starts[idx + 1] if idx + 1 < len(block_starts) else len(lines)
        m = re.match(r'\s*-\s+vehicle_name:\s+"(.*)"\s*$', lines[s])
        if m:
            records[m.group(1)] = (s, e)

    added: list[str] = []
    # update aliases in existing blocks, from end to start so indexes stay valid
    for name, (s, e) in sorted(records.items(), key=lambda x: x[1][0], reverse=True):
        alias = stripped_alias(name)
        block = lines[s:e]
        new_block = ensure_alias_in_block(block, alias or "")
        # Ensure removed flags exist and are synchronized from weekly payloads
        weeks = sorted(removed_map.get(name, set()))
        removed_bool = "true" if weeks else "false"
        inferred_tier = infer_vehicle_tier(name, bool(weeks))
        chosen_tier = tier_overrides.get(name, inferred_tier)
        weeks_inline = ", ".join(quote_yaml_string(w) for w in weeks)
        weeks_line = f"    removed_vehicle_weeks: [{weeks_inline}]"
        # Ensure tier field exists and keep it useful:
        # - explicit override wins
        # - otherwise inferred tier upgrades "unrated"
        if any("vehicle_tier:" in ln for ln in new_block):
            for i, ln in enumerate(new_block):
                if "vehicle_tier:" in ln:
                    if name in tier_overrides:
                        new_block[i] = f'    vehicle_tier: "{chosen_tier}"'
                    elif '"unrated"' in ln and inferred_tier != "unrated":
                        new_block[i] = f'    vehicle_tier: "{inferred_tier}"'
                    break
        else:
            new_block.insert(1, f'    vehicle_tier: "{chosen_tier}"')
        race_map = race_tiers.get(name, {})
        race_line = "    " + format_race_tiers(race_map)
        if any("race_tiers:" in ln for ln in new_block):
            for i, ln in enumerate(new_block):
                if "race_tiers:" in ln:
                    new_block[i] = race_line
                    break
        else:
            new_block.insert(2, race_line)
        if any("removed_vehicle:" in ln for ln in new_block):
            for i, ln in enumerate(new_block):
                if "removed_vehicle:" in ln:
                    new_block[i] = f"    removed_vehicle: {removed_bool}"
                    break
        else:
            new_block.insert(2, f"    removed_vehicle: {removed_bool}")
        if any("removed_vehicle_weeks:" in ln for ln in new_block):
            for i, ln in enumerate(new_block):
                if "removed_vehicle_weeks:" in ln:
                    new_block[i] = weeks_line
                    break
        else:
            new_block.insert(3, weeks_line)
        lines[s:e] = new_block

    # refresh records after potential line edits
    current_names = set(records.keys())
    missing = [n for n in vehicle_names if n not in current_names]
    if missing:
        if lines and lines[-1] != "":
            lines.append("")
        for name in missing:
            lines.extend(build_new_record(name))
            added.append(name)

    # null price report
    null_names: list[str] = []
    i = 0
    while i < len(lines):
        if lines[i].startswith("  - vehicle_name: "):
            m = re.match(r'\s*-\s+vehicle_name:\s+"(.*)"\s*$', lines[i])
            name = m.group(1) if m else "(unknown)"
            j = i + 1
            has_null = False
            while j < len(lines) and not lines[j].startswith("  - vehicle_name: "):
                if lines[j].strip() == "base_price: null":
                    has_null = True
                    break
                j += 1
            if has_null:
                null_names.append(name)
            i = j
            continue
        i += 1

    output = "\n".join(lines) + "\n"
    if args.dry_run:
        print(f"[dry-run] weekly: {weekly_path}")
        print(f"[dry-run] new vehicles added: {len(added)}")
    else:
        prices_path.write_text(output, encoding="utf-8")
        print(f"updated: {prices_path}")
        print(f"weekly source: {weekly_path}")
        print(f"new vehicles added: {len(added)}")
    if added:
        for name in added:
            print(f"  + {name}")
    print(f"vehicles missing base_price: {len(null_names)}")
    for name in null_names:
        print(f"  - {name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

