#!/usr/bin/env python3
"""Generate marker-bounded operations blocks for ``pixel-dashboard.html``."""

from __future__ import annotations

import argparse
import html
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.generate_dashboard import (
    DEFAULT_DATA_DIR,
    DEFAULT_PROFILE,
    DashboardMarkerError,
    available_markers,
    build_phase1_context,
    extract_markdown_section,
    find_latest_weekly_payload,
    find_matching_reports,
    format_currency_compact,
    load_json,
    load_text_if_exists,
    load_vehicle_price_reference,
    replace_marker_block,
    validate_required_markers,
)


DEFAULT_PIXEL_DASHBOARD = ROOT / "pixel-dashboard.html"
DEFAULT_VEHICLE_PRICES = ROOT / "data" / "references" / "vehicle_prices.yaml"
AUTOMATION_NOTE = "Thursday 08:00 Bangkok"
PIXEL_MARKERS = [
    "pixel_header_meta",
    "pixel_command_brief",
    "pixel_ignore_callout",
    "pixel_action_queue",
    "pixel_operations_wall",
    "pixel_field_intel",
    "pixel_buy_ledger",
]


def _strip_markdown(text: str) -> str:
    return text.replace("**", "").replace("`", "").strip()


def _extract_metric_chip(*texts: str) -> str | None:
    combined = " ".join(texts)
    multiplier = re.search(r"(\d+)x", combined, flags=re.IGNORECASE)
    if multiplier:
        return f"[{multiplier.group(1)}x]"
    percent_off = re.search(r"(\d+)%\s*off|(\d+)%", combined, flags=re.IGNORECASE)
    if percent_off:
        percent = percent_off.group(1) or percent_off.group(2)
        return f"[{percent}% OFF]"
    if re.search(r"\bfree\b|ฟรี", combined, flags=re.IGNORECASE):
        return "[FREE]"
    cash = re.search(r"GTA\$\s*([\d,]+)", combined, flags=re.IGNORECASE)
    if cash:
        value = int(cash.group(1).replace(",", ""))
        return f"[{format_currency_compact(value)}]"
    return None


def _decision_chip(reason: str, *, positive: bool) -> str:
    lowered = reason.casefold()
    if positive:
        if "free" in lowered or "claim" in lowered or "ฟรี" in lowered:
            return "[BUY]"
        if "only if" in lowered or "เฉพาะถ้า" in lowered or "check" in lowered:
            return "[HOLD]"
        return "[BUY]"
    if "already owned" in lowered or "มีอยู่แล้ว" in lowered:
        return "[IGNORE]"
    if "not priority" in lowered or "ไม่ใช่ priority" in lowered:
        return "[IGNORE]"
    return "[IGNORE]"


def _parse_report_entries(section_text: str | None, *, ordered: bool) -> list[tuple[str, str]]:
    if not section_text:
        return []
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


def _parse_ordered_items(section_text: str | None) -> list[str]:
    if not section_text:
        return []
    items: list[str] = []
    for line in section_text.splitlines():
        match = re.match(r"^\d+\.\s+(.*\S)\s*$", line.strip())
        if match:
            items.append(_strip_markdown(match.group(1)))
    return items


def _clean_item_label(label: str) -> str:
    label = label.split(" - ", 1)[0].strip()
    label = re.sub(r"\s+", " ", label)
    return label


def _bilingual_span(english: str, thai: str) -> str:
    return (
        f'<span data-lang="en">{html.escape(english)}</span>'
        f'<span data-lang="th">{html.escape(thai)}</span>'
    )


def _thai_command_label(label: str) -> str:
    mapping = {
        "HAPPENED": "เกิดอะไรขึ้น",
        "TO DO": "ต้องทำ",
        "BUY": "ซื้อ",
        "WHY": "เหตุผล",
    }
    return mapping.get(label, label)


