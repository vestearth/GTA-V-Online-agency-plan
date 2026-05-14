import json
import unittest
from pathlib import Path

from scripts.update_vehicle_prices import (
    classify_new_vehicle_slugs,
    extract_vehicle_names_from_weekly_payload,
)


class VehicleExtractionTests(unittest.TestCase):
    def test_weekly_w20_excludes_non_vehicle_rewards_weapons_and_services(self):
        payload = json.loads(Path("data/weekly_planning_2026_w20.json").read_text(encoding="utf-8"))

        names = extract_vehicle_names_from_weekly_payload(payload)

        self.assertIn("Benefactor LM87", names)
        self.assertIn("Benefactor Krieger", names)
        self.assertIn("Vapid FMJ MK V", names)
        self.assertIn("Dewbauchee JB 700", names)

        self.assertNotIn("Login Reward", names)
        self.assertNotIn("Prize Ride Challenge", names)
        self.assertNotIn("LS Car Meet Membership", names)
        self.assertNotIn("Horn Customization", names)
        self.assertNotIn("LS Tuners Racing Suits", names)
        self.assertNotIn("Turbo Tuning", names)
        self.assertNotIn("Eclipse Blvd Garage", names)
        self.assertNotIn("Compact EMP Launcher", names)
        self.assertNotIn("Homing Launcher", names)
        self.assertNotIn("Body Armor", names)

    def test_classifies_new_vehicles_without_resolvable_slugs(self):
        existing_records = {"Benefactor LM87": ('source_url: "https://gtacars.net/gta5/lm87"',)}
        new_vehicle_names = ["Benefactor LM87", "Imaginary Future Car"]
        slug_overrides = {"Benefactor LM87": "lm87"}

        classified = classify_new_vehicle_slugs(new_vehicle_names, existing_records, slug_overrides)

        self.assertEqual(classified.resolved, {"Benefactor LM87": "lm87"})
        self.assertEqual(classified.unresolved, ["Imaginary Future Car"])


if __name__ == "__main__":
    unittest.main()
