# Dashboard Generator Phase 2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extend the dashboard generator so it can safely update the report-derived `Weekly Action Plan`, `What to Buy / Ignore`, and `Asset Overview` sections while preserving existing content when report parsing is low-confidence.

**Architecture:** Add Phase 2 HTML markers for the existing dashboard sections, then extend `scripts/generate_dashboard.py` with conservative Markdown-section parsers and per-block fallback behavior. Keep Phase 1 deterministic behavior unchanged, and preserve current dashboard HTML for any Phase 2 block that cannot be parsed confidently.

**Tech Stack:** Python 3 standard library, `unittest`, static HTML, repository Markdown reports.

---

## File Map

- Modify: `dashboard.html` - add Phase 2 markers around existing section bodies
- Modify: `scripts/generate_dashboard.py` - add report loading, section parsing, Phase 2 renderers, and preserve-on-low-confidence logic
- Modify: `tests/test_generate_dashboard.py` - add failing tests for Phase 2 parsing and fallback behavior
- Modify: `README.md` - mention that Phase 2 is now partially generated if implemented
- Modify: `docs/dashboard-data-map.md` - mark generated Phase 2 blocks accurately
- Create: `docs/superpowers/specs/2026-05-31-dashboard-generator-phase2-design.md` - design reference

### Task 1: Add Failing Phase 2 Tests

**Files:**
- Modify: `tests/test_generate_dashboard.py`
- Read: `reports/weekly_master_plan_2026_w22.md`
- Read: `data/player_profile.json`

- [ ] **Step 1: Add report-section extraction tests**
- [ ] **Step 2: Add `weekly_action_plan` rendering test using W22 `Action Queue`**
- [ ] **Step 3: Add `what_to_buy_ignore` rendering test using W22 buy/ignore sections**
- [ ] **Step 4: Add low-confidence preserve test for malformed report input**
- [ ] **Step 5: Run `python -m unittest tests.test_generate_dashboard -v` and confirm failure before implementation**

### Task 2: Add Phase 2 Markers To `dashboard.html`

**Files:**
- Modify: `dashboard.html`

- [ ] **Step 1: Wrap the `Weekly Action Plan` body with `weekly_action_plan` markers**
- [ ] **Step 2: Wrap the `What to Buy / Ignore` table body with `what_to_buy_ignore` markers**
- [ ] **Step 3: Wrap the `Asset Overview` table body with `asset_overview` markers**
- [ ] **Step 4: Verify marker spellings with `rg -n "START: weekly_action_plan|START: what_to_buy_ignore|START: asset_overview" dashboard.html`**

### Task 3: Extend The Generator With Phase 2 Parsing

**Files:**
- Modify: `scripts/generate_dashboard.py`

- [ ] **Step 1: Add Phase 2 marker constants and report-path helpers**
- [ ] **Step 2: Add Markdown section extraction helpers for exact `##` headings**
- [ ] **Step 3: Add parsing helpers for ordered items and bullet items**
- [ ] **Step 4: Add `render_weekly_action_plan` with preserve-on-low-confidence behavior**
- [ ] **Step 5: Add `render_what_to_buy_ignore` with preserve-on-low-confidence behavior**
- [ ] **Step 6: Add `render_asset_overview` from profile + weekly notes with preserve-on-low-confidence behavior**
- [ ] **Step 7: Extend dry-run output so it reports planned Phase 2 updates and preserved blocks**
- [ ] **Step 8: Run `python -m unittest tests.test_generate_dashboard -v` and confirm Phase 2 tests pass**

### Task 4: Update Docs

**Files:**
- Modify: `README.md`
- Modify: `docs/dashboard-data-map.md`

- [ ] **Step 1: Update README generator scope language from Phase 1-only to include the new Phase 2 blocks that now generate**
- [ ] **Step 2: Update `docs/dashboard-data-map.md` so `Weekly Action Plan`, `What to Buy / Ignore`, and `Asset Overview` reflect generated-vs-preserved behavior**
- [ ] **Step 3: Verify docs with `rg -n "Phase 2|preserve|Weekly Action Plan|What to Buy / Ignore|Asset Overview" README.md docs/dashboard-data-map.md`**

### Task 5: Verify End-To-End Behavior

**Files:**
- Read: `dashboard.html`
- Read: `scripts/generate_dashboard.py`
- Read: `tests/test_generate_dashboard.py`

- [ ] **Step 1: Run `python scripts/generate_dashboard.py --dry-run` and confirm both Phase 1 updates and Phase 2 plan/preserve notes are reported**
- [ ] **Step 2: Run `python scripts/generate_dashboard.py` and confirm only marked sections change**
- [ ] **Step 3: Run `python -m unittest tests.test_generate_dashboard tests.test_update_vehicle_prices -v`**
- [ ] **Step 4: Review `git diff -- dashboard.html scripts/generate_dashboard.py tests/test_generate_dashboard.py README.md docs/dashboard-data-map.md` for only planned changes**