def _thai_pixel_copy(text: str) -> str:
    mapping = {
        "Money Fronts Special": "สัปดาห์ Money Fronts",
        "Run Money Laundering Missions": "เล่น Money Laundering Missions",
        "Benefactor Terrorbyte": "Benefactor Terrorbyte",
        "Money Fronts Sets The Weekly Cashflow": "Money Fronts คือแกน cashflow ของสัปดาห์นี้",
        "Higgins Helitours": "Higgins Helitours",
        "Heavy Rifle": "Heavy Rifle",
        "Hands On Car Wash / Smoke on the Water 40% off": "Hands On Car Wash / Smoke on the Water ลด 40%",
        "Free weekly claim with direct event relevance.": "รับฟรีประจำสัปดาห์ และเกี่ยวข้องกับ event โดยตรง",
        "Best only when client-job utility matters this week.": "คุ้มที่สุดเฉพาะเมื่อสัปดาห์นี้ต้องใช้ประโยชน์จาก client jobs",
        "Useful only when the combat loadout still has a gap.": "มีประโยชน์เฉพาะเมื่อชุดอาวุธต่อสู้ยังขาดช่องนี้",
        "Discount exists, but it adds little to this week's cashflow plan.": "มีส่วนลดจริง แต่เพิ่มคุณค่าต่อแผน cashflow สัปดาห์นี้น้อย",
    }
    return mapping.get(text, text)


def _normalize_public_reason(text: str) -> str:
    normalized = text.strip()
    replacements = [
        ("โปรไฟล์นี้มีอยู่แล้ว", "Low incremental value this week."),
        ("มี Sparrow อยู่แล้ว จึงไม่ใช่ priority", "Utility overlaps with faster core travel options."),
        (
            "ซื้อเฉพาะถ้ายังไม่มีและอยากใช้ client jobs / Oppressor Mk II ecosystem",
            "Best only when client-job utility matters this week.",
        ),
        (
            "พิจารณาถ้ายังไม่มีหรืออยากเติม combat kit",
            "Useful only when the combat loadout still has a gap.",
        ),
        ("มีอยู่แล้ว", "Low incremental value this week."),
    ]
    for old, new in replacements:
        normalized = normalized.replace(old, new)
    return normalized


def _public_reason_for_item(label: str, reason: str) -> str:
    lowered_label = label.casefold()
    if "money fronts money laundering" in lowered_label:
        return "Top active payout loop this week."
    if "weekly challenge" in lowered_label and "hands on car wash" in lowered_label:
        return "Fast bonus payout tied directly to the Money Fronts loop."
    if "lamar contact missions" in lowered_label:
        return "Strong side rotation for shorter mission bursts."
    if "fine art file" in lowered_label:
        return "Solid solo payout option for longer sessions."
    if "salvage yard" in lowered_label:
        return "No keep eligibility confirmed this week."
    if "hands on car wash / smoke on the water" in lowered_label:
        return "Discount exists, but it adds little to this week's cashflow plan."
    if "sea sparrow" in lowered_label:
        return "Utility overlaps with faster core travel options."
    if "higgins helitours" in lowered_label:
        return "Free weekly claim with direct event relevance."
    if "benefactor terrorbyte" in lowered_label:
        return "Best only when client-job utility matters this week."
    if "heavy rifle" in lowered_label:
        return "Useful only when the combat loadout still has a gap."
    return _normalize_public_reason(reason)


def _command_task(text: str) -> str:
    lowered = text.casefold()
    if "higgins helitours" in lowered:
        return "Claim Higgins Helitours"
    if "lucky wheel" in lowered or "komoda" in lowered:
        return "Spin Lucky Wheel"
    if "hands on car wash legal mission" in lowered:
        return "Complete 3 Legal Missions"
    if "money laundering" in lowered:
        return "Run Money Laundering Missions"
    if "lamar" in lowered:
        return "Run Lamar Contact Missions"
    if "fine art file" in lowered:
        return "Run Fine Art File"
    if "terrorbyte" in lowered:
        return "Check Terrorbyte Ownership"
    if "budget" in lowered or "reserve floor" in lowered:
        return "Protect Budget Floor"
    return text


def _activity_minutes_map(weekly_payload: dict[str, object]) -> dict[str, int]:
    activities = weekly_payload.get("weekly_content", {}).get("featured_activities", [])
    mapping: dict[str, int] = {}
    for item in activities:
        if not isinstance(item, dict):
            continue
        name = item.get("name")
        minutes = item.get("timebox_minutes")
        if isinstance(name, str) and isinstance(minutes, int):
            mapping[name.casefold()] = minutes
    return mapping


