# Dashboard Generator Phase 1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the first deterministic `scripts/generate_dashboard.py` flow so the dashboard can refresh Phase 1 blocks from the latest weekly payload, player profile, and vehicle price reference data without rewriting the whole file.

**Architecture:** Add explicit Phase 1 HTML markers to `dashboard.html`, then implement a small marker-based generator that loads structured inputs, renders deterministic fragments, validates required markers, and replaces only those blocks. Keep Phase 2 recommendation blocks untouched for now, while updating docs so the repository clearly distinguishes generated blocks from manual ones.

**Tech Stack:** Python 3 standard library, `unittest`, static HTML/CSS, repository JSON/YAML-like reference files.

---

## File Map

- Create: `scripts/generate_dashboard.py` - Phase 1 dashboard generator CLI and marker replacement logic
- Create: `tests/test_generate_dashboard.py` - focused unit tests for latest-week selection, marker validation, totals, and generated fragments
- Modify: `dashboard.html` - add Phase 1 markers and align seeded summary/provenance copy with generator output ownership
- Modify: `README.md` - document generator usage and deterministic scope
- Modify: `docs/dashboard-data-map.md` - mark Phase 1 blocks as generated and preserve manual Phase 2 notes

### Task 1: Add Failing Tests For Phase 1 Generator

**Files:**
- Create: `tests/test_generate_dashboard.py`
- Read: `tests/test_update_vehicle_prices.py`
- Read: `data/weekly_planning_2026_w22.json`
- Read: `data/player_profile.json`

- [ ] **Step 1: Add latest-week selection and marker validation tests**

```python
import tempfile
import textwrap
import unittest
from pathlib import Path

from scripts.generate_dashboard import (
    DashboardMarkerError,
    find_latest_weekly_payload,
    validate_required_markers,
)


class DashboardGeneratorSelectionTests(unittest.TestCase):
    def test_find_latest_weekly_payload_prefers_highest_year_week(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            data_dir = Path(tmpdir)
            for name in ("weekly_planning_2026_w09.json", "weekly_planning_2026_w22.json", "weekly_planning_2025_w52.json"):
                (data_dir / name).write_text("{}", encoding="utf-8")

            latest = find_latest_weekly_payload(data_dir)

            self.assertEqual(latest.name, "weekly_planning_2026_w22.json")

    def test_validate_required_markers_raises_when_phase1_marker_missing(self):
        html = textwrap.dedent(
            \"\"\"\
            <!-- START: header_meta -->
            ok
            <!-- END: header_meta -->
            \"\"\"
        )

        with self.assertRaises(DashboardMarkerError):
            validate_required_markers(
                html,
                required_markers=[
                    "header_meta",
                    "summary_cards",
                ],
            )
```

- [ ] **Step 2: Add totals and fragment rendering tests**

```python
import json

from scripts.generate_dashboard import (
    build_phase1_context,
    format_currency_compact,
    load_vehicle_price_reference,
    render_summary_cards,
)


class DashboardGeneratorRenderingTests(unittest.TestCase):
    def test_phase1_context_builds_expected_w22_totals(self):
        weekly_payload = json.loads(Path("data/weekly_planning_2026_w22.json").read_text(encoding="utf-8"))
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
```

- [ ] **Step 3: Add dry-run planning test**

```python
from scripts.generate_dashboard import plan_phase1_updates


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
```

- [ ] **Step 4: Run the new tests to verify they fail**

Run: `python -m unittest tests.test_generate_dashboard -v`

Expected: FAIL with import errors because `scripts.generate_dashboard` and its functions do not exist yet.

### Task 2: Add Phase 1 HTML Markers

**Files:**
- Modify: `dashboard.html`
- Read: `docs/superpowers/specs/2026-05-30-dashboard-generator-design.md`

- [ ] **Step 1: Add marker pairs around the header metadata block**

Wrap the inner contents of the `<aside class="meta">` block with these exact markers:

```html
<!-- START: header_meta -->
...
<!-- END: header_meta -->
```

- [ ] **Step 2: Add marker pairs around the provenance/status block**

