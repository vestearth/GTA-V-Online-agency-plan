#!/usr/bin/env python3
"""Generate deterministic Phase 1 dashboard blocks from repository data.

This generator updates only explicit marker-bounded regions inside
`dashboard.html`. It keeps the dashboard as a static HTML/CSS page while
refreshing deterministic blocks from structured repository inputs.
"""

from __future__ import annotations

import argparse
import copy
import datetime as dt
import glob
import html
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DASHBOARD = ROOT / "dashboard.html"
DEFAULT_PROFILE = ROOT / "data" / "player_profile.json"
DEFAULT_DATA_DIR = ROOT / "data"
DEFAULT_VEHICLE_PRICES = ROOT / "data" / "references" / "vehicle_prices.yaml"


class DashboardMarkerError(RuntimeError):
    """Raised when required dashboard markers are missing."""


PHASE1_MARKERS = [
    "header_meta",
    "summary_cards",
    "weekly_deals",
    "weekly_vehicle_spotlight",
    "data_status_note",
]

SPOTLIGHT_GROUP_ORDER = [
    "LS Car Meet",
    "Luxury Autos",
    "Premium Deluxe Motorsport",
    "Premium Test Ride",
    "Podium",
]


def find_latest_weekly_payload(data_dir: Path) -> Path:
    candidates = [Path(p) for p in glob.glob(str(data_dir / "weekly_planning_*.json"))]
    if not candidates:
        raise FileNotFoundError("No weekly_planning_*.json found in data/")
    week_id_pattern = re.compile(r"^weekly_planning_(\d{4})_w(\d{1,2})\.json$")
    ranked: list[tuple[int, int, Path]] = []
    for path in candidates:
        match = week_id_pattern.match(path.name)
        if not match:
            continue
        ranked.append((int(match.group(1)), int(match.group(2)), path))
    if not ranked:
        raise FileNotFoundError("No parseable weekly_planning_<year>_w<week>.json file found in data/")
    ranked.sort()
    return ranked[-1][2]


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_required_markers(html_text: str, required_markers: list[str]) -> None:
    missing: list[str] = []
    for marker in required_markers:
        if f"<!-- START: {marker} -->" not in html_text or f"<!-- END: {marker} -->" not in html_text:
            missing.append(marker)
    if missing:
        raise DashboardMarkerError(f"Missing required dashboard markers: {', '.join(missing)}")


def available_markers(html_text: str) -> list[str]:
    return re.findall(r"<!-- START: ([a-z0-9_]+) -->", html_text)


def replace_marker_block(html_text: str, marker: str, replacement: str) -> str:
    pattern = re.compile(
        rf"(?P<indent>[ \t]*)<!-- START: {re.escape(marker)} -->.*?^[ \t]*<!-- END: {re.escape(marker)} -->",
        flags=re.DOTALL | re.MULTILINE,
    )
    match = pattern.search(html_text)
    if not match:
        raise DashboardMarkerError(f"Missing marker block: {marker}")
    indent = match.group("indent")
    replacement_lines = replacement.rstrip().splitlines()
    indented = "\n".join(f"{indent}{line}" if line else "" for line in replacement_lines)
    block = f"{indent}<!-- START: {marker} -->\n{indented}\n{indent}<!-- END: {marker} -->"
    return html_text[: match.start()] + block + html_text[match.end() :]


