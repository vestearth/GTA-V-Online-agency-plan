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

PHASE2_MARKERS = [
    "current_focus",
    "next_claim_buy",
    "weekly_action_plan",
    "what_to_buy_ignore",
    "asset_overview",
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


def week_id_to_report_suffix(week_id: str) -> str:
    return week_id.lower().replace("-", "_")


def find_matching_reports(week_id: str) -> dict[str, Path]:
    suffix = week_id_to_report_suffix(week_id)
    reports_dir = ROOT / "reports"
    return {
        "weekly_master_plan": reports_dir / f"weekly_master_plan_{suffix}.md",
        "event_master_plan": reports_dir / f"event_master_plan_{suffix}.md",
        "income_scenarios": reports_dir / f"weekly_master_plan_{suffix}_income_scenarios.md",
    }


def load_text_if_exists(path: Path) -> str | None:
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8")


def validate_required_markers(html_text: str, required_markers: list[str]) -> None:
    missing: list[str] = []
    for marker in required_markers:
        if f"<!-- START: {marker} -->" not in html_text or f"<!-- END: {marker} -->" not in html_text:
            missing.append(marker)
    if missing:
        raise DashboardMarkerError(f"Missing required dashboard markers: {', '.join(missing)}")


def available_markers(html_text: str) -> list[str]:
    return re.findall(r"<!-- START: ([a-z0-9_]+) -->", html_text)


def extract_marker_block(html_text: str, marker: str) -> str | None:
    pattern = re.compile(
        rf"<!-- START: {re.escape(marker)} -->\s*(?P<body>.*?)\s*<!-- END: {re.escape(marker)} -->",
        flags=re.DOTALL,
    )
    match = pattern.search(html_text)
    if not match:
        return None
    return match.group("body").strip()


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
    return "\n".join(
        [
            '<article class="card">',
            "  <div>",
            '    <p class="label">Current Focus</p>',
            "    <!-- START: current_focus -->",
            '    <p class="value text">Money Fronts 4x loop</p>',
            '    <p class="card-note">Run legal missions first, then rotate into laundering for the strongest active ROI this week.</p>',
            "    <!-- END: current_focus -->",
            "  </div>",
            "</article>",
            '<article class="card">',
            "  <div>",
            '    <p class="label">Next Claim / Buy</p>',
            "    <!-- START: next_claim_buy -->",
            '    <p class="value text">Claim Higgins Helitours</p>',
            '    <p class="card-note">Free this week and directly relevant to the Money Fronts network before considering optional purchases.</p>',
            "    <!-- END: next_claim_buy -->",
            "  </div>",
            "</article>",
            '<article class="card">',
            "  <div>",
            '    <p class="label">Discounted Items Total</p>',
            f'    <p class="value text">{html.escape(format_currency_compact(int(context["discounted_items_total"])))}</p>',
            "  </div>",
            '  <p class="card-note">Known discounted values only; unresolved item prices are reported above when present.</p>',
            "</article>",
            '<article class="card">',
            "  <div>",
            '    <p class="label">All Cars Needed</p>',
            f'    <p class="value text">{html.escape(format_currency_compact(int(context["all_cars_needed_total"])))}</p>',
            "  </div>",
            '  <p class="card-note">Unique weekly vehicles only; unresolved reference prices are reported above when present.</p>',
            "</article>",
        ]
    )


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


def extract_markdown_section(markdown_text: str, heading: str) -> str | None:
    pattern = re.compile(
        rf"^{re.escape(heading)}\s*$\n(?P<body>.*?)(?=^##\s|\Z)",
        flags=re.MULTILINE | re.DOTALL,
    )
    match = pattern.search(markdown_text)
    if not match:
        return None
    body = match.group("body").strip()
    return body or None


def _parse_ordered_items(section_text: str) -> list[str]:
    items: list[str] = []
    for line in section_text.splitlines():
        match = re.match(r"^\d+\.\s+(.*\S)\s*$", line.strip())
        if match:
            items.append(match.group(1).strip())
    return items


def _strip_markdown(text: str) -> str:
    return text.replace("**", "").replace("`", "").strip()


def render_current_focus(weekly_payload: dict[str, object], weekly_report_text: str | None) -> str | None:
    weekly_content = weekly_payload.get("weekly_content", {})
    headline = weekly_content.get("headline")
    summary = weekly_content.get("summary")
    if not isinstance(headline, str) or not headline:
        return None

    if "money fronts" in headline.casefold():
        main = "Money Fronts 4x loop"
        copy_text = "Run legal missions first, then rotate into laundering for the strongest active ROI this week."
    else:
        main = headline
        copy_text = summary if isinstance(summary, str) and summary else "Weekly focus generated from the current planning payload."

    return "\n".join(
        [
            f'<p class="value text">{html.escape(main)}</p>',
            f'<p class="card-note">{html.escape(copy_text)}</p>',
        ]
    )


def _action_step_note(step_text: str) -> str:
    lowered = step_text.casefold()
    if "higgins helitours" in lowered:
        return "Free weekly claim before the event week ends."
    if "lucky wheel" in lowered or "komoda" in lowered:
        return "Quick casino spin to cover the podium chance before longer loops."
    if "legal mission" in lowered or "hands on car wash" in lowered:
        return "Completes the weekly challenge for GTA$100,000 while supporting the Money Fronts loop."
    if "money laundering" in lowered:
        return "Primary money loop from the weekly master plan."
    if "lamar" in lowered:
        return "Use as a shorter rotation when you want a break from Money Fronts."
    if "fine art file" in lowered:
        return "Strong solo filler for longer sessions once the main loop is underway."
    if "terrorbyte" in lowered:
        return "Ownership check first; only buy if the utility matters this week."
    if "budget" in lowered or "รถลด" in step_text:
        return "Protect the spend cap by skipping collection buys that do not improve cashflow."
    return "Generated from the weekly master plan action queue."


def render_weekly_action_plan(weekly_report_text: str) -> str | None:
    section = extract_markdown_section(weekly_report_text, "## Action Queue")
    if not section:
        return None
    steps = _parse_ordered_items(section)
    if len(steps) < 3:
        return None
    lines = ['<ol class="steps">']
    for step in steps:
        title = _strip_markdown(step)
        note = _action_step_note(title)
        lines.extend(
            [
                "  <li>",
                "    <div>",
                f"      <h3>{html.escape(title)}</h3>",
                f'      <p class="card-note">{html.escape(note)}</p>',
                "    </div>",
                "  </li>",
            ]
        )
    lines.append("</ol>")
    return "\n".join(lines)


def _parse_report_entries(section_text: str, ordered: bool) -> list[tuple[str, str]]:
    if ordered:
        pattern = re.compile(r"^\d+\.\s+\*\*(.*?)\*\*\s*-\s*(.+)$")
    else:
        pattern = re.compile(r"^-\s+\*\*(.*?)\*\*\s*-\s*(.+)$")
    entries: list[tuple[str, str]] = []
    for line in section_text.splitlines():
        match = pattern.match(line.strip())
        if not match:
            continue
        entries.append((_strip_markdown(match.group(1)), _strip_markdown(match.group(2))))
    return entries


def _clean_entry_label(label: str) -> str:
    if " - " in label:
        return label.split(" - ", 1)[0].strip()
    return label.strip()


def _buy_ruling(label: str, reason: str) -> tuple[str, str]:
    lowered = f"{label} {reason}".casefold()
    if "free" in lowered or "ฟรี" in lowered or "claim" in lowered:
        return ("Claim", "owned")
    if "ถ้ายังไม่มี" in reason or "buy only if" in lowered or "check" in lowered:
        return ("Check", "watch")
    return ("Buy", "watch")


def _ignore_ruling(label: str, reason: str) -> tuple[str, str]:
    lowered = f"{label} {reason}".casefold()
    if "claimable" in lowered or "keep eligibility" in lowered or "salvage yard" in lowered:
        return ("Do not claim", "warn")
    if "already owned" in lowered or "มีอยู่แล้ว" in lowered:
        return ("Skip", "low")
    return ("Ignore", "low")


def render_next_claim_buy(weekly_report_text: str, event_report_text: str | None = None) -> str | None:
    buy_section = extract_markdown_section(weekly_report_text, "## What to Buy")
    if not buy_section:
        return None
    buy_entries = _parse_report_entries(buy_section, ordered=True)
    if not buy_entries:
        return None
    label, reason = buy_entries[0]
    clean_label = _clean_entry_label(label)
    if "free" in reason.casefold() or "ฟรี" in reason:
        main = f"Claim {clean_label}"
    elif "check" in reason.casefold() or "ถ้ายังไม่มี" in reason:
        main = f"Check {clean_label}"
    else:
        main = f"Buy {clean_label}"
    return "\n".join(
        [
            f'<p class="value text">{html.escape(main)}</p>',
            f'<p class="card-note">{html.escape(reason)}</p>',
        ]
    )


def render_what_to_buy_ignore(weekly_report_text: str, event_report_text: str | None = None) -> str | None:
    buy_section = extract_markdown_section(weekly_report_text, "## What to Buy")
    ignore_section = extract_markdown_section(weekly_report_text, "## What to Ignore")
    if not buy_section or not ignore_section:
        return None
    buy_entries = _parse_report_entries(buy_section, ordered=True)
    ignore_entries = _parse_report_entries(ignore_section, ordered=False)
    if not buy_entries or not ignore_entries:
        return None
    rows: list[tuple[str, str, str, str]] = []
    for label, reason in buy_entries:
        ruling, css_class = _buy_ruling(label, reason)
        rows.append((_clean_entry_label(label), ruling, css_class, reason))
    for label, reason in ignore_entries:
        ruling, css_class = _ignore_ruling(label, reason)
        rows.append((_clean_entry_label(label), ruling, css_class, reason))

    lines: list[str] = ["<tbody>"]
    for item, ruling, css_class, reason in rows:
        lines.extend(
            [
                "  <tr>",
                f'    <td data-label="Item">{html.escape(item)}</td>',
                '    <td data-label="Ruling">',
                f'      <span class="pill {css_class}">{html.escape(ruling)}</span>',
                "    </td>",
                f'    <td data-label="Reason">{html.escape(reason)}</td>',
                "  </tr>",
            ]
        )
    lines.append("</tbody>")
    return "\n".join(lines)


def _owned_properties_set(player_profile: dict[str, object]) -> set[str]:
    owned_assets = player_profile.get("owned_assets", {})
    properties = owned_assets.get("properties", []) if isinstance(owned_assets, dict) else []
    return {prop for prop in properties if isinstance(prop, str)}


def _owned_vehicles_set(player_profile: dict[str, object]) -> set[str]:
    owned_assets = player_profile.get("owned_assets", {})
    vehicles = owned_assets.get("vehicles", []) if isinstance(owned_assets, dict) else []
    return {vehicle for vehicle in vehicles if isinstance(vehicle, str)}


def render_asset_overview(player_profile: dict[str, object], weekly_payload: dict[str, object], weekly_report_text: str) -> str | None:
    owned_properties = _owned_properties_set(player_profile)
    owned_vehicles = _owned_vehicles_set(player_profile)
    upgrades = player_profile.get("owned_assets", {}).get("upgrades", {})
    rows: list[tuple[str, str, str, str, str, str]] = []

    def add_row(asset: str, status_label: str, status_class: str, priority_label: str, priority_class: str, note: str) -> None:
        rows.append((asset, status_label, status_class, priority_label, priority_class, note))

    if "Hands On Car Wash Money Front" in owned_properties:
        add_row("Hands On Car Wash", "Owned", "owned", "High", "high", "Core weekly loop for legal missions, money laundering, and the free Higgins claim.")
    if "Smoke on the Water Money Front" in owned_properties:
        add_row("Smoke on the Water", "Owned", "owned", "Medium", "medium", "Already in the Money Fronts network, so the 40% discount is not a buy signal.")
    if "Nightclub" in owned_properties:
        add_row("Nightclub", "Owned", "owned", "Medium", "medium", "Passive filler between active weekly jobs.")
    if "Agency" in owned_properties:
        add_row("Agency", "Owned", "owned", "Medium", "medium", "Reliable fallback loop when you want to rotate away from Money Fronts.")
    if "Bunker" in owned_properties:
        add_row("Bunker", "Owned", "owned", "Medium", "medium", "Passive stock remains useful while the event loop does the heavy lifting.")
    if "The Garment Factory" in owned_properties:
        add_row("The Garment Factory", "Owned", "owned", "Medium", "medium", "Unlocks The Fine Art File 2x as a longer-session solo option.")
    if "Kosatka" in owned_properties or "Sparrow" in owned_vehicles:
        add_row("Kosatka + Sparrow", "Owned", "owned", "Medium", "medium", "Core solo infrastructure; the Sea Sparrow discount overlaps an existing use case.")
    if "Mammoth Avenger" in owned_properties:
        avenger_note = "Workshop upgrade marked done; convenience utility matters more than urgent ROI."
        if isinstance(upgrades, dict) and not upgrades.get("avenger_workshop", False):
            avenger_note = "Owned, but check workshop readiness before treating it as a utility anchor."
        add_row("Mammoth Avenger", "Owned", "owned", "Low", "low", avenger_note)
    if "Galaxy Super Yacht" in owned_properties:
        add_row("Galaxy Super Yacht", "Owned", "owned", "Low", "low", "Luxury/status asset with no urgent weekly action attached.")

    if "benefactor terrorbyte" not in {vehicle.casefold() for vehicle in owned_vehicles} and "Terrorbyte" in weekly_report_text:
        add_row("Benefactor Terrorbyte", "Check", "watch", "Conditional", "medium", "Discounted this week; buy only if it is still missing and the utility matters.")

    if len(rows) < 5:
        return None

    lines = ["<tbody>"]
    for asset, status_label, status_class, priority_label, priority_class, note in rows:
        lines.extend(
            [
                "  <tr>",
                f'    <td data-label="Asset">{html.escape(asset)}</td>',
                '    <td data-label="Status">',
                f'      <span class="pill {status_class}">{html.escape(status_label)}</span>',
                "    </td>",
                '    <td data-label="Priority">',
                f'      <span class="priority {priority_class}">{html.escape(priority_label)}</span>',
                "    </td>",
                f'    <td data-label="Note">{html.escape(note)}</td>',
                "  </tr>",
            ]
        )
    lines.append("</tbody>")
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


def plan_phase2_updates(available_markers: list[str]) -> list[str]:
    return [marker for marker in PHASE2_MARKERS if marker in available_markers]


def build_phase2_replacements(
    html_text: str,
    weekly_payload: dict[str, object],
    player_profile: dict[str, object],
    weekly_report_text: str | None,
    event_report_text: str | None,
) -> tuple[dict[str, str], list[str], list[str]]:
    replacements: dict[str, str] = {}
    updated_markers: list[str] = []
    preserved_markers: list[str] = []

    marker_to_renderer = {
        "current_focus": lambda: render_current_focus(weekly_payload, weekly_report_text),
        "next_claim_buy": lambda: render_next_claim_buy(weekly_report_text or "", event_report_text),
        "weekly_action_plan": lambda: render_weekly_action_plan(weekly_report_text or ""),
        "what_to_buy_ignore": lambda: render_what_to_buy_ignore(weekly_report_text or "", event_report_text),
        "asset_overview": lambda: render_asset_overview(player_profile, weekly_payload, weekly_report_text or ""),
    }

    for marker, renderer in marker_to_renderer.items():
        existing = extract_marker_block(html_text, marker)
        if existing is None:
            continue
        replacement = renderer()
        if replacement is None:
            preserved_markers.append(marker)
            continue
        replacements[marker] = replacement
        updated_markers.append(marker)

    return replacements, updated_markers, preserved_markers


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate dashboard blocks from repository data.")
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
    available = available_markers(html_text)
    marker_plan = plan_phase1_updates(available)
    phase2_plan = plan_phase2_updates(available)

    if args.check_markers:
        print(f"ok: validated {len(marker_plan)} Phase 1 markers in {dashboard_path.name}")
        return 0

    weekly_path = args.weekly or find_latest_weekly_payload(DEFAULT_DATA_DIR)
    weekly_payload = load_json(weekly_path)
    player_profile = load_json(DEFAULT_PROFILE)
    vehicle_prices = load_vehicle_price_reference(DEFAULT_VEHICLE_PRICES)
    context = build_phase1_context(weekly_payload, player_profile, vehicle_prices)
    replacements = build_phase1_replacements(context, vehicle_prices)
    report_paths = find_matching_reports(str(context["week_id"]))
    weekly_report_text = load_text_if_exists(report_paths["weekly_master_plan"])
    event_report_text = load_text_if_exists(report_paths["event_master_plan"])
    phase2_replacements, phase2_updated, phase2_preserved = build_phase2_replacements(
        html_text,
        weekly_payload,
        player_profile,
        weekly_report_text,
        event_report_text,
    )

    if args.dry_run:
        print(f"week: {context['week_id']} ({weekly_path.name})")
        print("planned_updates:")
        for marker in marker_plan:
            print(f"  - {marker}")
        for marker in phase2_updated:
            print(f"  - {marker}")
        if phase2_preserved:
            print("preserved_blocks:")
            for marker in phase2_preserved:
                print(f"  - {marker}")
        if context["unresolved_discount_items"]:
            print(f"warning: unresolved discounted items: {', '.join(context['unresolved_discount_items'])}")
        if context["unresolved_vehicle_prices"]:
            print(f"warning: unresolved vehicle prices: {', '.join(context['unresolved_vehicle_prices'])}")
        if not weekly_report_text:
            print("warning: weekly master plan report missing; Phase 2 report-derived blocks preserved where applicable")
        return 0

    updated_html = html_text
    for marker, replacement in replacements.items():
        updated_html = replace_marker_block(updated_html, marker, replacement)
    for marker, replacement in phase2_replacements.items():
        updated_html = replace_marker_block(updated_html, marker, replacement)

    args.output.write_text(updated_html, encoding="utf-8")
    if context["unresolved_discount_items"]:
        print(f"warning: unresolved discounted items: {', '.join(context['unresolved_discount_items'])}", file=sys.stderr)
    if context["unresolved_vehicle_prices"]:
        print(f"warning: skipped {len(context['unresolved_vehicle_prices'])} unresolved vehicle prices for All Cars Needed", file=sys.stderr)
    if phase2_preserved:
        print(f"warning: preserved Phase 2 blocks due to low confidence: {', '.join(phase2_preserved)}", file=sys.stderr)
    print(f"updated dashboard: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
