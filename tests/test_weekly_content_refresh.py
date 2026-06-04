import unittest
from pathlib import Path

from scripts.resolve_weekly_update_source import discover_latest_gta_online_article
from scripts.run_weekly_content_refresh import validate_weekly_payload_has_content


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


if __name__ == "__main__":
    unittest.main()
