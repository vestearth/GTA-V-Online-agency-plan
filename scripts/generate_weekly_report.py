#!/usr/bin/env python3
"""
GTA V Online Weekly Report Generator v1.1
- Softened "MUST BUY" to "Discounted Asset Review"
- Added Profit Calculation Table for Business Bonuses
- Integrated Vehicle Prices in Discount Gallery
"""

import json
import argparse
from pathlib import Path

class ReportGenerator:
    def __init__(self, json_path):
        self.path = Path(json_path)
        with open(self.path, 'r', encoding='utf-8') as f:
            self.data = json.load(f)

    def generate_markdown(self):
        week = self.data["week"]
        content = self.data["weekly_content"]
        metadata = self.data.get("scraper_metadata", {})
        prices = metadata.get("price_context", {})
        
        md = []
        md.append(f"# 📅 GTA Online Weekly Dashboard: {week['id']}")
        md.append(f"**Period:** {week['label']}")
        md.append(f"\n---\n")

        # 1. Actionable Recommendations (Softened wording)
        md.append("## 🚀 Strategic Opportunities")
        checks = metadata.get("ownership_checks", [])
        priorities = [c for c in checks if c["status"] == "missing_priority"]
        upgrades = [c for c in checks if c["status"] == "upgrade_available"]
        
        if priorities:
            md.append("### 💎 Discounted Asset Review (Recommended for Lester's Evaluation)")
            for p in priorities:
                md.append(f"- [ ] **{p['item']}** ({p['tier_percent']}% Off) - *Missing from Portfolio*")
        if upgrades:
            md.append("### 🛠️ Optimization Opportunities")
            for u in upgrades:
                md.append(f"- [ ] **{u['item']}** ({u['tier_percent']}% Off) - *Property Owned, review upgrades*")
        
        if not priorities and not upgrades:
            md.append("- No high-impact asset deals detected for your profile this week.")
        
        md.append("\n---\n")

        # 2. Bonuses & Profit Projections
        md.append("## 💰 Active Bonuses & Profit Projections")
        md.append("| Activity | Multiplier | Estimated Payout Focus |")
        md.append("| :--- | :--- | :--- |")
        
        bonuses = content.get("bonuses", [])
        for b in bonuses:
            # Simple profit projection hint
            focus = "High Efficiency" if "2x" in b['multiplier'] or "3x" in b['multiplier'] else "Standard"
            if "Nightclub" in b['name']: focus = "🔥 **Top Priority: Passive Income**"
            elif "Heist" in b['name']: focus = "Active Grinding"
            
            md.append(f"| {b['name']} | **{b['multiplier']}** | {focus} |")
        
        md.append("\n---\n")

        # 3. Events & Opportunities
        md.append("## 🏎️ Events & Opportunities")
        for e in content.get("events", []):
            name = e.get("name", "Event")
            vehicle = e.get("vehicle", "N/A")
            md.append(f"- **{name}:** {vehicle} ({e.get('source', 'Event source')})")
        
        md.append("\n---\n")

        # 4. All Discounts (with Price Context)
        md.append("## 🛒 All Discounts")
        for d in content.get("discounts", []):
            md.append(f"### {d['tier_percent']}% Off")
            for item in d["items"]:
                price_str = ""
                if item in prices:
                    orig = prices[item]
                    discounted = int(orig * (1 - d['tier_percent']/100))
                    price_str = f" - ~~GTA$ {orig:,}~~ → **GTA$ {discounted:,}**"
                md.append(f"- {item}{price_str}")
        
        return "\n".join(md)

    def save(self):
        report_dir = Path("reports")
        report_dir.mkdir(exist_ok=True)
        filename = f"weekly_report_{self.data['week']['id'].replace('-', '_').lower()}.md"
        output_path = report_dir / filename
        
        md_content = self.generate_markdown()
        output_path.write_text(md_content, encoding="utf-8")
        print(f"Report generated: {output_path}")
        return md_content

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("json_file", help="Path to the weekly planning JSON")
    args = parser.parse_args()
    
    gen = ReportGenerator(args.json_file)
    print(gen.save())

if __name__ == "__main__":
    main()