Wrap the inner contents of the existing `.provenance` section with:

```html
<!-- START: data_status_note -->
...
<!-- END: data_status_note -->
```

- [ ] **Step 3: Add marker pairs around the summary cards block**

Wrap the inner contents of `.summary-grid` with:

```html
<!-- START: summary_cards -->
...
<!-- END: summary_cards -->
```

- [ ] **Step 4: Add marker pairs around weekly highlights fragments**

Wrap only the inner generated content for each block:

```html
<!-- START: weekly_deals -->
...
<!-- END: weekly_deals -->
```

```html
<!-- START: weekly_vehicle_spotlight -->
...
<!-- END: weekly_vehicle_spotlight -->
```

- [ ] **Step 5: Re-open the relevant HTML snippets and confirm marker spellings**

Run: `rg -n "START: header_meta|START: summary_cards|START: weekly_deals|START: weekly_vehicle_spotlight|START: data_status_note" dashboard.html`

Expected: one match per Phase 1 marker.

### Task 3: Implement `scripts/generate_dashboard.py`

**Files:**
- Create: `scripts/generate_dashboard.py`
- Read: `scripts/update_vehicle_prices.py`
- Read: `data/weekly_planning_2026_w22.json`
- Read: `data/references/vehicle_prices.yaml`

- [ ] **Step 1: Create the CLI skeleton and exception type**

Add this starting structure:

```python
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import datetime as dt
import glob
import json
import re
import sys
from pathlib import Path


class DashboardMarkerError(RuntimeError):
    pass


PHASE1_MARKERS = [
    "header_meta",
    "summary_cards",
    "weekly_deals",
    "weekly_vehicle_spotlight",
    "data_status_note",
]
```

- [ ] **Step 2: Implement latest-week selection and week-id helpers**

Include:

```python
def find_latest_weekly_payload(data_dir: Path) -> Path:
    candidates = [Path(p) for p in glob.glob(str(data_dir / "weekly_planning_*.json"))]
    if not candidates:
        raise FileNotFoundError("No weekly_planning_*.json found in data/")
    week_id_pattern = re.compile(r"^weekly_planning_(\d{4})_w(\d{1,2})\.json$")
    ranked: list[tuple[int, int, Path]] = []
    for path in candidates:
        match = week_id_pattern.match(path.name)
        if not match:
            continue
        ranked.append((int(match.group(1)), int(match.group(2)), path))
    if not ranked:
        raise FileNotFoundError("No parseable weekly_planning_<year>_w<week>.json file found in data/")
    ranked.sort()
    return ranked[-1][2]


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))
```

- [ ] **Step 3: Implement marker discovery and replacement**

Include:

```python
def validate_required_markers(html: str, required_markers: list[str]) -> None:
    missing: list[str] = []
    for marker in required_markers:
        if f"<!-- START: {marker} -->" not in html or f"<!-- END: {marker} -->" not in html:
            missing.append(marker)
    if missing:
        raise DashboardMarkerError(f"Missing required dashboard markers: {', '.join(missing)}")


def replace_marker_block(html: str, marker: str, replacement: str) -> str:
    pattern = re.compile(
        rf"(<!-- START: {re.escape(marker)} -->)(.*?)(<!-- END: {re.escape(marker)} -->)",
        flags=re.DOTALL,
    )
    match = pattern.search(html)
    if not match:
        raise DashboardMarkerError(f"Missing marker block: {marker}")
    return html[: match.start()] + match.group(1) + "\n" + replacement.rstrip() + "\n" + match.group(3) + html[match.end() :]
```

- [ ] **Step 4: Implement vehicle price reference loading**

Use a minimal line parser compatible with the current `vehicle_prices.yaml` structure:

