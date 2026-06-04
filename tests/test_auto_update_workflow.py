import unittest
from pathlib import Path


class AutoUpdateWorkflowScheduleTests(unittest.TestCase):
    def test_vehicle_price_workflow_runs_at_0800_bangkok(self):
        workflow = Path(".github/workflows/auto-update-vehicle-prices.yml").read_text(
            encoding="utf-8"
        )

        self.assertIn('# Every Thursday at 01:00 UTC / 08:00 Bangkok', workflow)
        self.assertIn('- cron: "0 1 * * 4"', workflow)

    def test_readme_documents_matching_automation_time(self):
        readme = Path("README.md").read_text(encoding="utf-8")

        self.assertIn("every Thursday at 01:00 UTC / 08:00 Bangkok", readme)
        self.assertIn("`0 8 * * 4", readme)


if __name__ == "__main__":
    unittest.main()
