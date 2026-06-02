import json
import tempfile
import textwrap
import unittest
from pathlib import Path

from scripts.generate_dashboard import (
    DashboardMarkerError,
    build_phase1_context,
    counts_toward_all_cars_needed,
    extract_markdown_section,
    find_latest_weekly_payload,
    format_currency_compact,
    load_vehicle_price_reference,
    plan_phase1_updates,
    render_current_focus,
    render_next_claim_buy,
    render_asset_overview,
    render_summary_cards,
    render_weekly_deals,
    render_weekly_action_plan,
    render_what_to_buy_ignore,
    validate_required_markers,
)
from scripts.generate_pixel_dashboard import (
    PIXEL_MARKERS,
    build_pixel_replacements,
    render_pixel_action_queue,
    render_pixel_buy_ledger,
    render_pixel_command_brief,
    render_pixel_field_intel,
    render_pixel_header_meta,
    render_pixel_operations_wall,
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
        self.assertEqual(context["all_cars_needed_total"], 23278100)
        self.assertEqual(context["unresolved_discount_items"], [])
        self.assertEqual(context["unresolved_vehicle_prices"], [])

    def test_reward_vehicle_surfaces_do_not_count_toward_all_cars_needed(self):
        weekly_payload = json.loads(
            Path("data/weekly_planning_2026_w22.json").read_text(encoding="utf-8")
        )
        opportunities = weekly_payload["weekly_content"]["vehicle_opportunities"]

        reward_flags = {
            item["vehicle_name"]: counts_toward_all_cars_needed(item)
            for item in opportunities
            if item["vehicle_name"] in {"Lampadati Komoda", "Truffade Nero", "Annis Hardy"}
        }

        self.assertEqual(
            reward_flags,
            {
                "Lampadati Komoda": False,
                "Truffade Nero": False,
                "Annis Hardy": True,
            },
        )

    def test_render_summary_cards_uses_phase1_labels(self):
        html = render_summary_cards(
            {
                "owned_major_assets": 21,
                "missing_major_assets": 0,
                "discounted_items_total": 10304070,
                "all_cars_needed_total": 23278100,
                "unresolved_vehicle_prices": [],
                "unresolved_discount_items": [],
            }
        )

        self.assertIn("Current Focus", html)
        self.assertIn("Next Claim / Buy", html)
        self.assertIn("Discounted Items Total", html)
        self.assertIn("All Cars Needed", html)
        self.assertIn(format_currency_compact(10304070), html)
        self.assertIn(format_currency_compact(23278100), html)
        self.assertIn("<!-- START: current_focus -->", html)
        self.assertIn("<!-- START: next_claim_buy -->", html)
        self.assertIn("Prize Ride and Lucky Wheel rewards stay linked in the spotlight but are excluded.", html)

    def test_render_weekly_deals_collapses_long_gun_van_groups(self):
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

        html = render_weekly_deals(context, vehicle_prices)

        self.assertIn('class="deal-expandable"', html)
        self.assertIn("Show 10 more", html)
        self.assertIn("Show less", html)
        self.assertIn("Gun Van 10%", html)
        self.assertNotIn("Gun Van 50%</h3>\n    <details", html)


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


class DashboardCrossLinkMarkupTests(unittest.TestCase):
    def test_dashboard_links_to_pixel_view_and_shows_automation_note(self):
        html = Path("dashboard.html").read_text(encoding="utf-8")

        self.assertIn('href="pixel-dashboard.html#ops"', html)
        self.assertIn("Operations Center", html)
        self.assertIn("Auto update", html)
        self.assertIn("Thursday", html)
        self.assertIn("08:00", html)
        self.assertIn("Bangkok", html)


class PixelDashboardOperationsMarkupTests(unittest.TestCase):
    def test_pixel_dashboard_contains_generator_markers(self):
        html = Path("pixel-dashboard.html").read_text(encoding="utf-8")

        for marker in PIXEL_MARKERS:
            self.assertIn(f"<!-- START: {marker} -->", html)
            self.assertIn(f"<!-- END: {marker} -->", html)

    def test_pixel_dashboard_contains_operations_center_sections(self):
        html = Path("pixel-dashboard.html").read_text(encoding="utf-8")

        self.assertIn("WEEKLY COMMAND BRIEF", html)
        self.assertIn("ACTION QUEUE", html)
        self.assertIn("OPERATIONS WALL", html)
        self.assertIn("FIELD INTEL", html)
        self.assertIn("BUY / IGNORE LEDGER", html)
        self.assertIn("IGNORE THIS WEEK", html)

    def test_pixel_dashboard_uses_command_brief_and_timed_queue_rows(self):
        html = Path("pixel-dashboard.html").read_text(encoding="utf-8")

        self.assertIn("HAPPENED", html)
        self.assertIn("TO DO", html)
        self.assertIn("BUY", html)
        self.assertIn("WHY", html)
        self.assertIn("[4x]", html)
        self.assertIn("[30% OFF]", html)
        self.assertIn("[20m]", html)
        self.assertIn("Run Money Laundering Missions", html)

    def test_pixel_dashboard_uses_wall_intel_and_ledger_shapes(self):
        html = Path("pixel-dashboard.html").read_text(encoding="utf-8")

        self.assertIn("Money Fronts Money Laundering Missions", html)
        self.assertIn("[ACTIVE]", html)
        self.assertIn("Salvage Yard robberies", html)
        self.assertIn("[BONUS]", html)
        self.assertIn("Lamar Contact Missions", html)
        self.assertIn("[BUY]", html)
        self.assertIn("Benefactor Terrorbyte", html)

    def test_pixel_dashboard_presents_operations_center_not_prototype(self):
        html = Path("pixel-dashboard.html").read_text(encoding="utf-8")

        self.assertIn("GTA Weekly Operations Center", html)
        self.assertIn("Strategy Snapshot", html)
        self.assertNotIn("ops room prototype", html)
        self.assertNotIn("-CarlosZ-", html)

    def test_pixel_dashboard_uses_clear_ledger_decisions(self):
        html = Path("pixel-dashboard.html").read_text(encoding="utf-8")

        self.assertIn("[BUY]", html)
        self.assertIn("[HOLD]", html)
        self.assertIn("[IGNORE]", html)
        self.assertNotIn("[CHECK]", html)


class PixelDashboardGeneratorRenderingTests(unittest.TestCase):
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
        cls.vehicle_prices = load_vehicle_price_reference(Path("data/references/vehicle_prices.yaml"))
        cls.context = build_phase1_context(
            weekly_payload=cls.weekly_payload,
            player_profile=cls.player_profile,
            vehicle_prices=cls.vehicle_prices,
        )

    def test_render_pixel_header_meta_uses_current_week(self):
        html = render_pixel_header_meta(self.context)

        self.assertIn("Strategy Snapshot", html)
        self.assertIn("2026-W22", html)
        self.assertIn("READY TO RUN", html)
        self.assertIn("Thursday 08:00 Bangkok", html)

    def test_render_pixel_command_brief_uses_current_week_focus(self):
        html = render_pixel_command_brief(self.weekly_payload, self.weekly_report_text)

        self.assertIn("Money Fronts Special", html)
        self.assertIn("Run Money Laundering Missions", html)
        self.assertIn("Benefactor Terrorbyte", html)
        self.assertIn("[4x]", html)
        self.assertIn("[30% OFF]", html)
        self.assertNotIn("Nightclub Sales Lead The Week", html)

    def test_render_pixel_action_queue_uses_report_steps_and_time_chips(self):
        html = render_pixel_action_queue(self.weekly_payload, self.weekly_report_text)

        self.assertIn("Claim Higgins Helitours", html)
        self.assertIn("Spin Lucky Wheel", html)
        self.assertIn("Run Money Laundering Missions", html)
        self.assertIn("[2m]", html)
        self.assertIn("[5m]", html)
        self.assertIn("[20m]", html)
        self.assertIn("[45m]", html)

    def test_render_pixel_operations_wall_groups_active_optional_and_ignore(self):
        html = render_pixel_operations_wall(self.weekly_report_text)

        self.assertIn("ACTIVE", html)
        self.assertIn("OPTIONAL", html)
        self.assertIn("IGNORE", html)
        self.assertIn("Money Fronts Money Laundering Missions", html)
        self.assertIn("Salvage Yard robberies", html)
        self.assertIn("[ACTIVE]", html)
        self.assertIn("[IGNORE]", html)

    def test_render_pixel_field_intel_uses_bonus_discount_and_prize_context(self):
        html = render_pixel_field_intel(self.weekly_payload)

        self.assertIn("[BONUS]", html)
        self.assertIn("[DISCOUNT]", html)
        self.assertIn("[PRIZE]", html)
        self.assertIn("Lamar Contact Missions", html)
        self.assertIn("Higgins Helitours", html)
        self.assertIn("Lampadati Komoda", html)

    def test_render_pixel_buy_ledger_uses_decision_chips(self):
        html = render_pixel_buy_ledger(self.weekly_report_text)

        self.assertIn("Higgins Helitours", html)
        self.assertIn("Benefactor Terrorbyte", html)
        self.assertIn("[BUY]", html)
        self.assertIn("[HOLD]", html)
        self.assertIn("[IGNORE]", html)
        self.assertNotIn("โปรไฟล์นี้มีอยู่แล้ว", html)
        self.assertNotIn("ซื้อเฉพาะถ้ายังไม่มี", html)
        self.assertNotIn("current ownership", html)
        self.assertNotIn("current setup", html)

    def test_build_pixel_replacements_returns_every_marker(self):
        replacements = build_pixel_replacements(
            weekly_payload=self.weekly_payload,
            player_profile=self.player_profile,
            weekly_report_text=self.weekly_report_text,
        )

        self.assertEqual(set(replacements), set(PIXEL_MARKERS))
        self.assertIn("Money Fronts Special", replacements["pixel_command_brief"])
        self.assertIn("Claim Higgins Helitours", replacements["pixel_action_queue"])


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
