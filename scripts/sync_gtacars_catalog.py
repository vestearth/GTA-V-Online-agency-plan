#!/usr/bin/env python3
"""Sync GTACars vehicle catalog slugs and prices from public sitemap pages.

The script deliberately uses the public sitemap and `/gta5/<slug>` vehicle
pages only. It does not crawl `/api/`.
"""

from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path


DEFAULT_SITEMAP_URL = "https://gtacars.net/sitemap.xml"
DEFAULT_PRICES = Path("data/references/vehicle_prices.yaml")
DEFAULT_SLUG_MAP = Path("data/references/vehicle_gtacars_slugs.json")
GTACARS_VEHICLE_URL_RE = re.compile(r"^https://gtacars\.net/gta5/([A-Za-z0-9_-]+)$")
NON_VEHICLE_SLUGS = {
    "compare",
    "downforce",
    "flags",
    "glossary",
    "laptime",
    "setups",
    "tiers",
    "topspeed",
    "upgrades",
}


@dataclass(frozen=True)
class GtacarsVehicleRecord:
    vehicle_name: str
    slug: str
    base_price: int | None
    trade_price: int | None
    source_url: str


def extract_vehicle_urls_from_sitemap(sitemap_xml: str) -> list[str]:
    urls: list[str] = []
    seen: set[str] = set()
    for raw in re.findall(r"<loc>\s*([^<]+?)\s*</loc>", sitemap_xml):
        url = html.unescape(raw.strip())
        match = GTACARS_VEHICLE_URL_RE.match(url)
        if not match:
            continue
        slug = match.group(1)
        if slug in NON_VEHICLE_SLUGS or url in seen:
            continue
        seen.add(url)
        urls.append(url)
    return urls


def _extract_slug(source_url: str) -> str:
    parsed = urllib.parse.urlparse(source_url)
    parts = [part for part in parsed.path.split("/") if part]
    if len(parts) != 2 or parts[0] != "gta5":
        raise ValueError(f"not a GTACars vehicle page URL: {source_url!r}")
    return parts[1]


def _strip_tags(value: str) -> str:
    text = re.sub(r"<[^>]+>", " ", value)
    return re.sub(r"\s+", " ", html.unescape(text)).strip()


def _extract_h1_name(html_text: str) -> str | None:
    match = re.search(r"<h1\b[^>]*>(?P<body>.*?)</h1>", html_text, flags=re.I | re.S)
    if not match:
        return None
    text = _strip_tags(match.group("body"))
    return text or None


def _extract_manufacturer(html_text: str) -> str | None:
    pattern = re.compile(
        r"<td>\s*Manufacturer\s*</td>\s*<td>\s*<a[^>]*filter_manufacturer=[^>]*>(?P<name>.*?)</a>",
        flags=re.I | re.S,
    )
    match = pattern.search(html_text)
    if not match:
        return None
    name = _strip_tags(match.group("name"))
    if not name or name.casefold() in {"none", "unknown"}:
        return None
    return name


def _full_vehicle_name(base_name: str, manufacturer: str | None) -> str:
    if not manufacturer:
        return base_name
    if base_name.casefold().startswith(manufacturer.casefold() + " "):
        return base_name
    return f"{manufacturer} {base_name}"


def _parse_money(value: str) -> int:
    return int(re.sub(r"[^\d]", "", value))


def _extract_base_price(html_text: str, source_url: str) -> int | None:
    match = re.search(r"Price:</span>\s*<data[^>]*\bvalue=\"(\d+)\"", html_text, flags=re.I)
    if match:
        return int(match.group(1))
    text = _strip_tags(html_text)
    match = re.search(r"Price:\s*\$\s*([\d,]+)", text, flags=re.I)
    if match:
        return _parse_money(match.group(1))
    return None


def _extract_trade_price(html_text: str) -> int | None:
    text = _strip_tags(html_text)
    match = re.search(r"Trade price:\s*\$\s*([\d,]+)", text, flags=re.I)
    return _parse_money(match.group(1)) if match else None


