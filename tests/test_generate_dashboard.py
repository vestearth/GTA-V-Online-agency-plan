import json
import re
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
    render_header_meta,
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
    render_pixel_ignore_callout,
    render_pixel_operations_wall,
)


FIXTURES = Path(__file__).resolve().parent / "fixtures"


def load_fixture_json(name):
    """Load a frozen JSON fixture committed under tests/fixtures/.

    Fixtures are frozen snapshots of a real weekly plan (2026-W23). Tests read
    them instead of the live, gitignored reports/ artifacts so the suite is
    deterministic and runs in CI on a clean checkout.
    """
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def load_fixture_text(name):
    """Load a frozen text/markdown fixture committed under tests/fixtures/."""
    return (FIXTURES / name).read_text(encoding="utf-8")


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

    def test_phase1_context_falls_back_to_vehicle_base_prices_for_w23_discounts(self):
        weekly_payload = json.loads(
            Path("data/weekly_planning_2026_w23.json").read_text(encoding="utf-8")
        )
        player_profile = json.loads(Path("data/player_profile.json").read_text(encoding="utf-8"))
        vehicle_prices = load_vehicle_price_reference(Path("data/references/vehicle_prices.yaml"))

        context = build_phase1_context(
            weekly_payload=weekly_payload,
            player_profile=player_profile,
            vehicle_prices=vehicle_prices,
        )

        self.assertEqual(context["discounted_items_total"], 6575800)
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
        cls.weekly_payload = load_fixture_json("weekly_planning.json")
        cls.player_profile = load_fixture_json("player_profile.json")
        cls.weekly_report_text = load_fixture_text("weekly_master_plan.md")
        cls.event_report_text = load_fixture_text("event_master_plan.md")

    def test_extract_markdown_section_reads_action_queue_block(self):
        section = extract_markdown_section(
            self.weekly_report_text,
            "## Action Queue",
        )

        self.assertIsNotNone(section)
        self.assertIn("Steal from Stash House #1", section)
        self.assertIn("Weekly Challenge GTA$100,000", section)

    def test_render_weekly_action_plan_uses_action_queue(self):
        html = render_weekly_action_plan(self.weekly_report_text)

        self.assertIsNotNone(html)
        self.assertIn("Steal from Stash House #1", html)
        self.assertIn("Street Dealers", html)
        self.assertIn('class="steps"', html)

    def test_render_what_to_buy_ignore_builds_rulings_table(self):
        html = render_what_to_buy_ignore(
            self.weekly_report_text,
            self.event_report_text,
        )

        self.assertIsNotNone(html)
        self.assertIn("Meth Lab Upgrades", html)
        self.assertIn("Buy", html)
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
        self.assertIn("Nightclub", html)

    def test_render_weekly_action_plan_returns_none_when_parse_confidence_is_low(self):
        self.assertIsNone(render_weekly_action_plan("## Something Else\n- no action queue here"))

    def test_render_current_focus_uses_weekly_payload(self):
        html = render_current_focus(self.weekly_payload, self.weekly_report_text)

        self.assertIsNotNone(html)
        self.assertIn("Community Mission Series and Meth Sales Week", html)

    def test_render_next_claim_buy_uses_first_buy_entry(self):
        html = render_next_claim_buy(self.weekly_report_text, self.event_report_text)

        self.assertIsNotNone(html)
        self.assertIn("Buy Meth Lab Upgrades", html)


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


