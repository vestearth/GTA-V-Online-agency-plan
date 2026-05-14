import json
import unittest
import tempfile
import importlib.util
import sys
from pathlib import Path

from scripts.update_vehicle_prices import (
    classify_new_vehicle_slugs,
    extract_vehicle_names_from_weekly_payload,
    sync_slug_map,
)
from scripts.fetch_gtacar_prices import extract_prices_from_html, resolve_slug


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
        self.assertNotIn("Pool Cue", names)
        self.assertNotIn("Body Armor", names)

    def test_classifies_new_vehicles_without_resolvable_slugs(self):
        existing_records = {"Benefactor LM87": ('source_url: "https://gtacars.net/gta5/lm87"',)}
        new_vehicle_names = ["Benefactor LM87", "Imaginary Future Car"]
        slug_overrides = {"Benefactor LM87": "lm87"}

        classified = classify_new_vehicle_slugs(new_vehicle_names, existing_records, slug_overrides)

        self.assertEqual(classified.resolved, {"Benefactor LM87": "lm87"})
        self.assertEqual(classified.unresolved, ["Imaginary Future Car"])

    def test_classifies_new_vehicle_using_fallback_slug_hint(self):
        classified = classify_new_vehicle_slugs(["Bravado Banshee GTS"], {}, {})

        self.assertEqual(classified.resolved, {"Bravado Banshee GTS": "banshee3"})
        self.assertEqual(classified.unresolved, [])

    def test_resolve_slug_uses_builtin_fallbacks_for_root_source_urls(self):
        self.assertEqual(resolve_slug("Pfister Comet SR", "https://gtacars.net", {}), "comet5")
        self.assertEqual(resolve_slug("Penaud La Coureuse", "https://gtacars.net", {}), "coureur")

    def test_extract_prices_from_html_handles_visible_price_text(self):
        html = """
        <div>
          <h3>Buying, Storing & Upgrading</h3>
          <div>Price: $ 1,225,000</div>
          <div>Trade price: $ 918,750</div>
        </div>
        """

        self.assertEqual(
            extract_prices_from_html(html, "https://gtacars.net/gta5/jugular"),
            (1225000, 918750),
        )

    def test_sync_slug_map_writes_sorted_updates(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            slug_map_path = Path(tmpdir) / "vehicle_gtacars_slugs.json"
            slug_map_path.write_text(
                json.dumps(
                    {
                        "schema_version": "1.0",
                        "description": "test",
                        "slug_by_vehicle_name": {"Zed Car": "zed"},
                    },
                    indent=2,
                ),
                encoding="utf-8",
            )

            changed = sync_slug_map(slug_map_path, {"Alpha Car": "alpha", "Zed Car": "zed"}, dry_run=False)
            payload = json.loads(slug_map_path.read_text(encoding="utf-8"))

            self.assertEqual(changed, ["Alpha Car"])
            self.assertEqual(
                payload["slug_by_vehicle_name"],
                {"Alpha Car": "alpha", "Zed Car": "zed"},
            )

    def test_update_script_loads_when_executed_from_file_path(self):
        script_path = Path("scripts/update_vehicle_prices.py").resolve()
        spec = importlib.util.spec_from_file_location("update_vehicle_prices_direct", script_path)
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None

        sys.modules[spec.name] = module
        spec.loader.exec_module(module)

        self.assertTrue(hasattr(module, "classify_new_vehicle_slugs"))


if __name__ == "__main__":
    unittest.main()