```python
def load_vehicle_price_reference(path: Path) -> dict[str, dict[str, object]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    out: dict[str, dict[str, object]] = {}
    current_name: str | None = None
    current: dict[str, object] | None = None
    for line in lines:
        name_match = re.match(r'^  - vehicle_name: "(.*)"$', line)
        if name_match:
            if current_name and current is not None:
                out[current_name] = current
            current_name = name_match.group(1)
            current = {}
            continue
        if current is None:
            continue
        base_match = re.match(r"^    base_price: (\d+|null)$", line)
        if base_match:
            current["base_price"] = None if base_match.group(1) == "null" else int(base_match.group(1))
            continue
        source_match = re.match(r'^    source_url: "(.*)"$', line)
        if source_match:
            current["source_url"] = source_match.group(1)
    if current_name and current is not None:
        out[current_name] = current
    return out
```

- [ ] **Step 5: Implement deterministic Phase 1 context building**

Implement:

```python
def build_phase1_context(weekly_payload: dict, player_profile: dict, vehicle_prices: dict[str, dict[str, object]]) -> dict[str, object]:
    weekly_content = weekly_payload["weekly_content"]
    discounts = weekly_content.get("discounts", [])
    price_context = weekly_content.get("price_context", {})
    vehicle_opportunities = weekly_content.get("vehicle_opportunities", [])

    owned_major_assets = len(player_profile["owned_assets"]["properties"])
    missing_major_assets = len(player_profile["owned_assets"]["missing_properties"])

    discounted_items_total = 0
    unresolved_discount_items: list[str] = []
    discount_vehicle_names: list[str] = []
    seen_discount_vehicle_names: set[str] = set()
    for group in discounts:
        tier_percent = group.get("tier_percent")
        tier_label = str(group.get("tier_label", "")).casefold()
        for item in group.get("items", []):
            if tier_percent == 100:
                continue
            if item in price_context:
                context = price_context[item]
                key = f"discounted_price_{tier_percent}"
                value = context.get(key)
                if isinstance(value, int):
                    discounted_items_total += value
                    if item not in seen_discount_vehicle_names:
                        seen_discount_vehicle_names.add(item)
                        discount_vehicle_names.append(item)
                else:
                    unresolved_discount_items.append(item)
            elif "gun van" not in tier_label:
                unresolved_discount_items.append(item)

    spotlight_vehicle_names: list[str] = []
    seen_spotlight_vehicle_names: set[str] = set()
    for item in vehicle_opportunities:
        name = item.get("vehicle_name")
        if isinstance(name, str) and name not in seen_spotlight_vehicle_names:
            seen_spotlight_vehicle_names.add(name)
            spotlight_vehicle_names.append(name)

    all_vehicle_names: list[str] = []
    seen_all_vehicle_names: set[str] = set()
    for name in discount_vehicle_names + spotlight_vehicle_names:
        if name not in seen_all_vehicle_names:
            seen_all_vehicle_names.add(name)
            all_vehicle_names.append(name)

    all_cars_needed_total = 0
    unresolved_vehicle_prices: list[str] = []
    for name in all_vehicle_names:
        reference = vehicle_prices.get(name, {})
        base_price = reference.get("base_price")
        if isinstance(base_price, int):
            all_cars_needed_total += base_price
        else:
            unresolved_vehicle_prices.append(name)

    return {
        "player_name": player_profile["player_name"],
        "platform": player_profile["platform"],
        "week_id": weekly_payload["week"]["id"],
        "week_label": weekly_payload["week"]["label"],
        "last_reviewed": dt.date.today().isoformat(),
        "owned_major_assets": owned_major_assets,
        "missing_major_assets": missing_major_assets,
        "discounted_items_total": discounted_items_total,
        "all_cars_needed_total": all_cars_needed_total,
        "unresolved_discount_items": unresolved_discount_items,
        "unresolved_vehicle_prices": unresolved_vehicle_prices,
        "discounts": copy.deepcopy(discounts),
        "price_context": copy.deepcopy(price_context),
        "vehicle_opportunities": copy.deepcopy(vehicle_opportunities),
    }
```

- [ ] **Step 6: Implement Phase 1 HTML renderers**

Create focused functions:

```python
def format_currency_compact(value: int) -> str:
    if value >= 1_000_000:
        return f"GTA${value / 1_000_000:.1f}M"
    if value >= 1_000:
        return f"GTA${value / 1_000:.1f}K"
    return f"GTA${value}"
```