class DashboardLanguageToggleMarkupTests(unittest.TestCase):
    def test_dashboard_defaults_to_english_without_javascript(self):
        html = Path("dashboard.html").read_text(encoding="utf-8")

        self.assertIn('<html lang="en" data-ui-language="en">', html)

    def test_dashboard_contains_terminal_language_selector(self):
        html = Path("dashboard.html").read_text(encoding="utf-8")

        self.assertIn('class="header-utility"', html)
        self.assertIn('class="pixel-lang-selector"', html)
        self.assertIn('class="lang-btn"', html)
        self.assertIn('class="bracket"', html)
        self.assertIn('data-set-language="en"', html)
        self.assertIn('data-set-language="th"', html)
        self.assertIn('aria-label="Language selection"', html)


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

        # The command brief keeps its four decision cells regardless of week.
        for label in ("HAPPENED", "TO DO", "BUY", "WHY"):
            self.assertIn(label, html)

        # Chips are derived from each week's data, so assert their shape rather
        # than a specific week's values: a bonus multiplier, a discount, and
        # timed action-queue rows.
        self.assertRegex(html, r"\[\d+x\]")
        self.assertRegex(html, r"\[\d+% OFF\]")
        self.assertRegex(html, r'class="queue-chip">\[\d+m\]')

    def test_pixel_dashboard_uses_wall_intel_and_ledger_shapes(self):
        html = Path("pixel-dashboard.html").read_text(encoding="utf-8")

        # Operations wall groups carry status chips, field intel rows carry
        # category labels, and the buy/ignore ledger carries decision chips.
        # These shapes are stable week over week; the wrapped values are not.
        self.assertRegex(html, r'class="status-chip">\[(ACTIVE|READY|OPTIONAL|IGNORE)\]')
        self.assertRegex(html, r'class="intel-label">\[(BONUS|DISCOUNT|PRIZE)\]')
        self.assertRegex(html, r'class="decision-chip">\[(BUY|HOLD|IGNORE)\]')

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


class PixelDashboardThemeLayerTests(unittest.TestCase):
    def test_pixel_dashboard_declares_functional_surface_ownership(self):
        html = Path("pixel-dashboard.html").read_text(encoding="utf-8")

        expected = {
            'data-surface-owner="recommendations"': "Command brief owns recommendations",
            'data-surface-owner="sequencing"': "Action queue owns sequencing",
            'data-surface-owner="operational-state"': "Operations wall owns operational state",
            'data-surface-owner="context"': "Field intel owns context",
            'data-surface-owner="decisions"': "Ledger owns decisions",
        }

        for marker, message in expected.items():
            with self.subTest(marker=marker):
                self.assertIn(marker, html, message)

    def test_pixel_css_declares_strict_theme_layer_order(self):
        css = Path("pixel-dashboard.css").read_text(encoding="utf-8")

        self.assertIn("Theme Layer Order: Information > Functional > Atmospheric > Decorative", css)
        self.assertIn("--surface-rank-command: 1", css)
        self.assertIn("--surface-rank-intel: 4", css)
        self.assertIn("--command-brief-strength", css)
        self.assertIn("--field-intel-strength", css)

    def test_command_brief_has_stronger_treatment_than_field_intel(self):
        css = Path("pixel-dashboard.css").read_text(encoding="utf-8")

        self.assertIn("border: 2px solid var(--primary)", css)
        self.assertIn("box-shadow: var(--shadow), var(--glow-primary)", css)
        self.assertIn(".field-intel {\n  --surface-strength: var(--field-intel-strength);", css)
        self.assertNotIn(".field-intel {\n  --surface-strength: var(--command-brief-strength);", css)

    def test_pixel_css_forbids_motion_on_critical_information(self):
        css = Path("pixel-dashboard.css").read_text(encoding="utf-8")

        forbidden_patterns = [
            ".command-cell h3 { animation:",
            ".command-chip { animation:",
            ".queue-task { animation:",
            ".queue-chip { animation:",
            ".decision-chip { animation:",
            "marquee",
        ]

        for pattern in forbidden_patterns:
            with self.subTest(pattern=pattern):
                self.assertNotIn(pattern, css)

        self.assertIn("@media (prefers-reduced-motion: reduce)", css)
        self.assertIn("transition: none", css)

    def test_visual_companions_are_decorative_and_nonsemantic(self):
        html = Path("pixel-dashboard.html").read_text(encoding="utf-8")
        css = Path("pixel-dashboard.css").read_text(encoding="utf-8")

        self.assertIn('data-theme-layer="decorative"', html)
        self.assertIn('aria-hidden="true"', html)
        self.assertIn("visual-companion", html)
        self.assertIn(".visual-companion", css)
        self.assertIn("pointer-events: none", css)


class PixelDashboardLanguageToggleMarkupTests(unittest.TestCase):
    def test_pixel_dashboard_defaults_to_english_without_javascript(self):
        html = Path("pixel-dashboard.html").read_text(encoding="utf-8")

        self.assertIn('<html lang="en" data-ui-language="en">', html)

    def test_pixel_dashboard_contains_terminal_language_selector(self):
        html = Path("pixel-dashboard.html").read_text(encoding="utf-8")

        self.assertIn('class="pixel-header-utility"', html)
        self.assertIn('class="pixel-lang-selector"', html)
        self.assertIn('class="lang-btn"', html)
        self.assertIn('class="bracket"', html)
        self.assertIn('data-set-language="en"', html)
        self.assertIn('data-set-language="th"', html)
        self.assertIn('aria-label="Language selection"', html)


