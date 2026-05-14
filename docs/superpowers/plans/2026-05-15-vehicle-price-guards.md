# Vehicle Price Guards Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prevent non-vehicle weekly items and unresolved GTACars slugs from silently entering `data/references/vehicle_prices.yaml`.

**Architecture:** Keep `scripts/update_vehicle_prices.py` as the single updater, but split its decision-making into explicit classification and reporting helpers. The script should continue to update known vehicle records, while optionally failing in strict mode when new vehicles lack a resolvable slug.

**Tech Stack:** Python standard library, `unittest`, YAML-like text editing already used by the repository scripts.

---

### Task 1: Regression Tests

**Files:**
- Modify: `tests/test_update_vehicle_prices.py`

- [ ] **Step 1: Add tests for non-vehicle filtering**

Add assertions that W20 extracts real vehicles and excludes rewards, apparel, tuning, weapons, and properties.

- [ ] **Step 2: Add tests for unresolved slug staging**

Add a synthetic payload containing one known vehicle and one made-up vehicle. Assert the helper reports only the made-up vehicle as unresolved.

### Task 2: Updater Guardrails

**Files:**
- Modify: `scripts/update_vehicle_prices.py`

- [ ] **Step 1: Add slug loading/resolution helpers**

Load `data/references/vehicle_gtacars_slugs.json` and recognize GTACars URLs already present in `vehicle_prices.yaml`.

- [ ] **Step 2: Add staging report**

Print `vehicles needing slug` for new vehicles that would otherwise be added with `source_url: "https://gtacars.net"` and `base_price: null`.

- [ ] **Step 3: Add strict mode**

Add `--strict-new-vehicles`; in this mode, unresolved new vehicles return exit code `1` before writing.

- [ ] **Step 4: Keep default workflow compatible**

Default mode still writes records, but the output must make unresolved slugs visible.

### Task 3: Verification

**Files:**
- Read: `data/weekly_planning_2026_w20.json`
- Read: `data/references/vehicle_prices.yaml`
- Read: `data/references/vehicle_gtacars_slugs.json`

- [ ] **Step 1: Run unit tests**

Run `python -m unittest tests.test_update_vehicle_prices` if Python is available.

- [ ] **Step 2: Run fallback PowerShell checks**

Confirm non-vehicle records are absent, W20 vehicle prices/URLs are populated, and slug JSON parses.

- [ ] **Step 3: Inspect git diff**

Confirm only the updater, tests, slug map, price reference, and plan changed.