def load_vehicle_price_reference(path: Path) -> dict[str, dict[str, object]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    out: dict[str, dict[str, object]] = {}
    current_name: str | None = None
    current: dict[str, object] | None = None
    for line in lines:
        name_match = re.match(r'^  - vehicle_name: "(.*)"$', line)
        if name_match:
            if current_name and current is not None:
                out[current_name] = current
            current_name = name_match.group(1)
            current = {}
            continue
        if current is None:
            continue
        base_match = re.match(r"^    base_price: (\d+|null)$", line)
        if base_match:
            current["base_price"] = None if base_match.group(1) == "null" else int(base_match.group(1))
            continue
        source_match = re.match(r'^    source_url: "(.*)"$', line)
        if source_match:
            current["source_url"] = source_match.group(1)
            continue
    if current_name and current is not None:
        out[current_name] = current
    return out


def dedupe_preserve_order(values: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        out.append(value)
    return out


def build_phase1_context(weekly_payload: dict, player_profile: dict, vehicle_prices: dict[str, dict[str, object]]) -> dict[str, object]:
    weekly_content = weekly_payload["weekly_content"]
    discounts = copy.deepcopy(weekly_content.get("discounts", []))
    scraper_metadata = copy.deepcopy(weekly_payload.get("scraper_metadata", {}))
    price_context = copy.deepcopy(
        scraper_metadata.get("price_context", weekly_content.get("price_context", {}))
    )
    vehicle_opportunities = copy.deepcopy(weekly_content.get("vehicle_opportunities", []))

    owned_major_assets = len(player_profile["owned_assets"]["properties"])
    missing_major_assets = len(player_profile["owned_assets"]["missing_properties"])

    discounted_items_total = 0
    unresolved_discount_items: list[str] = []
    discount_vehicle_names: list[str] = []

    for group in discounts:
        tier_percent = group.get("tier_percent")
        tier_label = str(group.get("tier_label", "")).casefold()
        for item in group.get("items", []):
            if not isinstance(item, str):
                continue
            if tier_percent == 100:
                continue
            if item in price_context:
                context = price_context[item]
                if isinstance(context, dict):
                    key = f"discounted_price_{tier_percent}"
                    value = context.get(key)
                    if isinstance(value, int):
                        discounted_items_total += value
                        discount_vehicle_names.append(item)
                        continue
            if "gun van" not in tier_label and item in vehicle_prices:
                unresolved_discount_items.append(item)

    spotlight_vehicle_names: list[str] = []
    for item in vehicle_opportunities:
        name = item.get("vehicle_name")
        if isinstance(name, str):
            spotlight_vehicle_names.append(name)

    all_vehicle_names = dedupe_preserve_order(discount_vehicle_names + spotlight_vehicle_names)
    all_cars_needed_total = 0
    unresolved_vehicle_prices: list[str] = []
    for name in all_vehicle_names:
        reference = vehicle_prices.get(name, {})
        base_price = reference.get("base_price")
        if isinstance(base_price, int):
            all_cars_needed_total += base_price
        else:
            unresolved_vehicle_prices.append(name)

    return {
        "player_name": player_profile["player_name"],
        "platform": player_profile["platform"],
        "week_id": weekly_payload["week"]["id"],
        "week_label": weekly_payload["week"]["label"],
        "last_reviewed": dt.date.today().isoformat(),
        "owned_major_assets": owned_major_assets,
        "missing_major_assets": missing_major_assets,
        "discounted_items_total": discounted_items_total,
        "all_cars_needed_total": all_cars_needed_total,
        "unresolved_discount_items": dedupe_preserve_order(unresolved_discount_items),
        "unresolved_vehicle_prices": dedupe_preserve_order(unresolved_vehicle_prices),
        "discounts": discounts,
        "price_context": price_context,
        "vehicle_opportunities": vehicle_opportunities,
    }


def format_currency_compact(value: int) -> str:
    if value >= 1_000_000:
        return f"GTA${value / 1_000_000:.1f}M"
    if value >= 1_000:
        return f"GTA${value / 1_000:.1f}K"
    return f"GTA${value}"


def format_currency_full(value: int) -> str:
    return f"GTA${value:,}"


def _vehicle_link(name: str, vehicle_prices: dict[str, dict[str, object]], css_class: str) -> str:
    escaped_name = html.escape(name)
    source_url = vehicle_prices.get(name, {}).get("source_url")
    if isinstance(source_url, str) and source_url:
        return f'<span class="{css_class}"><a class="vehicle-link" href="{html.escape(source_url)}" target="_blank" rel="noopener noreferrer">{escaped_name}</a></span>'
    return f'<span class="{css_class}">{escaped_name}</span>'


def render_header_meta(context: dict[str, object]) -> str:
    return "\n".join(
        [
            "<p>",
            "  <strong>",
            f"    {html.escape(str(context['player_name']))}",
            "  </strong>",
            f"  / {html.escape(str(context['platform']))}",
            "</p>",
            f"<p>Week {html.escape(str(context['week_id']))}: {html.escape(str(context['week_label']))}</p>",
            "<p>",
            "  Discounted Items Total:",
            "  <strong>",
            f"    {html.escape(format_currency_compact(int(context['discounted_items_total'])))}",
            "  </strong>",
            "</p>",
            "<p>",
            "  All Cars Needed:",
            "  <strong>",
            f"    {html.escape(format_currency_compact(int(context['all_cars_needed_total'])))}",
            "  </strong>",
            "</p>",
        ]
    )


def render_data_status_note(context: dict[str, object]) -> str:
    status = "Generated / Clean"
    unresolved_vehicle_prices = context["unresolved_vehicle_prices"]
    unresolved_discount_items = context["unresolved_discount_items"]
    warnings: list[str] = []
    if unresolved_vehicle_prices or unresolved_discount_items:
        status = "Generated / Needs review"
    if unresolved_vehicle_prices:
        warnings.append(f"Totals exclude {len(unresolved_vehicle_prices)} unresolved vehicle prices.")
    if unresolved_discount_items:
        warnings.append(f"Discount totals exclude {len(unresolved_discount_items)} unresolved discounted items.")

    lines = [
        "<p>",
        "  <strong>",
        "    Data source:",
        "  </strong>",
        "  generated snapshot from",
        "  <code>",
        "    data/player_profile.json",
        "  </code>",
        "  + latest",
        "  <code>",
        "    weekly_planning_*.json",
        "  </code>",
        "  +",
        "  <code>",
        "    vehicle_prices.yaml",
        "  </code>",
        "</p>",
        '<div class="provenance-grid">',
        "  <p>",
        "    <strong>",
        "      Last reviewed:",
        "    </strong>",
        f"    {html.escape(str(context['last_reviewed']))}",
        "  </p>",
        "  <p>",
        "    <strong>",
        "      Data status:",
        "    </strong>",
        f"    {html.escape(status)}",
        "  </p>",
        "</div>",
    ]
    for warning in warnings:
        lines.extend(
            [
                '<p class="muted">',
                f"  {html.escape(warning)}",
                "</p>",
            ]
        )
    return "\n".join(lines)


def render_summary_cards(context: dict[str, object]) -> str:
    cards = [
        ("Owned Major Assets", str(context["owned_major_assets"]), "Properties from `owned_assets.properties`.", False),
        ("Missing Major Assets", str(context["missing_major_assets"]), "Uses `missing_properties`; profile note looks stale.", False),
        ("Discounted Items Total", format_currency_compact(int(context["discounted_items_total"])), "Known discounted values only; unresolved item prices are reported above when present.", True),
        ("All Cars Needed", format_currency_compact(int(context["all_cars_needed_total"])), "Unique weekly vehicles only; unresolved reference prices are reported above when present.", True),
    ]
    out: list[str] = []
    for label, value, note, is_text in cards:
        out.extend(
            [
                '<article class="card">',
                "  <div>",
                f'    <p class="label">{html.escape(label)}</p>',
                f'    <p class="value{" text" if is_text else ""}">{html.escape(value)}</p>',
                "  </div>",
                f'  <p class="card-note">{html.escape(note)}</p>',
                "</article>",
            ]
        )
    return "\n".join(out)


def _render_deal_value(item: str, group: dict[str, object], price_context: dict[str, object]) -> str:
    tier_percent = group.get("tier_percent")
    tier_label = str(group.get("tier_label", "")).casefold()
    if tier_percent == 100:
        return '<span class="pill value-state value-free">Free</span>'
    context = price_context.get(item)
    if isinstance(context, dict):
        key = f"discounted_price_{tier_percent}"
        value = context.get(key)
        if isinstance(value, int):
            return f'<span class="pill value-state value-price">{html.escape(format_currency_full(value))}</span>'
    if "gun van" in tier_label:
        return '<span class="pill value-state value-check">Check source</span>'
    return '<span class="pill value-state value-check">Check source</span>'


def render_weekly_deals(context: dict[str, object], vehicle_prices: dict[str, dict[str, object]]) -> str:
    groups = context["discounts"]
    price_context = context["price_context"]
    if not groups:
        return '<div class="compact-empty">No weekly deals confirmed.</div>'
    lines = [
        '<div class="section-head">',
        "  <div>",
        '    <h2 id="weekly-deals-title">Weekly Deals Snapshot</h2>',
        "    <p>Confirmed grouped offers from the latest payload. Show every confirmed group with explicit value states.</p>",
        "  </div>",
        "</div>",
        '<ul class="deal-groups" aria-label="Weekly deal groups">',
    ]
    for group in groups:
        items = [item for item in group.get("items", []) if isinstance(item, str)]
        if not items:
            continue
        tier_percent = group.get("tier_percent")
        tier_label = group.get("tier_label")
        if tier_percent == 100:
            group_title = "Free"
        elif tier_label:
            group_title = f"{tier_label} {tier_percent}%"
        else:
            group_title = f"{tier_percent}% Off"
        lines.extend(
            [
                '  <li class="deal-group">',
                f'    <h3 class="tier-label pill">{html.escape(group_title)}</h3>',
                '    <ul class="deal-list">',
            ]
        )
        for item in items:
            is_vehicle = item in vehicle_prices
            lines.append(
                "      <li class=\"deal-row\">"
                + (_vehicle_link(item, vehicle_prices, "deal-name") if is_vehicle else f'<span class="deal-name">{html.escape(item)}</span>')
                + _render_deal_value(item, group, price_context)
                + "</li>"
            )
        lines.extend(
            [
                "    </ul>",
                "  </li>",
            ]
        )
    lines.extend(
        [
            "</ul>",
            '<div class="compact-empty" hidden>',
            "  No weekly deals confirmed.",
            "</div>",
        ]
    )
    return "\n".join(lines)


def _spotlight_group_label(item: dict[str, object]) -> str:
    source = str(item.get("source", "")).casefold()
    if source == "ls_car_meet":
        return "LS Car Meet"
    if source == "luxury_autos":
        return "Luxury Autos"
    if source == "premium_deluxe_motorsport":
        return "Premium Deluxe Motorsport"
    if item.get("opportunity_type") == "premium_test_ride":
        return "Premium Test Ride"
    if item.get("opportunity_type") == "podium":
        return "Podium"
    return "Weekly Vehicle Spotlight"


def _spotlight_note(item: dict[str, object]) -> str:
    opportunity_type = str(item.get("opportunity_type", "")).casefold()
    if opportunity_type == "prize_ride":
        return "Prize Ride"
    if opportunity_type == "test_track":
        return "Test Track"
    if opportunity_type == "showroom":
        return "Showroom"
    if opportunity_type == "premium_test_ride":
        platforms = item.get("platforms")
        if isinstance(platforms, str) and platforms:
            normalized = (
                platforms.replace("XboxSeries", "Xbox Series")
                .replace("PC_Enhanced", "PC Enhanced")
                .replace("PS5", "PS5")
            )
            return " / ".join(part.strip() for part in normalized.split(",") if part.strip())
        return "Platform gated"
    if opportunity_type == "podium":
        return "Lucky Wheel"
    return "Check source"


def render_weekly_vehicle_spotlight(context: dict[str, object], vehicle_prices: dict[str, dict[str, object]]) -> str:
    items = [item for item in context["vehicle_opportunities"] if isinstance(item, dict)]
    if not items:
        return "\n".join(
            [
                '<div class="section-head">',
                "  <div>",
                '    <h2 id="weekly-spotlight-title">Weekly Vehicle Spotlight</h2>',
                "    <p>Confirmed vehicle surfaces from the latest payload. Presence does not imply discount unless the payload says so.</p>",
                "  </div>",
                "</div>",
                '<div class="compact-empty">No spotlight vehicles confirmed.</div>',
            ]
        )

    grouped: dict[str, list[dict[str, object]]] = {}
    for item in items:
        grouped.setdefault(_spotlight_group_label(item), []).append(item)

    lines = [
        '<div class="section-head">',
        "  <div>",
        '    <h2 id="weekly-spotlight-title">Weekly Vehicle Spotlight</h2>',
        "    <p>Confirmed vehicle surfaces from the latest payload. Presence does not imply discount unless the payload says so.</p>",
        "  </div>",
        "</div>",
    ]
    for group_name in SPOTLIGHT_GROUP_ORDER:
        group_items = grouped.get(group_name, [])
        if not group_items:
            continue
        lines.extend(
            [
                f'<ul class="spotlight-group" aria-label="{html.escape(group_name)} spotlight vehicles">',
                f'  <li class="spotlight-title pill">{html.escape(group_name)}</li>',
            ]
        )
        for item in group_items:
            vehicle_name = str(item.get("vehicle_name", ""))
            if not vehicle_name:
                continue
            note = _spotlight_note(item)
            lines.append(
                '  <li class="spotlight-row">'
                + _vehicle_link(vehicle_name, vehicle_prices, "spotlight-name")
                + f'<span class="pill spotlight-note">{html.escape(note)}</span>'
                + "</li>"
            )
        lines.append("</ul>")

    lines.extend(
        [
            '<div class="compact-empty" hidden>',
            "  No spotlight vehicles confirmed.",
            "</div>",
        ]
    )
    return "\n".join(lines)


def plan_phase1_updates(available_markers: list[str]) -> list[str]:
    return [marker for marker in PHASE1_MARKERS if marker in available_markers]


def build_phase1_replacements(context: dict[str, object], vehicle_prices: dict[str, dict[str, object]]) -> dict[str, str]:
    return {
        "header_meta": render_header_meta(context),
        "data_status_note": render_data_status_note(context),
        "summary_cards": render_summary_cards(context),
        "weekly_deals": render_weekly_deals(context, vehicle_prices),
        "weekly_vehicle_spotlight": render_weekly_vehicle_spotlight(context, vehicle_prices),
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate deterministic Phase 1 dashboard blocks.")
    parser.add_argument("--weekly", type=Path, help="Path to a specific weekly_planning_*.json file")
    parser.add_argument("--output", type=Path, default=DEFAULT_DASHBOARD, help="Dashboard HTML output path")
    parser.add_argument("--dry-run", action="store_true", help="Validate inputs and report planned updates without writing")
    parser.add_argument("--check-markers", action="store_true", help="Validate Phase 1 markers and exit without writing")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    dashboard_path = DEFAULT_DASHBOARD
    html_text = dashboard_path.read_text(encoding="utf-8")
    validate_required_markers(html_text, PHASE1_MARKERS)
    marker_plan = plan_phase1_updates(available_markers(html_text))

    if args.check_markers:
        print(f"ok: validated {len(marker_plan)} Phase 1 markers in {dashboard_path.name}")
        return 0

    weekly_path = args.weekly or find_latest_weekly_payload(DEFAULT_DATA_DIR)
    weekly_payload = load_json(weekly_path)
    player_profile = load_json(DEFAULT_PROFILE)
    vehicle_prices = load_vehicle_price_reference(DEFAULT_VEHICLE_PRICES)
    context = build_phase1_context(weekly_payload, player_profile, vehicle_prices)
    replacements = build_phase1_replacements(context, vehicle_prices)

    if args.dry_run:
        print(f"week: {context['week_id']} ({weekly_path.name})")
        print("planned_updates:")
        for marker in marker_plan:
            print(f"  - {marker}")
        if context["unresolved_discount_items"]:
            print(f"warning: unresolved discounted items: {', '.join(context['unresolved_discount_items'])}")
        if context["unresolved_vehicle_prices"]:
            print(f"warning: unresolved vehicle prices: {', '.join(context['unresolved_vehicle_prices'])}")
        return 0

    updated_html = html_text
    for marker, replacement in replacements.items():
        updated_html = replace_marker_block(updated_html, marker, replacement)

    args.output.write_text(updated_html, encoding="utf-8")
    if context["unresolved_discount_items"]:
        print(f"warning: unresolved discounted items: {', '.join(context['unresolved_discount_items'])}", file=sys.stderr)
    if context["unresolved_vehicle_prices"]:
        print(f"warning: skipped {len(context['unresolved_vehicle_prices'])} unresolved vehicle prices for All Cars Needed", file=sys.stderr)
    print(f"updated dashboard: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
