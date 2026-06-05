"""Bilingual content tests for the pixel dashboard.

These live in their own module so they stay decoupled from the shared
``test_generate_dashboard.py`` suite while the classic generator is iterated on.
"""

import unittest
from pathlib import Path

from scripts.generate_pixel_dashboard import (
    _parse_report_entries,
    render_pixel_buy_ledger,
    render_pixel_operations_wall,
)

FIXTURES = Path(__file__).resolve().parent / "fixtures"


class ParseBilingualContinuationTests(unittest.TestCase):
    def test_en_continuation_sets_english_keeps_thai_primary(self):
        section = (
            "1. **Label** - เหตุผลภาษาไทย\n"
            "   en: English reason here\n"
            "2. **Other** - only one language\n"
        )
        entries = _parse_report_entries(section, ordered=True)

        self.assertEqual(entries[0], ("Label", "English reason here", "เหตุผลภาษาไทย"))
        # No continuation: English falls through to the primary line.
        self.assertEqual(entries[1][0], "Other")
        self.assertEqual(entries[1][1], "only one language")

    def test_th_continuation_sets_thai_keeps_english_primary(self):
        section = "- **Item** - English primary\n  th: ไทยต่อท้าย\n"
        entries = _parse_report_entries(section, ordered=False)

        self.assertEqual(entries[0], ("Item", "English primary", "ไทยต่อท้าย"))


class PixelReasonBilingualTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = (FIXTURES / "weekly_master_plan.md").read_text(encoding="utf-8")

    def test_operations_wall_reasons_have_distinct_en_and_th(self):
        html = render_pixel_operations_wall(self.report)

        # English from an en: continuation and Thai from the primary line both appear.
        self.assertIn("A fast win that pays GTA$100,000 with no extra investment.", html)
        self.assertIn("Quick win ใช้เวลาน้อยและได้ GTA$100,000", html)

    def test_buy_ledger_reasons_have_distinct_en_and_th(self):
        html = render_pixel_buy_ledger(self.report)

        self.assertIn("Check what you already own in-game first", html)
        self.assertIn("ตรวจในเกมก่อนว่าคุณมีครบหรือยัง", html)
        # The verdict chip stays stable regardless of the English wording.
        self.assertIn("[BUY]", html)


if __name__ == "__main__":
    unittest.main()
