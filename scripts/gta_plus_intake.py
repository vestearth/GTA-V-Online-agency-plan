"""Validate monthly intake and combine only explicitly documented member overlays."""
from __future__ import annotations
import argparse
import copy
import datetime as dt
import html
import json
from pathlib import Path
from urllib.parse import urlparse

try:
    from scripts.content_safety import utc_now, write_json, payload_digest
except ModuleNotFoundError:
    from content_safety import utc_now, write_json, payload_digest

GROUPS = ("claimable_vehicles", "member_bonuses", "member_discounts", "freebies", "standing_perks")


def valid_sources(urls):
    if not isinstance(urls, list) or not urls:
        return False
    for url in urls:
        if not isinstance(url, str):
            return False
        try:
            parsed = urlparse(url)
            if parsed.scheme != "https" or not parsed.hostname:
                return False
        except ValueError:
            return False
    return True


def today_bangkok():
    return (utc_now() + dt.timedelta(hours=7)).date()


def monthly_issues(payload, today=None):
    today = today or today_bangkok()
    issues = []
    if not isinstance(payload, dict):
        return ["Invalid monthly payload object"]
    if payload.get("schema_mode") != "gta_plus_monthly":
        issues.append("Not a monthly payload")
    period = payload.get("membership_period", {})
    if not isinstance(period, dict) or not isinstance(payload.get("monthly_benefits", {}), dict):
        return ["Invalid monthly period/benefits object"]
    try:
        start = dt.date.fromisoformat(period.get("start_date", ""))
        end = dt.date.fromisoformat(period.get("end_date", ""))
        if not start <= today <= end:
            issues.append("GTA+ period has ended or has not started")
        if start >= end:
            issues.append("Invalid monthly period")
    except (ValueError, TypeError):
        issues.append("Unknown membership period")
    review = payload.get("review", {})
    if not isinstance(review, dict):
        return ["Invalid monthly review object"]
    if payload.get("review_state") != "confirmed" or not review.get("reviewer"):
        issues.append("Monthly review is missing")
    if review.get("payload_sha256") != payload_digest(payload):
        issues.append("Monthly payload changed since review or has no review hash")
    if not valid_sources(period.get("source_urls")):
        issues.append("Monthly sources are missing")
    benefits = payload.get("monthly_benefits", {})
    deposit = benefits.get("gta_dollar_deposit")
    if deposit is not None and (type(deposit) is not int or deposit < 0):
        issues.append("Invalid monthly deposit value")
    for group in GROUPS:
        records = benefits.get(group, [])
        if not isinstance(records, list):
            issues.append(f"Invalid benefit group: {group}")
            continue
        for record in records:
            if not isinstance(record, dict) or record.get("review_state") != "confirmed" or not valid_sources(record.get("source_urls")):
                issues.append(f"Unreviewed/unsourced benefit: {group}")
            elif not isinstance(record.get("eligibility"), dict):
                issues.append(f"Missing platform/edition/claim eligibility: {group}")
            elif any(not record["eligibility"].get(k) for k in ("platform", "edition", "claim_scope")):
                issues.append(f"Incomplete eligibility: {group}")
            if isinstance(record, dict) and group in ("claimable_vehicles", "freebies") and record.get("claim_method", "unknown") not in ("unknown", "login", "vinewood_car_club", "in_game_purchase"):
                issues.append(f"Unknown claim method vocabulary: {group}")
            if isinstance(record, dict) and group == "member_discounts" and (type(record.get("percent_off")) is not int or not 0 <= record["percent_off"] <= 100):
                issues.append("Invalid monthly discount")
    if benefits.get("gta_dollar_deposit") is not None:
        evidence = benefits.get("deposit_evidence", {})
        if evidence.get("review_state") != "confirmed" or not valid_sources(evidence.get("source_urls")):
            issues.append("Deposit lacks reviewed evidence")
    return issues


def select_monthly(data_dir, today=None):
    """Period-based selection; reject overlapping approved periods instead of guessing by filename."""
    today = today or today_bangkok()
    active = []
    for path in sorted(data_dir.glob("gta_plus_monthly_*.json")):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if not monthly_issues(payload, today):
            active.append(payload)
    if len(active) == 1:
        return active[0], "confirmed"
    return {}, "unknown: overlapping periods" if active else "stale/unknown: no reviewed current GTA+ period"


def monthly_status_html(payload, today=None):
    issues = monthly_issues(payload, today)
    if not issues:
        return ""
    return ('<p role="status" class="muted">GTA+ — ' + html.escape("; ".join(issues))
            + ' / ยังไม่มีข้อมูลสิทธิ์รอบปัจจุบันที่ผ่านรีวิว</p>')


