#!/usr/bin/env python3
"""Sync vehicle reference entries from weekly planning data.

This script updates `data/references/vehicle_prices.yaml` by:
1) reading vehicle names from a weekly JSON payload,
    pulling from `vehicle_opportunities` when present and otherwise falling back
    to raw weekly surfaces such as `events`, `discounts`, podium/prize/test-ride
    entries, and showroom-style sections,
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
from dataclasses import dataclass
from pathlib import Path

try:
    from scripts.fetch_gtacar_prices import resolve_slug
except ModuleNotFoundError:
    script_dir = Path(__file__).resolve().parent
    if str(script_dir) not in sys.path:
        sys.path.insert(0, str(script_dir))
    from fetch_gtacar_prices import resolve_slug


NON_VEHICLE_SUBSTRINGS = (
    "gta$",
    " rp",
    "community mission",
    "mission series",
    "community race series",
    "time trial",
    "weekly challenge",
    "daily objective",
    "targets",
    "priority file",
    "money front",
    "factory",
    "property",
    "properties",
    "upgrades",
    "upgrade",
    "modification",
    "modifications",
    "drinks at",
    "diamond casino",
    "music locker",
    "legal work",
    "rifle",
    "shotgun",
    "smg",
    "combat mg",
    "stun gun",
    "knife",
    "molotov",
    "proximity mine",
    "tear gas",
    "livery",
    "gun van",
    "membership",
    "customization",
    "tuning",
    "racing suit",
    "racing suits",
    "garage",
    "launcher",
    "body armor",
)

NON_VEHICLE_EXACT_NAMES = {
    "podium vehicle",
    "prize ride",
    "login reward",
    "prize ride challenge",
    "nightclub properties",
    "nightclub upgrades and modifications",
    "heavy rifle (gun van)",
    "ls car meet membership",
    "pool cue",
    "horn customization",
    "turbo tuning",
    "body armor",
}

RAW_VEHICLE_SECTION_KEYS = (
    "luxury_autos",
    "premium_deluxe_motorsports",
    "premium_deluxe_motorsport",
    "test_rides",
    "premium_test_rides",
)


@dataclass(frozen=True)
class SlugClassification:
    resolved: dict[str, str]
    unresolved: list[str]


def has_removed_vehicle_marker(value: str) -> bool:
    return "removed vehicle" in value.casefold()


def clean_vehicle_candidate(value: str) -> str:
    cleaned = re.sub(r"\(\s*Removed Vehicle\s*\)", "", value, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s+wrapped in .*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s+\([^)]*Enhanced[^)]*\)", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s+", " ", cleaned).strip(" :-")
    return cleaned.strip()


def looks_like_vehicle_name(value: str) -> bool:
    cleaned = clean_vehicle_candidate(value)
    if not cleaned:
        return False
    lowered = cleaned.casefold()
    if lowered in NON_VEHICLE_EXACT_NAMES:
        return False
    if lowered.startswith(("place top ", "win ", "complete ", "visit ")):
        return False
    return not any(fragment in lowered for fragment in NON_VEHICLE_SUBSTRINGS)


def append_vehicle_name(names: list[str], seen: set[str], raw_value: str) -> None:
    cleaned = clean_vehicle_candidate(raw_value)
    if not looks_like_vehicle_name(cleaned) or cleaned in seen:
        return
    seen.add(cleaned)
    names.append(cleaned)


def iter_dict_vehicle_candidates(item: dict) -> list[tuple[str, bool]]:
    candidates: list[tuple[str, bool]] = []
    removed = bool(item.get("removed_vehicle"))
    for key in ("vehicle_name", "vehicle"):
        value = item.get(key)
        if isinstance(value, str):
            candidates.append((value, removed or has_removed_vehicle_marker(value)))
    event_type = str(item.get("type", "")).casefold()
    is_non_vehicle_event = event_type in {"reward", "challenge"}
    if (
        "name" in item
        and not is_non_vehicle_event
        and any(k in item for k in ("price", "discount_percent", "source", "availability"))
    ):
        value = item.get("name")
        if isinstance(value, str):
            candidates.append((value, removed or has_removed_vehicle_marker(value)))
    nested_items = item.get("items")
    if isinstance(nested_items, list):
        for nested in nested_items:
            if isinstance(nested, dict):
                candidates.extend(iter_dict_vehicle_candidates(nested))
            elif isinstance(nested, str):
                candidates.append((nested, has_removed_vehicle_marker(nested)))
    nested_vehicles = item.get("vehicles")
    if isinstance(nested_vehicles, list):
        for nested in nested_vehicles:
            if isinstance(nested, dict):
                candidates.extend(iter_dict_vehicle_candidates(nested))
            elif isinstance(nested, str):
                candidates.append((nested, has_removed_vehicle_marker(nested)))
    return candidates


def extract_vehicle_names_from_weekly_payload(payload: dict) -> list[str]:
    weekly_content = payload.get("weekly_content", {}) if isinstance(payload, dict) else {}
    names: list[str] = []
    seen: set[str] = set()

    opportunities = weekly_content.get("vehicle_opportunities", [])
    if isinstance(opportunities, list):
        for item in opportunities:
            if not isinstance(item, dict):
                continue
            name = item.get("vehicle_name")
            if isinstance(name, str):
                append_vehicle_name(names, seen, name)

    events = weekly_content.get("events", [])
    if isinstance(events, list):
        for event in events:
            if not isinstance(event, dict):
                continue
            for candidate, _removed in iter_dict_vehicle_candidates(event):
                append_vehicle_name(names, seen, candidate)

    for section_key in RAW_VEHICLE_SECTION_KEYS:
        section = weekly_content.get(section_key)
        if isinstance(section, list):
            for item in section:
                if isinstance(item, dict):
                    for candidate, _removed in iter_dict_vehicle_candidates(item):
                        append_vehicle_name(names, seen, candidate)
                elif isinstance(item, str):
                    append_vehicle_name(names, seen, item)

    for field_name in ("podium_vehicle", "prize_ride_vehicle", "premium_test_ride"):
        value = weekly_content.get(field_name)
        if isinstance(value, str):
            append_vehicle_name(names, seen, value)

    discounts = weekly_content.get("discounts", [])
    if isinstance(discounts, list):
        for tier in discounts:
            if not isinstance(tier, dict):
                continue
            items = tier.get("items", [])
            if not isinstance(items, list):
                continue
            for item in items:
                if isinstance(item, str):
                    append_vehicle_name(names, seen, item)

    return names


def extract_removed_vehicle_names_from_weekly_payload(payload: dict) -> set[str]:
    weekly_content = payload.get("weekly_content", {}) if isinstance(payload, dict) else {}
    removed_names: set[str] = set()

    opportunities = weekly_content.get("vehicle_opportunities", [])
    if isinstance(opportunities, list):
        for item in opportunities:
            if not isinstance(item, dict) or not bool(item.get("removed_vehicle")):
                continue
            name = item.get("vehicle_name")
            if isinstance(name, str):
                cleaned = clean_vehicle_candidate(name)
                if looks_like_vehicle_name(cleaned):
                    removed_names.add(cleaned)

    events = weekly_content.get("events", [])
    if isinstance(events, list):
        for event in events:
            if not isinstance(event, dict):
                continue
            for candidate, removed in iter_dict_vehicle_candidates(event):
                cleaned = clean_vehicle_candidate(candidate)
                if removed and looks_like_vehicle_name(cleaned):
                    removed_names.add(cleaned)

    for section_key in RAW_VEHICLE_SECTION_KEYS:
        section = weekly_content.get(section_key)
        if not isinstance(section, list):
            continue
        for item in section:
            if isinstance(item, dict):
                for candidate, removed in iter_dict_vehicle_candidates(item):
                    cleaned = clean_vehicle_candidate(candidate)
                    if removed and looks_like_vehicle_name(cleaned):
                        removed_names.add(cleaned)
            elif isinstance(item, str) and has_removed_vehicle_marker(item):
                cleaned = clean_vehicle_candidate(item)
                if looks_like_vehicle_name(cleaned):
                    removed_names.add(cleaned)

    return removed_names


def discover_latest_weekly(data_dir: Path) -> Path:
    candidates = [Path(p) for p in glob.glob(str(data_dir / "weekly_planning_*.json"))]
    if not candidates:
        raise FileNotFoundError("No weekly_planning_*.json found in data/")
    # Prefer deterministic week-id selection over filesystem mtime.
    # Git checkouts can produce misleading mtimes (or ties), which may cause
    # the script to pick an older weekly payload in CI.
    week_id_pattern = re.compile(r"^weekly_planning_(\d{4})_w(\d{1,2})\.json$")
    week_candidates: list[tuple[int, int, Path]] = []
    for p in candidates:
        m = week_id_pattern.match(p.name)
        if not m:
            continue
        year = int(m.group(1))
        week = int(m.group(2))
        week_candidates.append((year, week, p))
    if week_candidates:
        return max(week_candidates, key=lambda x: (x[0], x[1]))[2]
    return max(candidates, key=lambda p: p.stat().st_mtime)


def load_vehicle_names(weekly_path: Path) -> list[str]:
    payload = json.loads(weekly_path.read_text(encoding="utf-8"))
    return extract_vehicle_names_from_weekly_payload(payload if isinstance(payload, dict) else {})


def load_slug_overrides(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"warning: could not read slug map {path}: {exc}", file=sys.stderr)
        return {}
    raw = payload.get("slug_by_vehicle_name", payload)
    if not isinstance(raw, dict):
        return {}
    out: dict[str, str] = {}
    for k, v in raw.items():
        if isinstance(k, str) and isinstance(v, str) and k.strip() and v.strip():
            slug = v.strip().strip("/")
            if re.fullmatch(r"[a-zA-Z0-9_-]+", slug):
                out[k.strip()] = slug
            else:
                print(f"warning: invalid GTACars slug for {k.strip()!r}: {v!r}", file=sys.stderr)
    return out


def sync_slug_map(path: Path, updates: dict[str, str], dry_run: bool = False) -> list[str]:
    if not updates:
        return []

    existing_payload: dict[str, object] = {}
    if path.exists():
        try:
            loaded = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                existing_payload = loaded
        except Exception as exc:
            print(f"warning: could not read slug map {path}: {exc}", file=sys.stderr)

    raw_map = existing_payload.get("slug_by_vehicle_name", {})
    existing_map: dict[str, str] = {}
    if isinstance(raw_map, dict):
        for k, v in raw_map.items():
            if isinstance(k, str) and isinstance(v, str) and k.strip() and v.strip():
                existing_map[k.strip()] = v.strip().strip("/")

    changed: list[str] = []
    for name, slug in sorted(updates.items(), key=lambda item: item[0].lower()):
        clean_slug = slug.strip().strip("/")
        if not clean_slug:
            continue
        if existing_map.get(name) != clean_slug:
            existing_map[name] = clean_slug
            changed.append(name)

    if not changed:
        return []

    payload = dict(existing_payload)
    payload.setdefault("schema_version", "1.0")
    payload.setdefault(
        "description",
        "Optional vehicle_name -> GTACars slug (/gta5/<slug>). Used when source_url is still the bare https://gtacars.net root. Keys must match vehicle_name in vehicle_prices.yaml exactly.",
    )
    payload["slug_by_vehicle_name"] = dict(sorted(existing_map.items(), key=lambda item: item[0].lower()))

    if dry_run:
        print(f"[dry-run] would sync {len(changed)} slug map entr{'y' if len(changed) == 1 else 'ies'}")
        for name in changed:
            print(f"  + {name} -> {existing_map[name]}")
        return changed

    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"updated slug map: {path}")
    for name in changed:
        print(f"  + {name} -> {existing_map[name]}")
    return changed


def slug_from_record_block(block: tuple[str, ...] | list[str]) -> str | None:
    for line in block:
        m = re.search(r'source_url:\s*"https://gtacars\.net/gta5/([^/"?#]+)', line)
        if m:
            return m.group(1)
    return None


def source_url_from_record_block(block: tuple[str, ...] | list[str]) -> str | None:
    for line in block:
        m = re.search(r'source_url:\s*"([^"]+)"', line)
        if m:
            return m.group(1)
    return None


def alias_hints_from_record_block(block: tuple[str, ...] | list[str]) -> list[str]:
    for line in block:
        if "alias_hints:" not in line:
            continue
        m = re.search(r'alias_hints:\s*\[(.*)\]\s*$', line)
        if not m:
            return []
        raw = m.group(1).strip()
        if not raw:
            return []
        values = re.findall(r'"((?:\\.|[^"])*)"', raw)
        return [v.replace('\\"', '"').replace("\\\\", "\\") for v in values]
    return []


def classify_new_vehicle_slugs(
    vehicle_names: list[str],
    records: dict[str, tuple[str, ...] | list[str]],
    slug_overrides: dict[str, str],
) -> SlugClassification:
    resolved: dict[str, str] = {}
    unresolved: list[str] = []
    for name in vehicle_names:
        block = records.get(name, ())
        source_url = source_url_from_record_block(block) or ""
        alias_hints = alias_hints_from_record_block(block)
        slug = resolve_slug(name, source_url, slug_overrides, alias_hints)
        if slug:
            resolved[name] = slug
        else:
            unresolved.append(name)
    return SlugClassification(resolved=resolved, unresolved=unresolved)


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
        for name in extract_removed_vehicle_names_from_weekly_payload(payload):
            removed_map.setdefault(name, set()).add(week_id)
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


def build_new_record(name: str, slug: str | None = None) -> list[str]:
    alias = stripped_alias(name)
    aliases = [alias] if alias else []
    removed = False
    tier = infer_vehicle_tier(name, removed)
    source_url = f"https://gtacars.net/gta5/{slug}" if slug else "https://gtacars.net"
    return [
        f'  - vehicle_name: "{name}"',
        f'    vehicle_tier: "{tier}"',
        "    race_tiers: {}",
        f"    removed_vehicle: {str(removed).lower()}",
        "    removed_vehicle_weeks: []",
        "    base_price: null",
        "    trade_price: null",
        f'    source_url: "{source_url}"',
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
    parser.add_argument(
        "--slug-map",
        type=Path,
        default=Path("data/references/vehicle_gtacars_slugs.json"),
        help="Optional JSON map for vehicle_name -> GTACars slug.",
    )
    parser.add_argument(
        "--strict-new-vehicles",
        action="store_true",
        help="Fail before writing if a new vehicle has no GTACars slug.",
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
    slug_overrides = load_slug_overrides(args.slug_map)
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
    record_blocks: dict[str, tuple[str, ...]] = {}
    for idx, s in enumerate(block_starts):
        e = block_starts[idx + 1] if idx + 1 < len(block_starts) else len(lines)
        m = re.match(r'\s*-\s+vehicle_name:\s+"(.*)"\s*$', lines[s])
        if m:
            name = m.group(1)
            records[name] = (s, e)
            record_blocks[name] = tuple(lines[s:e])

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
    resolved_slug_updates: dict[str, str] = {}
    for name, block in record_blocks.items():
        source_url = source_url_from_record_block(block) or ""
        slug = resolve_slug(name, source_url, slug_overrides)
        if slug:
            resolved_slug_updates[name] = slug
    slug_classification = classify_new_vehicle_slugs(missing, record_blocks, slug_overrides)
    if missing:
        print(f"new vehicle candidates: {len(missing)}")
    if slug_classification.unresolved:
        print(f"vehicles needing slug: {len(slug_classification.unresolved)}")
        for name in slug_classification.unresolved:
            print(f"  ! {name}")
        if args.strict_new_vehicles:
            print("error: unresolved new vehicle slugs in strict mode", file=sys.stderr)
            return 1
    if resolved_slug_updates:
        sync_slug_map(args.slug_map, resolved_slug_updates, dry_run=args.dry_run)
    if missing:
        if lines and lines[-1] != "":
            lines.append("")
        for name in missing:
            if not looks_like_vehicle_name(name):
                print(f"skip non-vehicle record: {name}")
                continue
            lines.extend(build_new_record(name, slug_classification.resolved.get(name)))
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
