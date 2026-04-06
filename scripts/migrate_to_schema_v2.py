#!/usr/bin/env python3
"""Migrate legacy weekly JSON into schema v2."""

from __future__ import annotations

import argparse
import re
from datetime import date
from pathlib import Path

from schema_v2_runtime import DEFAULT_WEEKLY, dump_json, load_json


MONTHS = {
    "january": 1,
    "february": 2,
    "march": 3,
    "april": 4,
    "may": 5,
    "june": 6,
    "july": 7,
    "august": 8,
    "september": 9,
    "october": 10,
    "november": 11,
    "december": 12,
}

MULT_RE = re.compile(r"(\d+)\s*[xX]")


def slugify(value):
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")


def parse_date_range(label):
    match = re.search(r"([A-Za-z]+)\s+(\d+)-(\d+),\s*(\d{4})", label or "")
    if not match:
        return None, None, None
    month_name, start_day, end_day, year = match.groups()
    month = MONTHS.get(month_name.lower())
    if not month:
        return None, None, None
    start_dt = date(int(year), month, int(start_day))
    end_dt = date(int(year), month, int(end_day))
    week_id = f"{start_dt.isocalendar().year}-W{start_dt.isocalendar().week:02d}"
    return week_id, start_dt.isoformat(), end_dt.isoformat()


def parse_bonus(notes):
    if not notes:
        return {}
    matches = MULT_RE.findall(notes)
    if not matches:
        return {}
    bonus = {}
    numbers = [int(item) for item in matches]
    if "gta+" in notes.lower() and len(numbers) >= 2:
        bonus["gta_cash_multiplier"] = numbers[0]
        bonus["rp_multiplier"] = numbers[0]
        bonus["gta_plus_cash_multiplier"] = numbers[1]
    elif "gta+" in notes.lower() and len(numbers) == 1:
        bonus["gta_plus_cash_multiplier"] = numbers[0]
    else:
        bonus["gta_cash_multiplier"] = numbers[0]
        if "rp" in notes.lower():
            bonus["rp_multiplier"] = numbers[0]
    return bonus


def build_featured_activity(entry, week_start, week_end):
    name = entry.get("name", "Unknown Activity")
    notes = entry.get("notes")
    lowered = name.lower()
    category = entry.get("category", "weekly_challenge").lower()
    derived_category = "weekly_challenge"
    if "bonus" in category or "bonus" in lowered:
        derived_category = "mission_bonus"
    elif "race" in category:
        derived_category = "race"
    elif "new vehicle" in category:
        derived_category = "new_release"
    content_type = "repeatable" if derived_category in {"mission_bonus", "race"} else "one_time"
    activity_id = slugify(name.replace("Bonus Activity:", "").strip())
    requirements = []
    if "dispatch work" in lowered:
        requirements = ["agency"]
    party_size = "solo"
    if "vespucci" in lowered or "community race" in lowered:
        party_size = "small_group"
    elif "dispatch" in lowered:
        party_size = "solo_or_duo"
    value_tags = []
    if "gta$" in (notes or "").lower() or derived_category == "mission_bonus":
        value_tags.append("money")
    if "rp" in (notes or "").lower():
        value_tags.append("rp")
    if "vespucci" in lowered or "community race" in lowered:
        value_tags.append("crew_fun")
    if "new" in lowered:
        value_tags.append("new_content")
    timebox = None
    if "dispatch" in lowered:
        timebox = 20
    elif "firefighter" in lowered:
        timebox = 10
    elif "wildlife" in lowered:
        timebox = 15
    return {
        "id": activity_id,
        "name": name.replace("Bonus Activity: ", ""),
        "category": derived_category,
        "content_type": content_type,
        "availability": {"start": week_start, "end": week_end},
        "bonus": parse_bonus(notes),
        "requirements": requirements,
        "recommended_party_size": party_size,
        "timebox_minutes": timebox,
        "value_tags": value_tags,
        "notes": notes,
    }