def _estimate_queue_minutes(task: str, weekly_payload: dict[str, object]) -> int:
    lowered = task.casefold()
    activity_minutes = _activity_minutes_map(weekly_payload)
    keyword_aliases = {
        "money laundering": "money fronts money laundering missions",
        "hands on car wash legal mission": "weekly challenge - complete three hands on car wash legal missions",
        "lamar": "lamar contact missions",
        "fine art file": "fib priority file - the fine art file",
        "lucky wheel": "casino lucky wheel - lampadati komoda",
    }
    for keyword, activity_name in keyword_aliases.items():
        if keyword in lowered:
            return activity_minutes.get(activity_name, 10)
    if "higgins helitours" in lowered:
        return 2
    if "terrorbyte" in lowered:
        return 2
    if "budget" in lowered or "reserve floor" in lowered:
        return 1
    return 10


def render_pixel_header_meta(context: dict[str, object]) -> str:
    status = "READY TO RUN"
    if context["unresolved_discount_items"] or context["unresolved_vehicle_prices"]:
        status = "REVIEW DATA"
    return "\n".join(
        [
            "<p><strong>Strategy Snapshot</strong></p>",
            f"<p>Week {html.escape(str(context['week_id']))}</p>",
            f"<p>Status: <strong>{html.escape(status)}</strong></p>",
            f"<p>Auto update: {html.escape(AUTOMATION_NOTE)}</p>",
        ]
    )


def render_pixel_command_brief(weekly_payload: dict[str, object], weekly_report_text: str) -> str:
    weekly_content = weekly_payload.get("weekly_content", {})
    headline = str(weekly_content.get("headline", "Weekly Strategy Update")).strip()
    bonuses = weekly_content.get("bonuses", [])
    focus_bonus = next(
        (
            item
            for item in bonuses
            if isinstance(item, dict) and str(item.get("name", "")).casefold().startswith("money fronts")
        ),
        bonuses[0] if bonuses else {},
    )
    focus_chip = _extract_metric_chip(
        str(focus_bonus.get("multiplier", "")),
        str(focus_bonus.get("name", "")),
        str(weekly_content.get("summary", "")),
    ) or "[PRIORITY]"

    play_entries = _parse_report_entries(extract_markdown_section(weekly_report_text, "## What to Play"), ordered=True)
    buy_entries = _parse_report_entries(extract_markdown_section(weekly_report_text, "## What to Buy"), ordered=True)

    top_play_label, _top_play_reason = play_entries[0] if play_entries else (headline, "")
    top_buy_label, top_buy_reason = next(
        (
            (label, reason)
            for label, reason in buy_entries
            if "free" not in reason.casefold() and "ฟรี" not in reason
        ),
        buy_entries[0] if buy_entries else ("Weekly Discount", ""),
    )

    buy_label = _clean_item_label(top_buy_label)
    buy_chip = _extract_metric_chip(top_buy_label, top_buy_reason) or "[BUY]"
    focus_task = _command_task(top_play_label)

    cells = [
        ("HAPPENED", headline, focus_chip),
        ("TO DO", focus_task, focus_chip),
        ("BUY", buy_label, buy_chip),
        ("WHY", "Money Fronts Sets The Weekly Cashflow", "[BEST VALUE]"),
    ]

    lines: list[str] = []
    for label, title, chip in cells:
        lines.extend(
            [
                '<article class="command-cell">',
                f'  <p class="command-label">{_bilingual_span(label, _thai_command_label(label))}</p>',
                f"  <h3>{_bilingual_span(title, _thai_pixel_copy(title))}</h3>",
                f'  <p class="command-chip">{html.escape(chip)}</p>',
                "</article>",
            ]
        )
    return "\n".join(lines)


def render_pixel_ignore_callout(weekly_report_text: str) -> str:
    ignore_entries = _parse_report_entries(
        extract_markdown_section(weekly_report_text, "## What to Ignore"),
        ordered=False,
    )
    labels = [_clean_item_label(label) for label, _reason in ignore_entries[:3]]
    if not labels:
        labels = ["No low-value items flagged"]
    lines = ['<p class="command-label">IGNORE THIS WEEK</p>', "<ul>"]
    for label in labels:
        lines.append(f"  <li>{html.escape(label)}</li>")
    lines.append("</ul>")
    return "\n".join(lines)


def render_pixel_action_queue(weekly_payload: dict[str, object], weekly_report_text: str) -> str:
    tasks = _parse_ordered_items(extract_markdown_section(weekly_report_text, "## Action Queue"))
    if not tasks:
        raise DashboardMarkerError("Action Queue section missing from weekly master plan")
    lines = ['<ol class="queue-list">']
    for task in tasks[:6]:
        command = _command_task(task)
        minutes = _estimate_queue_minutes(task, weekly_payload)
        lines.append(
            "  <li>"
            f'<span class="queue-task">{html.escape(command)}</span>'
            f'<span class="queue-chip">[{minutes}m]</span>'
            "</li>"
        )
    lines.append("</ol>")
    return "\n".join(lines)