def guard_monthly_html(content, payload):
    end = dt.date.fromisoformat(payload["membership_period"]["end_date"]) + dt.timedelta(days=1)
    return f'<div data-gta-plus-until="{end.isoformat()}T00:00:00+07:00">' + content + '</div>'


def claim_before_expiry(payload, today=None):
    if monthly_issues(payload, today):
        return []
    claims = []
    for group in ("claimable_vehicles", "freebies"):
        for item in payload.get("monthly_benefits", {}).get(group, []):
            method = item.get("claim_method", "unknown")
            claims.append({"item": item.get("vehicle", item.get("item")), "claim_method": method,
                           "location": item.get("location"), "eligibility": item.get("eligibility", {}),
                           "expires": payload["membership_period"]["end_date"], "source_urls": item["source_urls"]})
    return claims


def combine_weekly_bonuses(weekly, monthly, today=None):
    rows = []
    valid = not monthly_issues(monthly, today)
    try:
        week_start = dt.date.fromisoformat(weekly["week"]["start_date"])
        week_end = dt.date.fromisoformat(weekly["week"]["end_date"])
        period = monthly["membership_period"]
        # A monthly multiplier covering only part of the week needs a dated split, not a weekly blanket claim.
        valid = valid and dt.date.fromisoformat(period["start_date"]) <= week_start and dt.date.fromisoformat(period["end_date"]) >= week_end - dt.timedelta(days=1)
    except (ValueError, KeyError, TypeError):
        valid = False
    member = monthly.get("monthly_benefits", {}).get("member_bonuses", []) if valid else []
    for bonus in weekly.get("weekly_content", {}).get("bonuses", []):
        row = {"name": bonus.get("name"), "non_member": bonus.get("multiplier"), "member": "unknown", "source_urls": []}
        matches = [m for m in member if m.get("name", "").casefold() == str(bonus.get("name", "")).casefold()]
        if len(matches) == 1:
            entry = matches[0]
            row["member"] = entry.get("multiplier", "unknown")
            row["combination_state"] = "separate; stacking unknown"
            rule = entry.get("weekly_overlay", {})
            if (rule.get("review_state") == "confirmed" and valid_sources(rule.get("source_urls"))
                    and rule.get("week_id") == weekly.get("week", {}).get("id")
                    and rule.get("weekly_multiplier") == bonus.get("multiplier")
                    and rule.get("member_multiplier") == entry.get("multiplier")
                    and rule.get("reward_type") == bonus.get("reward_type")
                    and rule.get("reward_type") == entry.get("reward_type")
                    and isinstance(rule.get("effective_multiplier"), (int, float))
                    and not isinstance(rule.get("effective_multiplier"), bool)
                    and rule["effective_multiplier"] > 0):
                row.update(member=f'{rule["effective_multiplier"]}x', combination_state="documented overlay",
                           source_urls=rule["source_urls"])
        elif len(matches) > 1:
            row["combination_state"] = "conflicting member claims"
        rows.append(row)
    return rows


def approve_monthly(candidate, root, reviewer, today=None):
    payload = copy.deepcopy(json.loads(candidate.read_text(encoding="utf-8")))
    if not reviewer.strip():
        raise ValueError("Reviewer required")
    payload.update(review_state="confirmed", review={"reviewer": reviewer, "reviewed_at": utc_now().isoformat()})
    payload["review"]["payload_sha256"] = payload_digest(payload)
    issues = monthly_issues(payload, today)
    if issues:
        raise ValueError("; ".join(issues))
    start = payload["membership_period"]["start_date"]
    existing, state = select_monthly(root / "data", today)
    if existing and existing["membership_period"]["start_date"] != start:
        raise ValueError("Conflicting active membership period")
    path = root / "data" / f"gta_plus_monthly_{start[:7].replace('-', '_')}.json"
    write_json(path, payload)
    return path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("candidate", type=Path)
    parser.add_argument("--reviewer", help="Explicit review handoff; without this, validate only")
    args = parser.parse_args()
    try:
        if args.reviewer:
            print(approve_monthly(args.candidate, Path(__file__).resolve().parents[1], args.reviewer))
        else:
            issues = monthly_issues(json.loads(args.candidate.read_text(encoding="utf-8")))
            print(json.dumps({"issues": issues}))
            return 1 if issues else 0
    except (OSError, ValueError) as exc:
        parser.exit(1, str(exc) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
