"""Synthetic reviewed records for offline contract tests; never live game data."""
import datetime as dt
import json
from pathlib import Path
from scripts.content_safety import report_paths, payload_digest
from scripts.review_weekly_candidate import approve

TODAY = dt.date(2026, 10, 14)
URL = "https://www.rockstargames.com/newswire/article/test123/gta-online-weekly-bonuses"


def weekly_payload():
    return {"schema_version": "2.0", "schema_mode": "weekly_planning", "content_quality": "needs_review",
            "week": {"id": "2026-W41", "label": "October 8 - October 15 2026", "start_date": "2026-10-08", "end_date": "2026-10-15"},
            "player_context": {"owned_assets": {"properties": []}, "constraints": {"hours_available": 2}},
            "provenance": {"url": URL, "published_date": "2026-10-08", "article_sha256": "a" * 64,
                           "title": "GTA Online Weekly Bonuses"},
            "weekly_content": {"headline": "Fixture weekly bonuses", "events": [], "bonuses": [{"name": "Nightclub Sell Missions", "multiplier": "2x", "reward_type": "GTA$ & RP"}],
                               "discounts": [{"tier_percent": 30, "items": ["Pfister Growler"]}],
                               "vehicle_opportunities": [{"vehicle_name": "Pfister Growler", "opportunity_type": "discount"}]}}


def approved_workspace(root):
    (root / "data/candidates").mkdir(parents=True, exist_ok=True)
    (root / "reports").mkdir(exist_ok=True)
    payload = weekly_payload()
    for path in report_paths(root, payload["week"]["id"]):
        path.write_text("# Fixture report - 2026-W41\n\n## What to Play\n\n1. **Nightclub Sell Missions** - Fixture\n\n## What to Buy\n\n1. **Pfister Growler** - Fixture\n\n## What to Ignore\n\n- Nothing\n\n## Action Queue\n\n1. Check source\n", encoding="utf-8")
    candidate = root / "data/candidates/weekly_planning_2026_w41.json"
    candidate.write_text(json.dumps(payload), encoding="utf-8")
    target = approve(candidate, root, "fixture reviewer", TODAY)
    return json.loads(target.read_text(encoding="utf-8"))


def monthly_payload():
    # Upgrade the frozen June fixture with synthetic review metadata for rendering tests.
    payload = json.loads((Path(__file__).parent / "fixtures/gta_plus_monthly.json").read_text(encoding="utf-8"))
    payload["review_state"] = "confirmed"
    payload["review"] = {"reviewer": "offline fixture"}
    source = payload["membership_period"]["source_urls"][:1]
    for group in ("claimable_vehicles", "member_bonuses", "member_discounts", "freebies", "standing_perks"):
        for item in payload["monthly_benefits"][group]:
            item.update(review_state="confirmed", source_urls=source,
                        eligibility={"platform": "unknown", "edition": "unknown", "claim_scope": "unknown"})
            if group == "claimable_vehicles":
                item["claim_method"] = "vinewood_car_club"
            elif group == "freebies":
                item["claim_method"] = "unknown"
    payload["monthly_benefits"]["deposit_evidence"] = {"review_state": "confirmed", "source_urls": source}
    payload["review"]["payload_sha256"] = payload_digest(payload)
    return payload
