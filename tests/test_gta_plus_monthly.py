import datetime as dt
import json
import tempfile
import unittest
from pathlib import Path

from scripts.generate_dashboard import (
    GTA_PLUS_MARKER,
    PHASE1_MARKERS,
    find_latest_gta_plus_payload,
    gta_plus_period_covers,
    render_gta_plus_benefits,
    replace_marker_block,
)
from scripts.generate_pixel_dashboard import (
    PIXEL_GTA_PLUS_MARKER,
    render_pixel_gta_plus,
)


ROOT = Path(__file__).resolve().parent.parent
FIXTURES = Path(__file__).resolve().parent / "fixtures"


def load_fixture_payload():
    """Frozen snapshot of a real GTA+ monthly payload (2026-M06)."""
    return json.loads((FIXTURES / "gta_plus_monthly.json").read_text(encoding="utf-8"))


class FindLatestGtaPlusPayloadTests(unittest.TestCase):
    def test_returns_none_when_no_payloads(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertIsNone(find_latest_gta_plus_payload(Path(tmp)))

    def test_picks_latest_year_month(self):
        with tempfile.TemporaryDirectory() as tmp:
            data_dir = Path(tmp)
            for name in (
                "gta_plus_monthly_2025_12.json",
                "gta_plus_monthly_2026_06.json",
                "gta_plus_monthly_2026_01.json",
            ):
                (data_dir / name).write_text("{}", encoding="utf-8")
            latest = find_latest_gta_plus_payload(data_dir)
            self.assertEqual(latest.name, "gta_plus_monthly_2026_06.json")

    def test_ignores_non_matching_names(self):
        with tempfile.TemporaryDirectory() as tmp:
            data_dir = Path(tmp)
            (data_dir / "gta_plus_monthly_notes.json").write_text("{}", encoding="utf-8")
            self.assertIsNone(find_latest_gta_plus_payload(data_dir))


class GtaPlusPeriodCoversTests(unittest.TestCase):
    def setUp(self):
        self.payload = load_fixture_payload()

    def test_inside_period(self):
        self.assertTrue(gta_plus_period_covers(self.payload, dt.date(2026, 6, 12)))

    def test_boundary_dates_inclusive(self):
        self.assertTrue(gta_plus_period_covers(self.payload, dt.date(2026, 6, 11)))
        self.assertTrue(gta_plus_period_covers(self.payload, dt.date(2026, 7, 13)))

    def test_outside_period(self):
        self.assertFalse(gta_plus_period_covers(self.payload, dt.date(2026, 6, 10)))
        self.assertFalse(gta_plus_period_covers(self.payload, dt.date(2026, 7, 14)))

    def test_malformed_period_is_not_covered(self):
        self.assertFalse(gta_plus_period_covers({}, dt.date(2026, 6, 12)))
        self.assertFalse(
            gta_plus_period_covers(
                {"membership_period": {"start_date": "soon", "end_date": "later"}},
                dt.date(2026, 6, 12),
            )
        )


class RenderGtaPlusBenefitsTests(unittest.TestCase):
    def setUp(self):
        self.payload = load_fixture_payload()
        self.today = dt.date(2026, 6, 12)

    def test_renders_all_benefit_groups(self):
        rendered = render_gta_plus_benefits(self.payload, {}, today=self.today)
        self.assertIn("GTA+ Member Benefits", rendered)
        self.assertIn("June 11 - July 13 2026", rendered)
        self.assertIn("Ocelot Stromberg", rendered)
        self.assertIn("Free · GTA$2.5M value", rendered)
        self.assertIn("Claim at The Vinewood Car Club", rendered)
        self.assertIn("GTA$500,000", rendered)
        self.assertIn("5x GTA$ &amp; RP", rendered)
        self.assertIn("60% off", rendered)
        self.assertIn("Independence Day Jacket and Pants", rendered)
        self.assertIn("Vinewood Club Garage", rendered)

    def test_member_value_totals_deposit_plus_vehicle(self):
        rendered = render_gta_plus_benefits(self.payload, {}, today=self.today)
        self.assertIn("Member value this period:", rendered)
        self.assertIn("GTA$3M", rendered)

    def test_vehicle_price_falls_back_to_reference(self):
        payload = load_fixture_payload()
        del payload["monthly_benefits"]["claimable_vehicles"][0]["normal_price"]
        reference = {
            "Ocelot Stromberg": {
                "base_price": 2_500_000,
                "source_url": "https://gtacars.net/gta5/stromberg",
            }
        }
        rendered = render_gta_plus_benefits(payload, reference, today=self.today)
        self.assertIn("Free · GTA$2.5M value", rendered)
        self.assertIn("https://gtacars.net/gta5/stromberg", rendered)

    def test_active_period_has_no_expired_note(self):
        rendered = render_gta_plus_benefits(self.payload, {}, today=self.today)
        self.assertNotIn("period has ended", rendered)

    def test_expired_period_renders_refresh_note(self):
        rendered = render_gta_plus_benefits(self.payload, {}, today=dt.date(2026, 8, 1))
        self.assertIn("period has ended", rendered)

    def test_escapes_html_in_names(self):
        rendered = render_gta_plus_benefits(self.payload, {}, today=self.today)
        self.assertIn("G&#x27;s Caches", rendered)
        self.assertNotIn("<script", rendered.casefold())

    def test_replacement_fits_marker_block(self):
        rendered = render_gta_plus_benefits(self.payload, {}, today=self.today)
        html_text = (
            "<article>\n"
            f"  <!-- START: {GTA_PLUS_MARKER} -->\n"
            "  placeholder\n"
            f"  <!-- END: {GTA_PLUS_MARKER} -->\n"
            "</article>"
        )
        updated = replace_marker_block(html_text, GTA_PLUS_MARKER, rendered)
        self.assertIn("Ocelot Stromberg", updated)
        self.assertNotIn("placeholder", updated)

    def test_marker_is_optional_not_phase1(self):
        self.assertNotIn(GTA_PLUS_MARKER, PHASE1_MARKERS)


class RenderPixelGtaPlusTests(unittest.TestCase):
    def setUp(self):
        self.payload = load_fixture_payload()

    def test_renders_bilingual_intel_items(self):
        rendered = render_pixel_gta_plus(self.payload)
        self.assertIn("[PERIOD]", rendered)
        self.assertIn("[CLAIM]", rendered)
        self.assertIn("[DEPOSIT]", rendered)
        self.assertIn("[BONUS]", rendered)
        self.assertIn("[DISCOUNT]", rendered)
        self.assertIn('data-lang="en"', rendered)
        self.assertIn('data-lang="th"', rendered)
        self.assertIn("Ocelot Stromberg", rendered)
        self.assertIn("รับฟรีที่ The Vinewood Car Club", rendered)
        self.assertIn("ลด 60% สำหรับสมาชิก", rendered)

    def test_handles_minimal_payload(self):
        rendered = render_pixel_gta_plus({})
        self.assertIn("intel-list", rendered)
        self.assertNotIn("[CLAIM]", rendered)


class RepositoryGtaPlusDataTests(unittest.TestCase):
    """Guard committed monthly payloads against schema drift."""

    def test_all_committed_payloads_are_valid(self):
        paths = sorted((ROOT / "data").glob("gta_plus_monthly_*.json"))
        self.assertTrue(paths, "expected at least one data/gta_plus_monthly_*.json")
        for path in paths:
            with self.subTest(payload=path.name):
                payload = json.loads(path.read_text(encoding="utf-8"))
                self.assertEqual(payload["schema_mode"], "gta_plus_monthly")
                period = payload["membership_period"]
                start = dt.date.fromisoformat(period["start_date"])
                end = dt.date.fromisoformat(period["end_date"])
                self.assertLess(start, end)
                self.assertTrue(period["source_urls"])
                benefits = payload["monthly_benefits"]
                self.assertIsInstance(benefits["gta_dollar_deposit"], int)
                self.assertTrue(benefits["claimable_vehicles"])
                self.assertTrue(benefits["member_bonuses"])

    def test_dashboards_contain_gta_plus_markers(self):
        dashboard = (ROOT / "dashboard.html").read_text(encoding="utf-8")
        pixel = (ROOT / "pixel-dashboard.html").read_text(encoding="utf-8")
        self.assertIn(f"<!-- START: {GTA_PLUS_MARKER} -->", dashboard)
        self.assertIn(f"<!-- END: {GTA_PLUS_MARKER} -->", dashboard)
        self.assertIn(f"<!-- START: {PIXEL_GTA_PLUS_MARKER} -->", pixel)
        self.assertIn(f"<!-- END: {PIXEL_GTA_PLUS_MARKER} -->", pixel)


if __name__ == "__main__":
    unittest.main()
