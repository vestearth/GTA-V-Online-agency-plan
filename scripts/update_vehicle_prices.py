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


def stripped_alias(name: str) -> str | None:
    parts = name.replace("–", "-").split()
    if len(parts) <= 1:
        return None
    return " ".join(parts[1:])


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
    return [
        f'  - vehicle_name: "{name}"',
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
    parser.add_argument("--dry-run", action="store_true", help="Show changes without writing files")
    args = parser.parse_args()

    prices_path = args.prices
    if not prices_path.exists():
        print(f"error: missing prices file: {prices_path}", file=sys.stderr)
        return 1

    weekly_path = args.weekly if args.weekly else discover_latest_weekly(Path("data"))
    vehicle_names = load_vehicle_names(weekly_path)
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