Also implement:

- `render_header_meta(context)`
- `render_data_status_note(context)`
- `render_summary_cards(context)`
- `render_weekly_deals(context, vehicle_prices)`
- `render_weekly_vehicle_spotlight(context, vehicle_prices)`

Requirements:

- preserve GTACars links where `source_url` exists, using `target="_blank" rel="noopener noreferrer"`
- use `Discounted Items Total` and `All Cars Needed` card labels
- report unresolved totals in the provenance block if any unresolved price lists are non-empty
- preserve current value states (`Free`, `GTA$xxx`, `Check source`, `Unknown`)

- [ ] **Step 7: Implement dry-run planning and main CLI**

Include:

```python
def plan_phase1_updates(available_markers: list[str]) -> list[str]:
    planned = [marker for marker in PHASE1_MARKERS if marker in available_markers]
    return planned
```

And a `main()` that:

- parses `--weekly`, `--output`, `--dry-run`, `--check-markers`
- loads `dashboard.html`
- validates Phase 1 markers
- loads inputs
- builds the Phase 1 context
- renders replacements
- in `--check-markers` mode prints marker validation success and exits 0
- in `--dry-run` mode prints planned block updates and unresolved warnings without writing
- otherwise rewrites only the Phase 1 marker blocks in the chosen output path

- [ ] **Step 8: Run tests again**

Run: `python -m unittest tests.test_generate_dashboard -v`

Expected: PASS

### Task 4: Update Docs For The Generator

**Files:**
- Modify: `README.md`
- Modify: `docs/dashboard-data-map.md`

- [ ] **Step 1: Add generator usage to the dashboard docs**

Add a short section in `README.md` near the dashboard area covering:

```text
python scripts/generate_dashboard.py
python scripts/generate_dashboard.py --dry-run
python scripts/generate_dashboard.py --check-markers
python scripts/generate_dashboard.py --weekly data/weekly_planning_2026_w22.json
```

- [ ] **Step 2: Clarify generated vs manual blocks in `docs/dashboard-data-map.md`**

Update these rows:

- `Player name / platform`
- `Week label`
- `Owned Major Assets`
- `Missing Major Assets`
- `Weekly Deals Snapshot`
- `Weekly Vehicle Spotlight`
- `Data source note`
- `Last reviewed`
- `Data status`

Add wording that these are generated by Phase 1 when `scripts/generate_dashboard.py` runs, while recommendation blocks remain manual until Phase 2 lands.

- [ ] **Step 3: Run a documentation grep check**

Run: `rg -n "generate_dashboard.py|--dry-run|--check-markers|Phase 1|generated" README.md docs/dashboard-data-map.md`

Expected: matches in both files.

### Task 5: Verify End-To-End Behavior

**Files:**
- Read: `dashboard.html`
- Read: `scripts/generate_dashboard.py`
- Read: `tests/test_generate_dashboard.py`

- [ ] **Step 1: Run marker validation**

Run: `python scripts/generate_dashboard.py --check-markers`

Expected: success message confirming all Phase 1 markers exist.

- [ ] **Step 2: Run dry-run mode**

Run: `python scripts/generate_dashboard.py --dry-run`

Expected:
- no file write
- list of planned block updates for the five Phase 1 markers
- unresolved warnings only if applicable

- [ ] **Step 3: Regenerate the live dashboard**

Run: `python scripts/generate_dashboard.py`

Expected:
- `dashboard.html` rewritten only inside Phase 1 markers
- summary cards show `Discounted Items Total` and `All Cars Needed`
- highlights blocks preserve GTACars links

- [ ] **Step 4: Run focused unit tests**

Run: `python -m unittest tests.test_generate_dashboard tests.test_update_vehicle_prices -v`

Expected: PASS

- [ ] **Step 5: Review final diff**

Run: `git diff -- dashboard.html scripts/generate_dashboard.py tests/test_generate_dashboard.py README.md docs/dashboard-data-map.md`

Expected: diffs only in planned files, with Phase 1 markers and generated block changes readable.