def build_vehicle_from_activity(entry, week_start, week_end):
    name = entry.get("name", "")
    notes = entry.get("notes", "")
    lowered = name.lower()
    label = name.split(":", 1)[1].strip() if ":" in name else name
    opportunity_type = "new_release"
    if "podium vehicle" in lowered:
        opportunity_type = "podium"
    elif "premium test ride" in lowered:
        opportunity_type = "premium_test_ride"
    elif "test ride" in lowered:
        opportunity_type = "test_ride"
    elif "prize ride challenge" in lowered:
        opportunity_type = "prize_ride"
        prize_vehicle = re.search(r"Prize Ride Vehicle:\s*(.+)", notes)
        if prize_vehicle:
            label = prize_vehicle.group(1).strip()
    source = "unknown"
    if "podium" in lowered:
        source = "casino"
    elif "ls car meet" in lowered or "test ride" in lowered or "prize ride" in lowered:
        source = "ls_car_meet"
    elif "new vehicle" in lowered:
        source = "warstock"
    return {
        "id": slugify(f"{label}_{opportunity_type}"),
        "vehicle_name": label,
        "opportunity_type": opportunity_type,
        "source": source,
        "availability": {"start": week_start, "end": week_end},
        "discount_percent": None,
        "price": None,
        "trade_price": None,
        "class": None,
        "limited": opportunity_type in {"podium", "prize_ride", "test_ride", "premium_test_ride", "new_release"},
        "removed_vehicle": "removed vehicle" in notes.lower(),
        "gta_plus_only": "gta+" in notes.lower() and "free" in notes.lower(),
        "acquisition": {
            "challenge": name.split(":", 1)[1].strip() if opportunity_type == "prize_ride" and ":" in name else None,
            "claim_path": None if opportunity_type == "prize_ride" else notes,
        },
        "evaluation_inputs": {
            "performance_score": None,
            "utility_tags": [],
            "weaponized": False,
            "service_vehicle": "police" in label.lower() or "cruiser" in label.lower(),
        },
    }


def build_race_or_trial(entry):
    name = entry.get("name", "")
    notes = entry.get("notes")
    restrictions = []
    if "motorcycle" in (notes or "").lower():
        restrictions.append("motorcycle")
    if name.lower().startswith("hsw"):
        restrictions.append("HSW_eligible")
    return {
        "id": slugify(name),
        "name": name,
        "type": "premium_race" if "premium race" in name.lower() else "time_trial",
        "vehicle_restrictions": restrictions,
        "recommended_vehicle_classes": restrictions or [],
        "reward": {"cash": None},
        "notes": notes,
    }


def build_discount_vehicle(name, discount_percent, availability_end, source_hint):
    service = any(token in name.lower() for token in ("police", "cruiser", "interceptor", "park ranger", "pursuit"))
    return {
        "id": slugify(f"{name}_discount"),
        "vehicle_name": name,
        "opportunity_type": "discount",
        "source": source_hint,
        "availability": {"start": None, "end": availability_end},
        "discount_percent": discount_percent,
        "price": None,
        "trade_price": None,
        "class": None,
        "limited": False,
        "removed_vehicle": False,
        "gta_plus_only": False,
        "acquisition": {"claim_path": "Purchase from weekly discount market"},
        "evaluation_inputs": {
            "performance_score": None,
            "utility_tags": ["service"] if service else [],
            "weaponized": "tank" in name.lower(),
            "service_vehicle": service,
        },
    }


def merge_franklin_supplement(vehicle_opportunities, supplement):
    lookup = {item["vehicle_name"].lower(): item for item in vehicle_opportunities}
    for entry in supplement.get("discount", []):
        name = entry.get("name", "")
        existing = lookup.get(name.lower())
        if not existing:
            existing = {
                "id": slugify(f"{name}_discount"),
                "vehicle_name": name,
                "opportunity_type": "discount",
                "source": "unknown",
                "availability": {"start": None, "end": None},
                "discount_percent": None,
                "price": None,
                "trade_price": None,
                "class": None,
                "limited": False,
                "removed_vehicle": False,
                "gta_plus_only": False,
                "acquisition": {"claim_path": "Purchase path unknown in legacy data"},
                "evaluation_inputs": {},
            }
            vehicle_opportunities.append(existing)
            lookup[name.lower()] = existing
        existing["price"] = entry.get("price")
        existing.setdefault("evaluation_inputs", {})
        existing["evaluation_inputs"]["performance_score"] = entry.get("performance_score")
        existing["evaluation_inputs"]["upgrade_cost"] = entry.get("upgrade_cost")
        existing["evaluation_inputs"]["rarity"] = entry.get("rarity")
        test_metrics = supplement.get("test_rides", {}).get(entry.get("sku"), {})
        if test_metrics:
            existing["evaluation_inputs"]["test_metrics"] = test_metrics

    prize_conditions = supplement.get("prize_ride_conditions")
    if prize_conditions:
        for item in vehicle_opportunities:
            if item.get("opportunity_type") == "prize_ride":
                item.setdefault("acquisition", {})
                item["acquisition"]["qualification_rules"] = prize_conditions