def render_pixel_operations_wall(weekly_report_text: str) -> str:
    play_entries = _parse_report_entries(extract_markdown_section(weekly_report_text, "## What to Play"), ordered=True)
    ignore_entries = _parse_report_entries(extract_markdown_section(weekly_report_text, "## What to Ignore"), ordered=False)
    prioritized_ignore = sorted(
        ignore_entries,
        key=lambda entry: 0 if "salvage yard" in entry[0].casefold() else 1,
    )

    groups = [
        ("ACTIVE", [("[ACTIVE]", play_entries[0])] if len(play_entries) > 0 else []),
        ("ACTIVE", [("[READY]", play_entries[1])] if len(play_entries) > 1 else []),
        ("OPTIONAL", [("[OPTIONAL]", entry) for entry in play_entries[2:4]]),
        ("IGNORE", [("[IGNORE]", entry) for entry in prioritized_ignore[:3]]),
    ]

    merged_groups: dict[str, list[tuple[str, tuple[str, str]]]] = {}
    for group_name, items in groups:
        if not items:
            continue
        merged_groups.setdefault(group_name, []).extend(items)

    lines: list[str] = ['<div class="wall-groups">']
    for group_name in ("ACTIVE", "OPTIONAL", "IGNORE"):
        items = merged_groups.get(group_name, [])
        if not items:
            continue
        lines.extend([f'  <article class="wall-group">', f"    <h3>{html.escape(group_name)}</h3>"])
        for chip, (label, reason) in items:
            lines.extend(
                [
                    '    <div class="wall-item">',
                    '      <div class="wall-item-head">',
                    f"        <span>{html.escape(_clean_item_label(label))}</span>",
                    f'        <span class="status-chip">{html.escape(chip)}</span>',
                    "      </div>",
                    f"      <p>{html.escape(_public_reason_for_item(_clean_item_label(label), reason))}</p>",
                    "    </div>",
                ]
            )
        lines.append("  </article>")
    lines.append("</div>")
    return "\n".join(lines)


def render_pixel_field_intel(weekly_payload: dict[str, object]) -> str:
    weekly_content = weekly_payload.get("weekly_content", {})
    bonuses = [item for item in weekly_content.get("bonuses", []) if isinstance(item, dict)]
    discounts = [item for item in weekly_content.get("discounts", []) if isinstance(item, dict)]
    events = [item for item in weekly_content.get("events", []) if isinstance(item, dict)]

    intel_rows: list[tuple[str, str, str]] = []
    if bonuses:
        top_bonus = bonuses[0]
        intel_rows.append(
            (
                "[BONUS]",
                str(top_bonus.get("name", "Weekly Bonus")),
                f"{top_bonus.get('multiplier', 'Boost')} {top_bonus.get('reward_type', '').strip()} this week".strip(),
            )
        )
    free_claim_event = next(
        (
            item
            for item in events
            if str(item.get("name", "")).casefold() == "free business claim"
        ),
        None,
    )
    if free_claim_event:
        intel_rows.append(
            (
                "[LIMITED]",
                str(free_claim_event.get("vehicle", "Weekly Claim")),
                "Free claim ends this week",
            )
        )
    discount_group = next(
        (
            group
            for group in discounts
            if isinstance(group.get("tier_percent"), int) and int(group["tier_percent"]) < 100
        ),
        None,
    )
    if discount_group:
        items = [item for item in discount_group.get("items", []) if isinstance(item, str)]
        if items:
            intel_rows.append(
                (
                    "[DISCOUNT]",
                    items[0],
                    f"{discount_group.get('tier_percent')}% off this week",
                )
            )
    prize_event = next(
        (
            item
            for item in events
            if str(item.get("name", "")).casefold() in {"podium vehicle", "prize ride challenge"}
        ),
        None,
    )
    if prize_event:
        intel_rows.append(
            (
                "[PRIZE]",
                str(prize_event.get("vehicle", "Weekly Prize")),
                "Limited-time reward surface this week",
            )
        )

    lines = ['<div class="intel-list">']
    for label, item, implication in intel_rows[:4]:
        lines.extend(
            [
                '  <article class="intel-item">',
                f'    <p class="intel-label">{html.escape(label)}</p>',
                f"    <h3>{html.escape(item)}</h3>",
                f"    <p>{html.escape(implication)}</p>",
                "  </article>",
            ]
        )
    lines.append("</div>")
    return "\n".join(lines)


