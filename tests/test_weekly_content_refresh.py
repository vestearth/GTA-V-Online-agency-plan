import unittest
from pathlib import Path

from scripts.resolve_weekly_update_source import discover_latest_gta_online_article
from scripts.run_weekly_content_refresh import validate_weekly_payload_has_content
from scripts.generate_pixel_dashboard import render_pixel_command_brief


class WeeklyUpdateSourceResolverTests(unittest.TestCase):
    def test_discovers_latest_gta_online_article_from_newswire_markup(self):
        html = """
        <a href="/newswire/article/abc123/gta-online-weekly-bonuses">
          <span>GTA Online</span>
          <span>Launder Your Bottom Line with Money Fronts Bonuses</span>
        </a>
        <a href="/newswire/article/old999/red-dead-online-monthly">
          <span>Red Dead Online</span>
        </a>
        """

        resolved = discover_latest_gta_online_article(html)

        self.assertEqual(
            resolved,
            "https://www.rockstargames.com/newswire/article/abc123/gta-online-weekly-bonuses",
        )

    def test_ignores_gta_plus_member_articles_when_general_article_exists(self):
        html = """
        <a href="/newswire/article/gta-plus/claim-a-free-car-with-gta-plus">
          <span>GTA Online</span>
          <span>Claim a Free Car with GTA+</span>
        </a>
        <a href="/newswire/article/general/boost-nightclub-popularity">
          <span>GTA Online</span>
          <span>Boost Your Nightclub Popularity and Bring in Doubled Daily Income</span>
        </a>
        """

        resolved = discover_latest_gta_online_article(html)

        self.assertEqual(
            resolved,
            "https://www.rockstargames.com/newswire/article/general/boost-nightclub-popularity",
        )


class WeeklyContentRefreshWorkflowTests(unittest.TestCase):
    def test_workflow_runs_full_refresh_pipeline_at_0800_bangkok(self):
        workflow = Path(".github/workflows/weekly-content-refresh.yml").read_text(
            encoding="utf-8"
        )

        self.assertIn("name: Weekly Content Refresh", workflow)
        self.assertIn('- cron: "0 1 * * 4"', workflow)
        self.assertIn("WEEKLY_UPDATE_URL", workflow)
        self.assertIn("python3 scripts/run_weekly_content_refresh.py", workflow)
        self.assertIn("data/weekly_planning_*.json", workflow)
        self.assertIn("reports/weekly_report_*.md", workflow)
        self.assertIn("dashboard.html", workflow)

    def test_readme_documents_full_refresh_scope_and_source_url(self):
        readme = Path("README.md").read_text(encoding="utf-8")

        self.assertIn("Weekly Content Refresh", readme)
        self.assertIn("WEEKLY_UPDATE_URL", readme)
        self.assertIn("scrape weekly payload", readme)


class WeeklyContentRefreshValidationTests(unittest.TestCase):
    def test_rejects_empty_weekly_payload_before_downstream_generation(self):
        payload = {
            "weekly_content": {
                "bonuses": [],
                "events": [],
                "discounts": [],
                "vehicle_opportunities": [],
                "salvage_yard_robberies": [],
            }
        }

        with self.assertRaises(ValueError):
            validate_weekly_payload_has_content(payload)

    def test_accepts_weekly_payload_with_detected_content(self):
        payload = {
            "weekly_content": {
                "bonuses": [{"name": "Nightclub Sell Missions", "multiplier": "2x"}],
                "events": [],
                "discounts": [],
                "vehicle_opportunities": [],
                "salvage_yard_robberies": [],
            }
        }

        validate_weekly_payload_has_content(payload)


class WeeklyPixelDashboardCopyTests(unittest.TestCase):
    def test_command_brief_uses_current_week_context_for_why_cell(self):
        weekly_payload = {
            "weekly_content": {
                "headline": "Community Mission Series and Meth Sales Week",
                "summary": "New Community Mission Series content with 4x GTA$ and RP, 2x Meth Sell Missions, and 2x Street Dealers.",
                "bonuses": [
                    {"name": "Community Mission Series", "multiplier": "4x"},
                    {"name": "Meth Sell Missions", "multiplier": "2x"},
                ],
            }
        }
        weekly_report_text = """
## What to Play

1. **Community Mission Series 4x GTA$ & RP** - Conditional active objective for PC Enhanced
2. **Meth Sell Missions 2x GTA$ & RP** - Core business loop

## What to Buy

1. **Meth Lab Upgrades** - Check if missing before buying vehicles
"""

        html = render_pixel_command_brief(weekly_payload, weekly_report_text)

        self.assertIn("Community Missions Set The Weekly Bonus", html)
        self.assertNotIn("Money Fronts Sets The Weekly Cashflow", html)


if __name__ == "__main__":
    unittest.main()
