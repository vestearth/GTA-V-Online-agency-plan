#!/usr/bin/env python3
"""Fill base_price / trade_price in vehicle_prices.yaml from GTACars HTML pages.

Uses only the Python standard library. Resolves each vehicle's GTACars slug from
(in order): --slug-map JSON, ``source_url`` path ``/gta5/<slug>``, then built-in
fallbacks for common weekly names that still point at the bare gtacars.net root.

Examples:
  python3 scripts/fetch_gtacar_prices.py
  python3 scripts/fetch_gtacar_prices.py --dry-run
  python3 scripts/fetch_gtacar_prices.py --refresh-all --sleep 0.4

``--dry-run`` resolves slugs and prints targets only (no HTTP, no file write).
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path


GTACARS_BASE = "https://gtacars.net/gta5"

# When ``source_url`` is only https://gtacars.net, map ``vehicle_name`` -> slug segment.
FALLBACK_SLUG_BY_VEHICLE_NAME: dict[str, str] = {
    "Bravado Buffalo Cruiser": "polbuffalo",
    "Pfister Growler": "growler",
    "Annis 300R": "r300",
    "Enus Cognoscenti": "cognoscenti",
    "Declasse Tornado Rat Rod": "tornado6",
    "Benefactor Streiter": "streiter",
    "Karin Vivanite": "vivanite",
    "Imponte Arbiter GT": "arbitergt",
    "Vapid Apocalypse Imperator (Arena)": "imperator",
    "Imponte Ruiner 2000": "ruiner2",
    "Grotti Itali Classic": "itali2",
    "Dinka Jester Classic": "jester3",
    "Dewbauchee JB 700W": "jb7002",
    "Bravado Banshee GTS": "banshee3",
    "Överflöd Autarch": "autarch",
    "Vom Feuer Anti-Aircraft Trailer": "trailersmall2",
    "Nagasaki Outlaw": "outlaw",
    "Mammoth Squaddie": "squaddie",
    "Vapid Winky": "winky",
    "Western Rampant Rocket": "rrocket",
    "Pfister Comet Safari": "comet4",
    "Dewbauchee Specter": "specter",
    "Pfister Astrale": "astrale",
    "Übermacht Sentinel GTS": "sentinel5",
    "Western Reever": "reever",
    "BF Club": "club",
    "Vapid Hustler": "hustler",
    "Dewbauchee Rapid GT Classic": "rapidgt3",
    "Vapid Clique": "clique",
    "Coil Cyclone II": "cyclone2",
    "Gallivanter Baller ST-D": "baller8",
    "Vapid Festival Bus": "pbus2",
    "Declasse DR1": "openwheel2",
    "Benefactor BR8": "openwheel1",
    "Invetero Coquette D1": "coquette5",
    "Pfister Comet SR": "comet5",
    "Grotti Turismo Classic": "turismo2",
    "Penaud La Coureuse": "coureur",
    "Western Zombie Bobber": "zombiea",
    "Enus Cognoscenti Cabrio": "cogcabrio",
    "Western Company Cargobob": "cargobob",
    "Pfister 811": "pfister811",
}


def load_slug_overrides(path: Path | None) -> dict[str, str]:
    if path is None or not path.exists():
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
            out[k.strip()] = v.strip()
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


def slug_from_source_url(url: str) -> str | None:
    m = re.search(r"gtacars\.net/gta5/([^/\"?#]+)/?", url, flags=re.I)
    if not m:
        return None
    slug = m.group(1).strip()
    return slug or None


def normalize_vehicle_key(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.casefold())


def slug_from_alias_hint(alias_hints: list[str] | None) -> str | None:
    if not alias_hints:
        return None
    for hint in alias_hints:
        if not isinstance(hint, str):
            continue
        slug = re.sub(r"[^a-zA-Z0-9_-]+", "", hint).strip().strip("/").casefold()
        if slug:
            return slug
    return None


def resolve_slug(
    vehicle_name: str,
    source_url: str,
    slug_overrides: dict[str, str],
    alias_hints: list[str] | None = None,
) -> str | None:
    candidates: list[str] = []
    if vehicle_name in slug_overrides:
        candidates.append(slug_overrides[vehicle_name])
    su = slug_from_source_url(source_url)
    if su:
        candidates.append(su)
    fb = FALLBACK_SLUG_BY_VEHICLE_NAME.get(vehicle_name)
    if fb:
        candidates.append(fb)
    if not candidates:
        target_key = normalize_vehicle_key(vehicle_name)
        for name, slug in slug_overrides.items():
            if normalize_vehicle_key(name) == target_key:
                candidates.append(slug)
                break
    alias_slug = slug_from_alias_hint(alias_hints)
    if alias_slug and normalize_vehicle_key(alias_slug) == normalize_vehicle_key(vehicle_name):
        candidates.append(alias_slug)
    for raw in candidates:
        slug = raw.strip().strip("/")
        if slug and re.fullmatch(r"[a-zA-Z0-9_-]+", slug):
            return slug
    return None


def fetch_prices(slug: str, user_agent: str) -> tuple[int, int | None]:
    url = f"{GTACARS_BASE}/{slug}"
    req = urllib.request.Request(url, headers={"User-Agent": user_agent})
    with urllib.request.urlopen(req, timeout=30) as resp:
        html = resp.read().decode("utf-8", errors="replace")
    return extract_prices_from_html(html, url)


def extract_prices_from_html(html: str, url: str) -> tuple[int, int | None]:
    pm = re.search(r'Price:</span>\s*<data[^>]*value="(\d+)"', html, flags=re.I)
    if not pm:
        text = re.sub(r"<[^>]+>", " ", html)
        text = re.sub(r"\s+", " ", text)
        pm = re.search(r"Price:\s*\$\s*([\d,]+)", text, flags=re.I)
    if not pm:
        raise ValueError(f"no Price data found on page {url!r}")
    base = int(pm.group(1).replace(",", ""))

    tm = re.search(r'Trade price:</span>\s*<span[^>]*>\$\s*([\d,]+)</span>', html, flags=re.I)
    if not tm:
        text = re.sub(r"<[^>]+>", " ", html)
        text = re.sub(r"\s+", " ", text)
        tm = re.search(r"Trade price:\s*\$\s*([\d,]+)", text, flags=re.I)
    trade = int(tm.group(1).replace(",", "")) if tm else None
    return base, trade


def vehicle_block_starts(lines: list[str]) -> list[int]:
    return [i for i, ln in enumerate(lines) if ln.startswith("  - vehicle_name: ")]


def parse_vehicle_name(line: str) -> str | None:
    m = re.match(r'\s*-\s+vehicle_name:\s+"(.*)"\s*$', line)
    return m.group(1) if m else None


def get_field(lines: list[str], s: int, e: int, field: str) -> str | None:
    prefix = f"    {field}: "
    for i in range(s, e):
        if lines[i].startswith(prefix):
            return lines[i][len(prefix) :].strip()
    return None


def set_field(lines: list[str], s: int, e: int, field: str, value: int | None) -> bool:
    prefix = f"    {field}: "
    rendered = "null" if value is None else str(int(value))
    for i in range(s, e):
        if lines[i].startswith(prefix):
            lines[i] = prefix + rendered
            return True
    return False


def set_source_url(lines: list[str], s: int, e: int, slug: str) -> bool:
    prefix = "    source_url: "
    target = f'{prefix}"{GTACARS_BASE}/{slug}"'
    for i in range(s, e):
        if lines[i].startswith(prefix):
            lines[i] = target
            return True
    return False


def bump_last_verified(lines: list[str], today: str) -> None:
    for i, ln in enumerate(lines):
        if ln.startswith("last_verified_at: "):
            lines[i] = f'last_verified_at: "{today}"'
            break


def parse_int_price(token: str) -> int | None:
    token = token.strip()
    if token == "null":
        return None
    try:
        return int(token)
    except ValueError:
        return None


def get_alias_hints(lines: list[str], s: int, e: int) -> list[str]:
    for i in range(s, e):
        line = lines[i]
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


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch GTA vehicle prices from GTACars into vehicle_prices.yaml.")
    parser.add_argument(
        "--prices",
        type=Path,
        default=Path("data/references/vehicle_prices.yaml"),
        help="Path to vehicle_prices.yaml",
    )
    parser.add_argument(
        "--slug-map",
        type=Path,
        default=Path("data/references/vehicle_gtacars_slugs.json"),
        help="Optional JSON: {\"slug_by_vehicle_name\": {\"Full Name\": \"slug\", ...}}",
    )
    parser.add_argument("--dry-run", action="store_true", help="Show planned updates without writing the file")
    parser.add_argument(
        "--refresh-all",
        action="store_true",
        help="Re-fetch every vehicle with a resolvable slug (not only missing base_price)",
    )
    parser.add_argument(
        "--sleep",
        type=float,
        default=0.35,
        help="Seconds to sleep between HTTP requests (default: 0.35)",
    )
    parser.add_argument(
        "--user-agent",
        default="GTA-V-Online-agency-plan/fetch_gtacar_prices (contact: repo maintainer)",
        help="User-Agent sent to GTACars",
    )
    args = parser.parse_args()

    prices_path: Path = args.prices
    if not prices_path.exists():
        print(f"error: missing file {prices_path}", file=sys.stderr)
        return 1

    slug_overrides = load_slug_overrides(args.slug_map)

    lines = prices_path.read_text(encoding="utf-8").splitlines()
    if lines and lines[-1].strip() == "":
        trailing_blank = True
        lines = lines[:-1]
    else:
        trailing_blank = False

    starts = vehicle_block_starts(lines)
    today = dt.date.today().isoformat()

    targets: list[tuple[str, str]] = []
    skipped: list[tuple[str, str]] = []

    for idx, s in enumerate(starts):
        e = starts[idx + 1] if idx + 1 < len(starts) else len(lines)
        name = parse_vehicle_name(lines[s])
        if not name:
            continue
        base_raw = get_field(lines, s, e, "base_price")
        current_base = parse_int_price(base_raw or "")
        if not args.refresh_all and current_base is not None:
            continue

        source_url_field = get_field(lines, s, e, "source_url") or ""
        source_url = source_url_field.strip('"')
        alias_hints = get_alias_hints(lines, s, e)

        slug = resolve_slug(name, source_url, slug_overrides, alias_hints)
        if not slug:
            skipped.append((name, "no slug (set source_url or add to slug map JSON)"))
            continue
        targets.append((name, slug))

    if not targets:
        print("nothing to update (no matching vehicles or all skipped)")
        for name, reason in skipped:
            print(f"  skip {name!r}: {reason}", file=sys.stderr)
        return 0

    if args.dry_run:
        print(f"[dry-run] would fetch {len(targets)} vehicle(s) (no HTTP); not writing {prices_path}")
        for name, slug in targets:
            print(f"  {name} -> {GTACARS_BASE}/{slug}")
        for name, reason in skipped:
            print(f"  skip {name!r}: {reason}", file=sys.stderr)
        return 0

    planned: list[tuple[str, str, int, int | None]] = []
    for name, slug in targets:
        try:
            base, trade = fetch_prices(slug, args.user_agent)
        except urllib.error.HTTPError as exc:
            skipped.append((name, f"HTTP {exc.code} for slug {slug!r}"))
            time.sleep(max(args.sleep, 0.0))
            continue
        except Exception as exc:
            skipped.append((name, f"{type(exc).__name__}: {exc}"))
            time.sleep(max(args.sleep, 0.0))
            continue
        planned.append((name, slug, base, trade))
        print(f"  {name}: slug={slug} base_price={base} trade_price={trade}")
        time.sleep(max(args.sleep, 0.0))

    if not planned:
        print("no prices applied (all fetches failed or were skipped)")
        for name, reason in skipped:
            print(f"  skip {name!r}: {reason}", file=sys.stderr)
        return 0

    sync_slug_map(args.slug_map, {name: slug for name, slug, _base, _trade in planned}, dry_run=args.dry_run)

    # Apply edits: re-locate blocks after any prior logic (indices unchanged)
    name_to_update = {p[0]: (p[1], p[2], p[3]) for p in planned}
    changed = False
    starts = vehicle_block_starts(lines)
    for idx, s in enumerate(starts):
        e = starts[idx + 1] if idx + 1 < len(starts) else len(lines)
        name = parse_vehicle_name(lines[s])
        if not name or name not in name_to_update:
            continue
        slug, base, trade = name_to_update[name]
        if not set_field(lines, s, e, "base_price", base):
            print(f"warning: no base_price field for {name!r}", file=sys.stderr)
            continue
        set_field(lines, s, e, "trade_price", trade)
        set_source_url(lines, s, e, slug)
        changed = True

    if changed:
        bump_last_verified(lines, today)

    out = "\n".join(lines) + "\n"
    if trailing_blank:
        out += "\n"
    prices_path.write_text(out, encoding="utf-8")
    print(f"updated: {prices_path} ({len(planned)} vehicle(s))")

    for name, reason in skipped:
        print(f"  skip {name!r}: {reason}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
