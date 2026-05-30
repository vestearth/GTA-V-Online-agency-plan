import json
import tempfile
import textwrap
import unittest
from pathlib import Path

from scripts.generate_dashboard import (
    DashboardMarkerError,
    build_phase1_context,
    find_latest_weekly_payload,
    format_currency_compact,
    load_vehicle_price_reference,
    plan_phase1_updates,
    render_summary_cards,
    validate_required_markers,
)


class DashboardGeneratorSelectionTests(unittest.TestCase):
    def test_find_latest_weekly_payload_prefers_highest_year_week(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            data_dir = Path(tmpdir)
            for name in (
                "weekly_planning_2026_w09.json",
                "weekly_planning_2026_w22.json",
                "weekly_planning_2025_w52.json",
            ):
                (data_dir / name).write_text("{}", encoding="utf-8")

            latest = find_latest_weekly_payload(data_dir)

            self.assertEqual(latest.name, "weekly_planning_2026_w22.json")

    def test_validate_required_markers_raises_when_phase1_marker_missing(self):
        html = textwrap.dedent(
            """\
            <!-- START: header_meta -->
            ok
            <!-- END: header_meta -->
            """
        )

        with self.assertRaises(DashboardMarkerError):
            validate_required_markers(
                html,
                required_markers=["header_meta", "summary_cards"],
            )


class DashboardGeneratorRenderingTests(unittest.TestCase):
    def test_phase1_context_builds_expected_w22_totals(self):
        weekly_payload = json.loads(
            Path("data/weekly_planning_2026_w22.json").read_text(encoding="utf-8")
        )
        player_profile = json.loads(Path("data/player_profile.json").read_text(encoding="utf-8"))
        vehicle_prices = load_vehicle_price_reference(Path("data/references/vehicle_prices.yaml"))

        context = build_phase1_context(
            weekly_payload=weekly_payload,
            player_profile=player_profile,
            vehicle_prices=vehicle_prices,
        )

        self.assertEqual(context["owned_major_assets"], 21)
        self.assertEqual(context["missing_major_assets"], 0)
        self.assertEqual(context["discounted_items_total"], 10304070)
        self.assertEqual(context["all_cars_needed_total"], 26418100)
        self.assertEqual(context["unresolved_discount_items"], [])
        self.assertEqual(context["unresolved_vehicle_prices"], [])

    def test_render_summary_cards_uses_phase1_labels(self):
        html = render_summary_cards(
            {
                "owned_major_assets": 21,
                "missing_major_assets": 0,
                "discounted_items_total": 10304070,
                "all_cars_needed_total": 26418100,
                "unresolved_vehicle_prices": [],
                "unresolved_discount_items": [],
            }
        )

        self.assertIn("Owned Major Assets", html)
        self.assertIn("Missing Major Assets", html)
        self.assertIn("Discounted Items Total", html)
        self.assertIn("All Cars Needed", html)
        self.assertIn(format_currency_compact(10304070), html)
        self.assertIn(format_currency_compact(26418100), html)


class DashboardGeneratorDryRunTests(unittest.TestCase):
    def test_plan_phase1_updates_reports_marker_names_without_writing(self):
        plan = plan_phase1_updates(
            available_markers=[
                "header_meta",
                "summary_cards",
                "weekly_deals",
                "weekly_vehicle_spotlight",
                "data_status_note",
            ]
        )

        self.assertEqual(
            plan,
            [
                "header_meta",
                "summary_cards",
                "weekly_deals",
                "weekly_vehicle_spotlight",
                "data_status_note",
            ],
        )


if __name__ == "__main__":
    unittest.main()