def extract_vehicle_record_from_html(html_text: str, source_url: str) -> GtacarsVehicleRecord:
    slug = _extract_slug(source_url)
    base_name = _extract_h1_name(html_text)
    if not base_name:
        raise ValueError(f"no vehicle name found on page {source_url!r}")
    manufacturer = _extract_manufacturer(html_text)
    return GtacarsVehicleRecord(
        vehicle_name=_full_vehicle_name(base_name, manufacturer),
        slug=slug,
        base_price=_extract_base_price(html_text, source_url),
        trade_price=_extract_trade_price(html_text),
        source_url=source_url,
    )


def load_slug_overrides(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    raw = payload.get("slug_by_vehicle_name", payload)
    if not isinstance(raw, dict):
        return {}
    return {
        str(name).strip(): str(slug).strip().strip("/")
        for name, slug in raw.items()
        if str(name).strip() and str(slug).strip()
    }


def build_slug_updates(records: list[GtacarsVehicleRecord], existing_slugs: dict[str, str]) -> dict[str, str]:
    updates: dict[str, str] = {}
    for record in records:
        if record.vehicle_name not in existing_slugs:
            updates[record.vehicle_name] = record.slug
    return dict(sorted(updates.items(), key=lambda item: item[0].casefold()))


def merge_slug_map_text(existing_text: str, updates: dict[str, str]) -> str:
    clean_text = existing_text.lstrip("\ufeff")
    payload = json.loads(clean_text) if clean_text.strip() else {}
    raw = payload.get("slug_by_vehicle_name", {})
    existing = raw if isinstance(raw, dict) else {}
    merged = {str(k): str(v).strip().strip("/") for k, v in existing.items()}
    merged.update(updates)
    payload.setdefault("schema_version", "1.0")
    payload.setdefault(
        "description",
        "Optional vehicle_name -> GTACars slug (/gta5/<slug>). Used when source_url is still the bare https://gtacars.net root. Keys must match vehicle_name in vehicle_prices.yaml exactly.",
    )
    payload["slug_by_vehicle_name"] = dict(sorted(merged.items(), key=lambda item: item[0].casefold()))
    return json.dumps(payload, indent=2, ensure_ascii=False) + "\n"


def _quote_yaml_string(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def _stripped_alias(name: str) -> str | None:
    parts = name.split()
    if len(parts) <= 1:
        return None
    return " ".join(parts[1:])


def _record_block(record: GtacarsVehicleRecord) -> list[str]:
    alias = _stripped_alias(record.vehicle_name)
    aliases = [alias] if alias else []
    trade_price = "null" if record.trade_price is None else str(record.trade_price)
    alias_line = ", ".join(_quote_yaml_string(item) for item in aliases)
    return [
        f"  - vehicle_name: {_quote_yaml_string(record.vehicle_name)}",
        '    vehicle_tier: "unrated"',
        "    race_tiers: {}",
        "    removed_vehicle: false",
        "    removed_vehicle_weeks: []",
        f"    base_price: {'null' if record.base_price is None else record.base_price}",
        f"    trade_price: {trade_price}",
        f"    source_url: {_quote_yaml_string(record.source_url)}",
        f"    alias_hints: [{alias_line}]",
        "",
    ]


def _set_block_field(block: list[str], field: str, value: str) -> bool:
    prefix = f"    {field}: "
    for index, line in enumerate(block):
        if line.startswith(prefix):
            if line != prefix + value:
                block[index] = prefix + value
                return True
            return False
    block.append(prefix + value)
    return True


def _get_block_field(block: list[str], field: str) -> str | None:
    prefix = f"    {field}: "
    for line in block:
        if line.startswith(prefix):
            return line[len(prefix):].strip()
    return None


def _is_empty_yaml_value(value: str | None) -> bool:
    if value is None:
        return True
    return value.strip().strip('"') in {"", "null", "https://gtacars.net"}


def apply_price_records(source_text: str, records: list[GtacarsVehicleRecord], today: str | None = None) -> tuple[str, list[str]]:
    today = today or dt.date.today().isoformat()
    lines = source_text.splitlines()
    changed: list[str] = []

    for index, line in enumerate(lines):
        if line.startswith("last_verified_at: "):
            lines[index] = f'last_verified_at: "{today}"'
            break

    starts = [index for index, line in enumerate(lines) if line.startswith("  - vehicle_name: ")]
    records_by_name = {record.vehicle_name: record for record in records}
    existing_names: list[str] = []

    for position, start in enumerate(starts):
        end = starts[position + 1] if position + 1 < len(starts) else len(lines)
        match = re.match(r'\s*-\s+vehicle_name:\s+"(.*)"\s*$', lines[start])
        if not match:
            continue
        name = match.group(1)
        existing_names.append(name)
        record = records_by_name.get(name)
        if not record:
            continue
        block = lines[start:end]
        block_changed = False
        current_base = _get_block_field(block, "base_price")
        if record.base_price is not None and _is_empty_yaml_value(current_base):
            block_changed |= _set_block_field(block, "base_price", str(record.base_price))
        trade_price = "null" if record.trade_price is None else str(record.trade_price)
        current_trade = _get_block_field(block, "trade_price")
        if record.trade_price is not None and _is_empty_yaml_value(current_trade):
            block_changed |= _set_block_field(block, "trade_price", trade_price)
        current_source = _get_block_field(block, "source_url")
        if _is_empty_yaml_value(current_source):
            block_changed |= _set_block_field(block, "source_url", _quote_yaml_string(record.source_url))
        if block_changed:
            changed.append(name)
            lines[start:end] = block

    missing = [record for record in records if record.vehicle_name not in set(existing_names)]
    if missing and lines and lines[-1] != "":
        lines.append("")
    for record in missing:
        lines.extend(_record_block(record))
        changed.append(record.vehicle_name)

    return "\n".join(lines).rstrip() + "\n", changed


def fetch_text(url: str, user_agent: str) -> str:
    parsed = urllib.parse.urlparse(url)
    if parsed.path.startswith("/api/"):
        raise ValueError(f"refusing to fetch disallowed API path: {url}")
    request = urllib.request.Request(url, headers={"User-Agent": user_agent})
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8", errors="replace")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Sync GTACars sitemap vehicle slugs and prices.")
    parser.add_argument("--sitemap-url", default=DEFAULT_SITEMAP_URL)
    parser.add_argument("--prices", type=Path, default=DEFAULT_PRICES)
    parser.add_argument("--slug-map", type=Path, default=DEFAULT_SLUG_MAP)
    parser.add_argument("--limit", type=int, help="Only fetch the first N sitemap vehicle pages")
    parser.add_argument("--sleep", type=float, default=0.6, help="Seconds between vehicle page requests")
    parser.add_argument("--dry-run", action="store_true", help="Fetch and report changes without writing")
    parser.add_argument(
        "--user-agent",
        default="GTA-V-Online-agency-plan/sync_gtacars_catalog (contact: repo maintainer)",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    sitemap_text = fetch_text(args.sitemap_url, args.user_agent)
    urls = extract_vehicle_urls_from_sitemap(sitemap_text)
    if args.limit is not None:
        urls = urls[: max(args.limit, 0)]

    records: list[GtacarsVehicleRecord] = []
    skipped: list[tuple[str, str]] = []
    for index, url in enumerate(urls):
        try:
            page_html = fetch_text(url, args.user_agent)
            records.append(extract_vehicle_record_from_html(page_html, url))
        except Exception as exc:
            skipped.append((url, f"{type(exc).__name__}: {exc}"))
        if index + 1 < len(urls):
            time.sleep(max(args.sleep, 0.0))

    existing_slugs = load_slug_overrides(args.slug_map)
    slug_updates = build_slug_updates(records, existing_slugs)
    price_text = args.prices.read_text(encoding="utf-8")
    updated_prices, price_changes = apply_price_records(price_text, records)

    print(f"sitemap_vehicle_pages: {len(urls)}")
    print(f"parsed_records: {len(records)}")
    print(f"slug_updates: {len(slug_updates)}")
    print(f"price_changes: {len(price_changes)}")
    for name in list(slug_updates)[:20]:
        print(f"  slug + {name} -> {slug_updates[name]}")
    for name in price_changes[:20]:
        print(f"  price * {name}")
    for url, reason in skipped:
        print(f"warning: skipped {url}: {reason}", file=sys.stderr)

    if args.dry_run:
        print("[dry-run] no files written")
        return 0

    if slug_updates:
        existing_slug_text = args.slug_map.read_text(encoding="utf-8") if args.slug_map.exists() else "{}"
        args.slug_map.write_text(merge_slug_map_text(existing_slug_text, slug_updates), encoding="utf-8")
    if price_changes:
        args.prices.write_text(updated_prices, encoding="utf-8")
    print("updated GTACars references")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
