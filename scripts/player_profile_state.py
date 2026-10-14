"""Character-scoped profile views with legacy compatibility and observation provenance."""
import argparse
import copy
import json
import re
from pathlib import Path


def normalize_profile(payload):
    profile = copy.deepcopy(payload)
    if "characters" not in profile:
        profile["characters"] = {"main": {
            "role": "legacy", "inventory_state": "legacy_recorded",
            "owned_assets": copy.deepcopy(profile.get("owned_assets", {})),
            "bankroll": copy.deepcopy(profile.get("bankroll", {})), "progress": {}, "prize_claims": []}}
        profile["active_character"] = "main"
        profile["account"] = {"bank_balance": None, "entitlements": {}, "shared_unlocks": []}
    return profile


def character_view(payload, character=None):
    profile = normalize_profile(payload)
    character = character or profile.get("active_character")
    if character not in profile["characters"]:
        raise ValueError("Select a known character before evaluating ownership/readiness")
    view = copy.deepcopy(profile)
    state = profile["characters"][character]
    view.update(selected_character=character, owned_assets=copy.deepcopy(state.get("owned_assets", {})),
                inventory_state=state.get("inventory_state", "unknown"))
    view["bankroll"] = copy.deepcopy(state.get("bankroll", {}))
    # Shared entitlement does not imply character-level claims or shared vehicles.
    view["account"] = copy.deepcopy(profile.get("account", {}))
    return view


def cosmetic_available(payload, cosmetic, character):
    profile = normalize_profile(payload)
    for unlock in profile.get("account", {}).get("shared_unlocks", []):
        if unlock.get("name") == cosmetic:
            observations = [o for o in unlock.get("observations", []) if o.get("character") == character
                            and o.get("state") == "observed_available" and o.get("source") == "user_in_game_test"]
            if observations:
                return {"state": "observed_available", "buy_duplicate_for_unlock": False,
                        "unlock_method": unlock.get("confirmed_unlock_method", "unknown"),
                        "expiry_behavior": unlock.get("expiry_behavior", "unknown")}
    return {"state": "unknown", "buy_duplicate_for_unlock": "verify_first"}


def validate_profile(payload):
    profile = normalize_profile(payload)
    issues = []
    characters = profile.get("characters", {})
    if profile.get("active_character") not in characters:
        issues.append("Unknown active_character")
    for identifier, state in characters.items():
        assets = state.get("owned_assets", {})
        owned = set(assets.get("properties", []))
        missing = set(assets.get("missing_properties", []))
        if owned & missing:
            issues.append(f"{identifier}: properties marked owned and missing: {sorted(owned & missing)}")
        note = str(assets.get("notes", ""))
        # Inspect missing/does-not-own clauses, not unrelated mentions of names.
        clauses = re.findall(r"(?:missing|does not own|not owned)\b([^.;]*)(?:[.;]|$)", note, re.I)
        for clause in clauses:
            for item in owned:
                if item.casefold() in clause.casefold() or (item.endswith("Yacht") and "yacht" in clause.casefold()) or (item.endswith("Avenger") and "avenger" in clause.casefold()):
                    issues.append(f"{identifier}: ownership note contradicts inventory: {item}")
    main = characters.get("main", {})
    if "owned_assets" in payload and payload["owned_assets"] != main.get("owned_assets"):
        issues.append("Legacy owned_assets alias differs from main character inventory")
    if "bankroll" in payload and payload["bankroll"] != main.get("bankroll"):
        issues.append("Legacy bankroll alias differs from main character bankroll")
    for unlock in profile.get("account", {}).get("shared_unlocks", []):
        for observation in unlock.get("observations", []):
            if (observation.get("character") not in characters or not observation.get("observed_at")
                    or not observation.get("platform") or not observation.get("edition")
                    or observation.get("source") != "user_in_game_test"):
                issues.append("Unlock observation lacks character/date/platform/edition/source")
    return issues


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("profile", type=Path, nargs="?", default=Path("data/player_profile.json"))
    args = parser.parse_args()
    issues = validate_profile(json.loads(args.profile.read_text(encoding="utf-8")))
    print(json.dumps({"issues": issues}, ensure_ascii=False))
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
