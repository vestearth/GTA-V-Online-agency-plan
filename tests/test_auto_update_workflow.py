import unittest
import json
import tempfile
from pathlib import Path
from unittest import mock

from scripts import run_weekly_content_refresh as refresh


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


class WeeklyContentRefreshDashboardTests(unittest.TestCase):
    def _run_refresh_with_fake_workspace(self, *, create_master_plan: bool) -> tuple[int, list[list[str]]]:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "data").mkdir()
            (root / "reports").mkdir()
            week_id = "2026-W25"
            weekly_path = root / "data" / "weekly_planning_2026_w25.json"
            master_path = root / "reports" / "weekly_master_plan_2026_w25.md"
            commands: list[list[str]] = []

            def fake_run_step(command: list[str], *, allow_failure: bool = False) -> int:
                commands.append(command)
                if command[:2] == ["python3", "scripts/scrape_weekly_update.py"]:
                    weekly_path.write_text(
                        json.dumps(
                            {
                                "weekly_content": {
                                    "bonuses": [{"name": "Casino Heist", "multiplier": "2x"}]
                                }
                            }
                        ),
                        encoding="utf-8",
                    )
                if (
                    create_master_plan
                    and command[:2] == ["python3", "scripts/generate_weekly_report.py"]
                ):
                    master_path.write_text("# Weekly Master Plan - 2026-W25\n", encoding="utf-8")
                return 0

            with (
                mock.patch.object(refresh, "ROOT", root),
                mock.patch.object(refresh, "current_week_id", return_value=week_id),
                mock.patch.object(refresh, "resolve_weekly_update_url", return_value="https://example.test/news"),
                mock.patch.object(refresh, "run_step", side_effect=fake_run_step),
            ):
                result = refresh.main([])

            return result, commands

    def _normalized_commands(self, commands: list[list[str]]) -> list[list[str]]:
        return [[part.replace("\\", "/") for part in command] for command in commands]

    def test_weekly_refresh_fails_when_master_plan_is_missing(self):
        result, commands = self._run_refresh_with_fake_workspace(create_master_plan=False)
        normalized_commands = self._normalized_commands(commands)

        self.assertEqual(1, result)
        self.assertNotIn(
            ["python3", "scripts/generate_pixel_dashboard.py", "--weekly", "data/weekly_planning_2026_w25.json"],
            normalized_commands,
        )

    def test_weekly_refresh_updates_both_dashboards_when_master_plan_exists(self):
        result, commands = self._run_refresh_with_fake_workspace(create_master_plan=True)
        normalized_commands = self._normalized_commands(commands)

        self.assertEqual(0, result)
        self.assertIn(
            ["python3", "scripts/generate_dashboard.py", "--weekly", "data/weekly_planning_2026_w25.json"],
            normalized_commands,
        )
        self.assertIn(
            ["python3", "scripts/generate_pixel_dashboard.py", "--weekly", "data/weekly_planning_2026_w25.json"],
            normalized_commands,
        )

    def test_weekly_refresh_workflow_has_no_pixel_dashboard_skip_input(self):
        workflow = Path(".github/workflows/weekly-content-refresh.yml").read_text(encoding="utf-8")

        self.assertNotIn("skip_pixel_dashboard", workflow)

    def test_weekly_refresh_workflow_commits_standard_master_plan_reports(self):
        workflow = Path(".github/workflows/weekly-content-refresh.yml").read_text(encoding="utf-8")

        self.assertIn("reports/weekly_master_plan_*.md", workflow)
        self.assertIn("reports/event_master_plan_*.md", workflow)
        self.assertIn("git add -f", workflow)


if __name__ == "__main__":
    unittest.main()
