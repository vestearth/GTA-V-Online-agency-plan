#!/usr/bin/env python3
"""
GTA V Online Weekly Scraper v2.6
- Refined mapping-driven regex
- Fixes "on" prefix in item names
"""

import argparse
import datetime
import json
import re
import sys
import urllib.request
from pathlib import Path

# Constants
DEFAULT_OUTPUT_DIR = Path("data")
SCHEMA_VERSION = "2.0"
MAPPING_PATH = Path("data/references/scraper_mapping.yaml")

class WeeklyScraper:
    def __init__(self, week_override=None, is_simulation=False):
        self.player_profile = self._load_player_profile()
        self.mapping = self._load_mapping()
        self.is_simulation = is_simulation
        self.dates = self._calculate_dates()
        self.week_id = week_override or self.dates["week_id"]
        self.vehicle_ref = self._load_vehicle_reference()
        
        self.data = {
            "schema_version": SCHEMA_VERSION,
            "schema_mode": "weekly_planning",
            "week": {
                "id": self.week_id,
                "label": self.dates["label"],
                "start_date": self.dates["start_date"],
                "end_date": self.dates["end_date"],
                "source": "automated_scraper" if not is_simulation else "simulation",
                "last_updated_at": datetime.datetime.utcnow().isoformat() + "Z"
            },
            "player_context": {
                "player_name": self.player_profile.get("player_name", "Unknown"),
                "platform": self.player_profile.get("platform", "PC"),
                "gta_plus": self.player_profile.get("gta_plus", True)
            },
            "weekly_content": {
                "headline": "GTA Online Weekly Update",
                "summary": "",
                "bonuses": [],
                "events": [],
                "salvage_yard_robberies": [],
                "discounts": [],
                "vehicle_opportunities": []
            },
            "scraper_metadata": {
                "ownership_checks": [],
                "price_context": {}
            }
        }

    def _load_player_profile(self):
        path = Path("data/player_profile.json")
        return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}

    def _load_mapping(self):
        mapping = {"bonus_keywords": {}, "event_types": {}, "discount_patterns": []}
        if not MAPPING_PATH.exists(): return mapping
        content = MAPPING_PATH.read_text(encoding="utf-8")
        current_section = None
        for line in content.splitlines():
            line = line.split('#')[0].strip()
            if not line: continue
            if line.endswith(':'):
                current_section = line[:-1]
                continue
            kv = re.search(r"\"(.+)\":\s*\"(.+)\"", line)
            if kv and current_section: mapping[current_section][kv.group(1)] = kv.group(2)
            li = re.search(r"-\s*\"(.+)\"", line)
            if li and current_section == "discount_patterns": mapping[current_section].append(li.group(1))
        return mapping

    def _load_vehicle_reference(self):
        ref = []
        path = Path("data/references/vehicle_prices.yaml")
        if not path.exists(): return ref
        content = path.read_text(encoding="utf-8")
        current_v = None
        for line in content.splitlines():
            nm = re.search(r"vehicle_name:\s*\"(.+)\"", line)
            if nm:
                current_v = {"name": nm.group(1), "price": None, "aliases": []}
                ref.append(current_v)
                continue
            pr = re.search(r"base_price:\s*(\d+)", line)
            if pr and current_v: current_v["price"] = int(pr.group(1))
            al = re.search(r"alias_hints:\s*\[(.+)\]", line)
            if al and current_v:
                current_v["aliases"] = [a.strip().strip('"') for a in al.group(1).split(',')]
        return ref

    def _normalize_name(self, name):
        return re.sub(r'[^a-z0-9]', '', name.lower())

    def _strip_manufacturer(self, name):
        parts = name.split()
        return " ".join(parts[1:]) if len(parts) > 1 else name

    def _find_price(self, target_name):
        target_norm = self._normalize_name(target_name)
        target_stripped_norm = self._normalize_name(self._strip_manufacturer(target_name))
        for v in self.vehicle_ref:
            if v["name"] == target_name or self._normalize_name(v["name"]) == target_norm: return v["price"]
        for v in self.vehicle_ref:
            if self._normalize_name(self._strip_manufacturer(v["name"])) == target_stripped_norm: return v["price"]
        for v in self.vehicle_ref:
            for alias in v.get("aliases", []):
                if self._normalize_name(alias) == target_norm or self._normalize_name(alias) == target_stripped_norm: return v["price"]
        return None

    def _calculate_dates(self):
        today = datetime.date.today()
        days_since_thursday = (today.weekday() - 3) % 7
        start_date = today - datetime.timedelta(days=days_since_thursday)
        end_date = start_date + datetime.timedelta(days=7)
        year, week_num, _ = start_date.isocalendar()
        return {"week_id": f"{year}-W{week_num:02d}", "start_date": start_date.isoformat(), "end_date": end_date.isoformat(), "label": f"{start_date.strftime('%B %d')} - {end_date.strftime('%B %d %Y')}"}

    def parse_content(self, text):
        if not text: return
        
        # 1. Bonuses
        for kw, mult in self.mapping["bonus_keywords"].items():
            pattern = fr"{kw}\s+GTA\$\s+(?:&|AND)\s+RP\s+(?:\**on\**|on:)\s+\**([^\*\n]+)\**"
            for activity in re.findall(pattern, text, re.IGNORECASE):
                name = activity.strip()
                if not any(b["name"] == name for b in self.data["weekly_content"]["bonuses"]):
                    self.data["weekly_content"]["bonuses"].append({"name": name, "multiplier": mult})

        # 2. Discounts
        discount_tiers = {}
        for pattern_raw in self.mapping["discount_patterns"]:
            # Handle "on [Item]" if the pattern ends with "Discount"
            is_discount_on = "Discount" in pattern_raw
            suffix = r"(?:\s+on)?\s+\**([^\*\n]+)\**"
            pattern = pattern_raw + suffix
            for pct, item in re.findall(pattern, text, re.IGNORECASE):
                pct, name = int(pct), item.strip()
                if pct not in discount_tiers: discount_tiers[pct] = []
                if name not in discount_tiers[pct]:
                    discount_tiers[pct].append(name)
                    price = self._find_price(name)
                    if price: self.data["scraper_metadata"]["price_context"][name] = price
        
        for pct, items in discount_tiers.items():
            self.data["weekly_content"]["discounts"].append({"tier_percent": pct, "items": items})

        # 3. Events
        for kw, ev_type in self.mapping["event_types"].items():
            pattern = fr"{kw}:?\s+\**([^\*\n]+)\**"
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                val = match.group(1).strip()
                if not any(e["name"] == kw for e in self.data["weekly_content"]["events"]):
                    self.data["weekly_content"]["events"].append({"name": kw, "vehicle": val, "source": ev_type})
                if ev_type in ["podium", "prize_ride"] and not any(o["vehicle_name"] == val for o in self.data["weekly_content"]["vehicle_opportunities"]):
                    self.data["weekly_content"]["vehicle_opportunities"].append({
                        "id": f"{ev_type}_{self._normalize_name(val)}", "vehicle_name": val, "opportunity_type": ev_type, "source": "ls_car_meet" if ev_type == "prize_ride" else "casino_lucky_wheel"
                    })

    def run_metadata_checks(self):
        owned = self.player_profile.get("owned_assets", {}).get("properties", [])
        missing = self.player_profile.get("owned_assets", {}).get("missing_properties", [])
        for discount in self.data["weekly_content"]["discounts"]:
            for item in discount["items"]:
                status = "owned" if item in owned else "missing_priority" if item in missing else "upgrade_available" if any(p in item for p in owned) else "unknown"
                self.data["scraper_metadata"]["ownership_checks"].append({"item": item, "status": status, "tier_percent": discount["tier_percent"]})

    def save(self, overwrite=False):
        prefix = "temp_" if self.is_simulation else ""
        filename = f"{prefix}weekly_planning_{self.week_id.replace('-', '_').lower()}.json"
        output_path = DEFAULT_OUTPUT_DIR / filename
        if output_path.exists() and not overwrite and not self.is_simulation:
            print(f"Error: {output_path} exists. Use --overwrite."); return
        with open(output_path, 'w', encoding='utf-8') as f: json.dump(self.data, f, indent=2, ensure_ascii=False)
        print(f"Saved: {output_path} (Week: {self.week_id})")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url"); parser.add_argument("--simulate", action="store_true"); parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    scraper = WeeklyScraper(is_simulation=args.simulate)
    content = None
    if args.simulate:
        content = "DOUBLE GTA$ AND RP on Nightclub Sell Missions\n40% Off Nightclub Properties\n30% Discount on Maibatsu MonstroCiti\n30% Off Galaxy Super Yacht\nLucky Wheel: **Överflöd Imorgon**"
    elif args.url:
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            req = urllib.request.Request(args.url, headers=headers)
            with urllib.request.urlopen(req) as response: content = response.read().decode('utf-8')
        except: pass
    if content:
        scraper.parse_content(content); scraper.run_metadata_checks(); scraper.save(overwrite=args.overwrite)

if __name__ == "__main__": main()