def render_pixel_buy_ledger(weekly_report_text: str) -> str:
    buy_entries = _parse_report_entries(extract_markdown_section(weekly_report_text, "## What to Buy"), ordered=True)
    ignore_entries = _parse_report_entries(extract_markdown_section(weekly_report_text, "## What to Ignore"), ordered=False)

    rows: list[tuple[str, str, str]] = []
    for label, reason in buy_entries[:3]:
        rows.append((_clean_item_label(label), _decision_chip(reason, positive=True), reason))
    for label, reason in ignore_entries[:2]:
        rows.append((_clean_item_label(label), _decision_chip(reason, positive=False), reason))

    lines = ['<div class="ledger-list">']
    for item, chip, reason in rows[:4]:
        lines.extend(
            [
                '  <article class="ledger-item">',
                f'    <div class="ledger-head"><h3>{_bilingual_span(item, _thai_pixel_copy(item))}</h3><span class="decision-chip">{html.escape(chip)}</span></div>',
                f"    <p>{_bilingual_span(_public_reason_for_item(item, reason), _thai_pixel_copy(_public_reason_for_item(item, reason)))}</p>",
                "  </article>",
            ]
        )
    lines.append("</div>")
    return "\n".join(lines)


def build_pixel_replacements(
    weekly_payload: dict[str, object],
    player_profile: dict[str, object],
    weekly_report_text: str,
) -> dict[str, str]:
    vehicle_prices = load_vehicle_price_reference(DEFAULT_VEHICLE_PRICES)
    context = build_phase1_context(weekly_payload, player_profile, vehicle_prices)
    return {
        "pixel_header_meta": render_pixel_header_meta(context),
        "pixel_command_brief": render_pixel_command_brief(weekly_payload, weekly_report_text),
        "pixel_ignore_callout": render_pixel_ignore_callout(weekly_report_text),
        "pixel_action_queue": render_pixel_action_queue(weekly_payload, weekly_report_text),
        "pixel_operations_wall": render_pixel_operations_wall(weekly_report_text),
        "pixel_field_intel": render_pixel_field_intel(weekly_payload),
        "pixel_buy_ledger": render_pixel_buy_ledger(weekly_report_text),
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate marker-bounded operations blocks for pixel-dashboard.html.")
    parser.add_argument("--weekly", type=Path, help="Path to a specific weekly_planning_*.json file")
    parser.add_argument("--output", type=Path, default=DEFAULT_PIXEL_DASHBOARD, help="Pixel dashboard HTML output path")
    parser.add_argument("--dry-run", action="store_true", help="Validate inputs and report planned updates without writing")
    parser.add_argument("--check-markers", action="store_true", help="Validate required pixel markers and exit without writing")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    html_text = DEFAULT_PIXEL_DASHBOARD.read_text(encoding="utf-8")
    validate_required_markers(html_text, PIXEL_MARKERS)
    marker_plan = [marker for marker in PIXEL_MARKERS if marker in available_markers(html_text)]

    if args.check_markers:
        print(f"ok: validated {len(marker_plan)} pixel markers in {DEFAULT_PIXEL_DASHBOARD.name}")
        return 0

    weekly_path = args.weekly or find_latest_weekly_payload(DEFAULT_DATA_DIR)
    weekly_payload = load_json(weekly_path)
    player_profile = load_json(DEFAULT_PROFILE)
    report_paths = find_matching_reports(str(weekly_payload["week"]["id"]))
    weekly_report_text = load_text_if_exists(report_paths["weekly_master_plan"])
    if not weekly_report_text:
        raise FileNotFoundError(f"Missing weekly master plan report for {weekly_payload['week']['id']}")

    replacements = build_pixel_replacements(weekly_payload, player_profile, weekly_report_text)

    if args.dry_run:
        print(f"week: {weekly_payload['week']['id']} ({weekly_path.name})")
        print("planned_updates:")
        for marker in marker_plan:
            print(f"  - {marker}")
        return 0

    updated_html = html_text
    for marker, replacement in replacements.items():
        updated_html = replace_marker_block(updated_html, marker, replacement)

    args.output.write_text(updated_html, encoding="utf-8")
    print(f"updated pixel dashboard: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