def build_schema_v2(legacy, supplement=None):
    date_label = legacy.get("date_range") or legacy.get("week")
    week_id, start_date, end_date = parse_date_range(date_label)
    weekly_content = {
        "featured_activities": [],
        "vehicle_opportunities": [],
        "weapon_and_gear_opportunities": [],
        "business_opportunities": [],
        "time_trials_and_races": [],
        "salvage_yard_targets": [],
    }

    for entry in legacy.get("activities", []):
        name = entry.get("name", "")
        lowered = name.lower()
        if any(token in lowered for token in ("podium vehicle", "prize ride", "test ride", "new vehicle")):
            weekly_content["vehicle_opportunities"].append(build_vehicle_from_activity(entry, start_date, end_date))
        elif "time trial" in lowered or "premium race" in lowered:
            weekly_content["time_trials_and_races"].append(build_race_or_trial(entry))
        else:
            weekly_content["featured_activities"].append(build_featured_activity(entry, start_date, end_date))

    discounts = legacy.get("discounts", {})
    law_block = discounts.get("law_enforcement_vehicle_discounts", {})
    general_block = discounts.get("general_vehicle_discounts", {})
    for vehicle_name in law_block.get("vehicles", []):
        weekly_content["vehicle_opportunities"].append(
            build_discount_vehicle(vehicle_name, 35, law_block.get("available_until"), "warstock")
        )
    for vehicle_name in general_block.get("vehicles", []):
        weekly_content["vehicle_opportunities"].append(
            build_discount_vehicle(vehicle_name, 30, end_date, "unknown")
        )

    gun_van_discounts = legacy.get("gun_van_discounts", {})
    for item in gun_van_discounts.get("free", []):
        weekly_content["weapon_and_gear_opportunities"].append(
            {
                "id": slugify(f"{item}_free"),
                "name": item,
                "opportunity_type": "gun_van_free",
                "discount_percent": 100,
                "gta_plus_only": False,
                "combat_role_tags": [],
                "urgency": "must_claim",
                "notes": "Migrated from legacy gun van free list",
            }
        )
    for item in gun_van_discounts.get("free_for_gta_plus_members", []):
        weekly_content["weapon_and_gear_opportunities"].append(
            {
                "id": slugify(f"{item}_free_plus"),
                "name": item,
                "opportunity_type": "gun_van_free",
                "discount_percent": 100,
                "gta_plus_only": True,
                "combat_role_tags": [],
                "urgency": "must_claim",
                "notes": "Migrated from legacy GTA+ gun van free list",
            }
        )
    for entry in gun_van_discounts.get("discounts", []):
        text = entry.get("discount", "")
        number = MULT_RE.search(text.replace("%", "X"))
        discount_percent = int(number.group(1)) if number else None
        weekly_content["weapon_and_gear_opportunities"].append(
            {
                "id": slugify(f"{entry.get('item')}_discount"),
                "name": entry.get("item"),
                "opportunity_type": "gun_van_discount",
                "discount_percent": discount_percent,
                "gta_plus_only": "gta+" in text.lower(),
                "combat_role_tags": [],
                "urgency": "good_pick",
                "notes": text,
            }
        )

    for item in legacy.get("gun_van", {}).get("stock", []):
        if item.get("item") in gun_van_discounts.get("free", []):
            continue
        weekly_content["weapon_and_gear_opportunities"].append(
            {
                "id": slugify(f"{item.get('item')}_stock"),
                "name": item.get("item"),
                "opportunity_type": "gun_van_discount",
                "discount_percent": int(item.get("discount", "0").replace("%", "")) if "%" in item.get("discount", "") else None,
                "gta_plus_only": False,
                "combat_role_tags": [],
                "urgency": "optional",
                "notes": f"Gun Van stock; GTA+ {item.get('gta_plus_discount')}",
            }
        )

    for entry in legacy.get("salvage_yard_robberies", []):
        weekly_content["salvage_yard_targets"].append(
            {
                "id": slugify(f"{entry.get('robbery')}_{entry.get('vehicle')}"),
                "robbery_name": entry.get("robbery"),
                "vehicle_name": entry.get("vehicle"),
                "claimable": True,
                "salvage_value": None,
                "sell_value": None,
                "notes": "Migrated from legacy Salvage Yard weekly list",
            }
        )

    weekly_content["business_opportunities"].append(
        {
            "id": "dispatch_work_agency_bonus",
            "name": "Agency Dispatch Work Bonus",
            "business_type": "agency",
            "bonus": {"gta_cash_multiplier": 2, "gta_plus_cash_multiplier": 3, "rp_multiplier": 2},
            "requires_owned_business": True,
            "requirements": ["agency"],
            "estimated_value_tags": ["active_grind", "money", "limited_reward"],
            "notes": "Derived from Dispatch Work bonus activity",
        }
    )
    if weekly_content["salvage_yard_targets"]:
        weekly_content["business_opportunities"].append(
            {
                "id": "salvage_yard_weekly_targets",
                "name": "Salvage Yard Weekly Targets",
                "business_type": "salvage_yard",
                "bonus": {},
                "requires_owned_business": True,
                "requirements": ["salvage_yard"],
                "estimated_value_tags": ["active_grind", "vehicle_collecting"],
                "notes": "Derived from Salvage Yard robbery list",
            }
        )

    if supplement:
        merge_franklin_supplement(weekly_content["vehicle_opportunities"], supplement)

    player_name = legacy.get("player")
    crew_name = legacy.get("crew")
    player_known = player_name not in {None, "", "Unknown"}
    crew_known = crew_name not in {None, "", "Unknown"}

    return {
        "schema_version": "2.0",
        "schema_mode": "weekly_planning",
        "week": {
            "id": week_id,
            "label": legacy.get("week"),
            "start_date": start_date,
            "end_date": end_date,
            "source": "mixed",
            "last_updated_at": None,
        },
        "player_context": {
            "player_name": player_name if player_known else None,
            "platform": "unknown",
            "gta_plus": bool(legacy.get("gta_plus_exclusive")),
            "rank": None,
            "cash_on_hand": None,
            "bank_balance": None,
            "play_style_tags": [],
            "goals_this_week": ["make_money", "unlock_vehicle"],
            "owned_assets": {
                "properties": [],
                "businesses": [],
                "key_vehicles": [],
                "key_weapons": [],
            },
            "constraints": {
                "hours_available": legacy.get("playtime_hours"),
                "preferred_session_size": "any",
                "avoid_content_tags": [],
            },
        },
        "planning_context": {
            "primary_objective": "mixed",
            "budget_limit": None,
            "risk_tolerance": "medium",
            "session_plan": [],
            "decision_policy": {
                "recommend_owned_only": False,
                "allow_new_purchases": True,
                "prioritize_limited_time_content": True,
            },
        },
        "weekly_content": weekly_content,
        "business_state": {
            "nightclub": {
                "owned": False,
                "safe_cash": None,
                "popularity_percent": None,
                "technicians_total": None,
                "technician_assignments": [],
                "goods_stock": [],
                "upgrade_flags": [],
            },
            "feeder_businesses": [],
        },
        "crew_context": {
            "crew_name": crew_name if crew_known else None,
            "active_members": [],
            "usual_party_size": "solo",
            "coordination_level": "low",
            "notes": None,
        },
        "analysis_hints": {
            "missing_data_policy": "state_unknown_explicitly",
            "recommendation_style": "ranked_list",
            "language": "th",
            "max_recommendations": 5,
            "must_cite_ids": True,
        },
        "data_quality": {
            "coverage": {
                "player_context_complete": False,
                "business_state_complete": False,
                "crew_context_complete": False,
            },
            "known_gaps": [
                "Legacy payload does not describe owned assets or business readiness.",
                "Legacy payload mixes event catalog and post-play fields.",
                "Some vehicle and payout values were unavailable during migration.",
            ],
            "confidence_level": "medium",
        },
    }


def main():
    parser = argparse.ArgumentParser(description="Migrate legacy weekly JSON into schema v2.")
    parser.add_argument("--input", required=True, help="Path to legacy weekly JSON")
    parser.add_argument("--output", default=str(DEFAULT_WEEKLY), help="Destination path for schema v2 JSON")
    parser.add_argument("--franklin-supplement", help="Optional path to sample Franklin vehicle JSON")
    args = parser.parse_args()

    legacy = load_json(Path(args.input))
    supplement = load_json(Path(args.franklin_supplement)) if args.franklin_supplement else None
    migrated = build_schema_v2(legacy, supplement=supplement)
    dump_json(Path(args.output), migrated)
    print(f"Migrated legacy payload to {args.output}")


if __name__ == "__main__":
    main()