class DashboardLanguageScriptMarkupTests(unittest.TestCase):
    def test_language_script_contains_shared_storage_key_and_root_attribute(self):
        script = Path("dashboard-language.js").read_text(encoding="utf-8")

        self.assertIn("gta-dashboard-language", script)
        self.assertIn("function normalizeLanguage", script)
        self.assertIn('value === "th" ? "th" : "en"', script)
        self.assertIn("document.documentElement", script)
        self.assertIn("root.lang = language", script)
        self.assertIn('root.setAttribute("data-ui-language", language)', script)
        self.assertIn("data-ui-language", script)
        self.assertIn("aria-pressed", script)
        self.assertIn("localStorage", script)
        self.assertIn("window.localStorage.getItem(STORAGE_KEY)", script)
        self.assertIn("window.localStorage.setItem(STORAGE_KEY, language)", script)
        self.assertIn('button.setAttribute("aria-pressed"', script)
        self.assertIn("data-set-language", script)


class DashboardBilingualRenderingTests(unittest.TestCase):
    def test_render_header_meta_outputs_en_and_th_variants(self):
        weekly_payload = json.loads(
            Path("data/weekly_planning_2026_w22.json").read_text(encoding="utf-8")
        )
        player_profile = json.loads(Path("data/player_profile.json").read_text(encoding="utf-8"))
        vehicle_prices = load_vehicle_price_reference(Path("data/references/vehicle_prices.yaml"))
        context = build_phase1_context(weekly_payload, player_profile, vehicle_prices)

        html = render_header_meta(context)

        self.assertIn('data-lang="en"', html)
        self.assertIn('data-lang="th"', html)
        self.assertIn("Week 2026-W22", html)
        self.assertIn("สัปดาห์ 2026-W22", html)


class PixelDashboardGeneratorRenderingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.weekly_payload = load_fixture_json("weekly_planning.json")
        cls.player_profile = load_fixture_json("player_profile.json")
        cls.weekly_report_text = load_fixture_text("weekly_master_plan.md")
        cls.vehicle_prices = load_vehicle_price_reference(Path("data/references/vehicle_prices.yaml"))
        cls.context = build_phase1_context(
            weekly_payload=cls.weekly_payload,
            player_profile=cls.player_profile,
            vehicle_prices=cls.vehicle_prices,
        )

    def test_render_pixel_header_meta_uses_current_week(self):
        html = render_pixel_header_meta(self.context)

        self.assertIn("Strategy Snapshot", html)
        self.assertIn("2026-W23", html)
        self.assertIn("READY TO RUN", html)
        self.assertIn("Thursday 08:00 Bangkok", html)

    def test_render_pixel_command_brief_uses_current_week_focus(self):
        html = render_pixel_command_brief(self.weekly_payload, self.weekly_report_text)

        self.assertIn("Community Mission Series and Meth Sales Week", html)
        self.assertIn("Meth Lab Upgrades", html)
        self.assertIn("[4x]", html)
        self.assertIn("[40% OFF]", html)
        self.assertNotIn("Nightclub Sales Lead The Week", html)

    def test_render_pixel_action_queue_uses_report_steps_and_time_chips(self):
        html = render_pixel_action_queue(self.weekly_payload, self.weekly_report_text)

        self.assertIn("Steal from Stash House #1", html)
        self.assertIn("Spin Lucky Wheel", html)
        self.assertIn("Sell to Street Dealers while product stock is available", html)
        self.assertNotIn("[ ]", html)
        # Each queue row carries a timed chip (shape, not a fixed value).
        self.assertRegex(html, r'class="queue-chip">\[\d+m\]')

    def test_render_pixel_operations_wall_groups_active_optional_and_ignore(self):
        html = render_pixel_operations_wall(self.weekly_report_text)

        self.assertIn("ACTIVE", html)
        self.assertIn("OPTIONAL", html)
        self.assertIn("IGNORE", html)
        self.assertIn("Weekly Challenge", html)
        self.assertIn("Salvage Yard robbery vehicles", html)
        self.assertIn("[ACTIVE]", html)
        self.assertIn("[IGNORE]", html)

    def test_render_pixel_field_intel_uses_bonus_discount_and_prize_context(self):
        html = render_pixel_field_intel(self.weekly_payload)

        self.assertIn("[BONUS]", html)
        self.assertIn("[DISCOUNT]", html)
        self.assertIn("[PRIZE]", html)
        self.assertIn("Community Mission Series", html)
        self.assertIn("Meth Labs", html)
        self.assertIn("Vapid GB200", html)
        self.assertNotIn("5x GTA$ &amp; RP this week", html)

    def test_render_pixel_ignore_callout_stays_headline_only(self):
        html = render_pixel_ignore_callout(self.weekly_report_text)

        self.assertLessEqual(html.count("<li>"), 2)
        self.assertIn("Rhino Tank / MTL Dune / BF Raptor", html)
        self.assertNotIn("Discount exists, but it adds little", html)

    def test_render_pixel_buy_ledger_uses_decision_chips(self):
        html = render_pixel_buy_ledger(self.weekly_report_text)

        self.assertIn("Meth Lab Upgrades", html)
        self.assertIn("Western Company Rogue", html)
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
        self.assertIn("Community Mission Series and Meth Sales Week", replacements["pixel_command_brief"])
        self.assertIn("Steal from Stash House #1", replacements["pixel_action_queue"])


class PixelDashboardBilingualRenderingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.weekly_payload = load_fixture_json("weekly_planning.json")
        cls.player_profile = load_fixture_json("player_profile.json")
        cls.weekly_report_text = load_fixture_text("weekly_master_plan.md")

    def test_render_pixel_command_brief_outputs_bilingual_copy_and_universal_chips(self):
        html = render_pixel_command_brief(self.weekly_payload, self.weekly_report_text)

        self.assertIn('data-lang="en"', html)
        self.assertIn('data-lang="th"', html)
        self.assertIn("[4x]", html)
        self.assertNotIn("[ซื้อ]", html)
        self.assertNotIn("[ลำดับความสำคัญ]", html)

    def test_render_pixel_buy_ledger_outputs_bilingual_copy_and_universal_chips(self):
        html = render_pixel_buy_ledger(self.weekly_report_text)

        self.assertIn('data-lang="en"', html)
        self.assertIn('data-lang="th"', html)
        self.assertIn("[BUY]", html)
        self.assertIn("[HOLD]", html)
        self.assertIn("[IGNORE]", html)
        self.assertNotIn("[ซื้อ]", html)
        self.assertNotIn("[ข้าม]", html)

    def test_remaining_pixel_generated_blocks_output_bilingual_copy(self):
        html_blocks = [
            render_pixel_header_meta(build_phase1_context(
                self.weekly_payload,
                self.player_profile,
                load_vehicle_price_reference(Path("data/references/vehicle_prices.yaml")),
            )),
            render_pixel_ignore_callout(self.weekly_report_text),
            render_pixel_action_queue(self.weekly_payload, self.weekly_report_text),
            render_pixel_operations_wall(self.weekly_report_text),
            render_pixel_field_intel(self.weekly_payload),
        ]

        for html in html_blocks:
            with self.subTest(html=html[:80]):
                self.assertIn('data-lang="en"', html)
                self.assertIn('data-lang="th"', html)

    def test_pixel_dashboard_shell_chrome_is_bilingual(self):
        html = Path("pixel-dashboard.html").read_text(encoding="utf-8")
        body_html = html.split("<body", 1)[1]

        expected_shell_markers = [
            "Weekly Operations Center",
            "Classic View",
            "WEEKLY COMMAND BRIEF",
            "ACTION QUEUE",
            "OPERATIONS WALL",
            "FIELD INTEL",
            "BUY / IGNORE LEDGER",
        ]

        for marker in expected_shell_markers:
            with self.subTest(marker=marker):
                position = body_html.find(marker)
                self.assertNotEqual(position, -1)
                nearby = body_html[max(0, position - 160): position + 220]
                self.assertIn('data-lang="en"', nearby)
                self.assertIn('data-lang="th"', nearby)


class PixelOperationsRoomSpecTests(unittest.TestCase):
    def test_theme_spec_declares_ledger_decision_chip_vocabulary(self):
        spec = Path("docs/superpowers/specs/2026-06-03-pixel-operations-room-theme-design.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("[BUY]", spec)
        self.assertIn("[HOLD]", spec)
        self.assertIn("[IGNORE]", spec)


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
