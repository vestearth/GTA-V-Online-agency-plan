import json
import tempfile
import textwrap
import unittest
from pathlib import Path

from scripts.generate_dashboard import (
    DashboardMarkerError,
    build_phase1_context,
    extract_markdown_section,
    find_latest_weekly_payload,
    format_currency_compact,
    load_vehicle_price_reference,
    plan_phase1_updates,
    render_current_focus,
    render_next_claim_buy,
    render_asset_overview,
    render_summary_cards,
    render_weekly_action_plan,
    render_what_to_buy_ignore,
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

        self.assertIn("Current Focus", html)
        self.assertIn("Next Claim / Buy", html)
        self.assertIn("Discounted Items Total", html)
        self.assertIn("All Cars Needed", html)
        self.assertIn(format_currency_compact(10304070), html)
        self.assertIn(format_currency_compact(26418100), html)
        self.assertIn("<!-- START: current_focus -->", html)
        self.assertIn("<!-- START: next_claim_buy -->", html)


class DashboardGeneratorPhase2RenderingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.weekly_payload = json.loads(
            Path("data/weekly_planning_2026_w22.json").read_text(encoding="utf-8")
        )
        cls.player_profile = json.loads(
            Path("data/player_profile.json").read_text(encoding="utf-8")
        )
        cls.weekly_report_text = Path("reports/weekly_master_plan_2026_w22.md").read_text(
            encoding="utf-8"
        )
        cls.event_report_text = Path("reports/event_master_plan_2026_w22.md").read_text(
            encoding="utf-8"
        )

    def test_extract_markdown_section_reads_action_queue_block(self):
        section = extract_markdown_section(
            self.weekly_report_text,
            "## Action Queue",
        )

        self.assertIsNotNone(section)
        self.assertIn("Higgins Helitours", section)
        self.assertIn("Money Fronts Money Laundering Missions 4x", section)

    def test_render_weekly_action_plan_uses_w22_action_queue(self):
        html = render_weekly_action_plan(self.weekly_report_text)

        self.assertIsNotNone(html)
        self.assertIn("Higgins Helitours", html)
        self.assertIn("Money Laundering", html)
        self.assertIn('class="steps"', html)

    def test_render_what_to_buy_ignore_builds_rulings_table(self):
        html = render_what_to_buy_ignore(
            self.weekly_report_text,
            self.event_report_text,
        )

        self.assertIsNotNone(html)
        self.assertIn("Higgins Helitours", html)
        self.assertIn("Claim", html)
        self.assertIn("Salvage Yard", html)
        self.assertIn("Do not claim", html)

    def test_render_asset_overview_uses_profile_and_week_notes(self):
        html = render_asset_overview(
            self.player_profile,
            self.weekly_payload,
            self.weekly_report_text,
        )

        self.assertIsNotNone(html)
        self.assertIn("Hands On Car Wash", html)
        self.assertIn("Owned", html)
        self.assertIn("Benefactor Terrorbyte", html)

    def test_render_weekly_action_plan_returns_none_when_parse_confidence_is_low(self):
        self.assertIsNone(render_weekly_action_plan("## Something Else\n- no action queue here"))

    def test_render_current_focus_uses_weekly_payload(self):
        html = render_current_focus(self.weekly_payload, self.weekly_report_text)

        self.assertIsNotNone(html)
        self.assertIn("Money Fronts 4x loop", html)

    def test_render_next_claim_buy_uses_first_buy_entry(self):
        html = render_next_claim_buy(self.weekly_report_text, self.event_report_text)

        self.assertIsNotNone(html)
        self.assertIn("Claim Higgins Helitours", html)


class DashboardFocusRowMarkupTests(unittest.TestCase):
    def test_dashboard_contains_summary_card_markers_for_focus_content(self):
        html = Path("dashboard.html").read_text(encoding="utf-8")

        self.assertIn('class="grid summary-grid"', html)
        self.assertNotIn('class="grid focus-row"', html)
        self.assertIn("<!-- START: current_focus -->", html)
        self.assertIn("<!-- END: current_focus -->", html)
        self.assertIn("<!-- START: next_claim_buy -->", html)
        self.assertIn("<!-- END: next_claim_buy -->", html)


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
