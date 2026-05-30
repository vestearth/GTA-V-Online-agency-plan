# Static Dashboard Roadmap Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Stabilize the repository's static dashboard so it clearly documents its manual data sources, satisfies issue #8 acceptance criteria, and leaves future dashboard automation explicitly optional.

**Architecture:** Keep the dashboard as plain `dashboard.html` + `styles.css`, with repository docs explaining where values come from and how the page is maintained. Treat generator automation as a documented follow-up, not part of the baseline cleanup, so the current workflow stays dependency-free and GitHub Pages-friendly.

**Tech Stack:** Static HTML, static CSS, Markdown documentation, GitHub Pages hosting from repository root.

**Implementation Status:** Completed on 2026-05-30 for the baseline scope in issue `#8`. The optional generator and dynamic-dashboard items remain documented as future roadmap only.

---

### Task 1: Baseline Audit And Scope Lock

**Files:**
- Read: `dashboard.html`
- Read: `styles.css`
- Read: `README.md`
- Create: `docs/dashboard-data-map.md`

- [x] **Step 1: Confirm the issue baseline against current files**

Check that `dashboard.html` already exists, `README.md` already has a dashboard section, and `styles.css` currently starts with leading indentation before `:root {`.

Run: `rg -n "Static Planning Dashboard|dashboard.html|GitHub Pages" README.md dashboard.html styles.css`
Expected: matches in `README.md` and `dashboard.html`, plus evidence that `styles.css` is the stylesheet used by `dashboard.html`.

- [x] **Step 2: Lock implementation scope to v1.1-v1.3**

Treat the issue's immediate implementation as:
1. static dashboard hygiene,
2. data-source visibility,
3. data mapping documentation,
4. local/GitHub Pages usage notes.

Leave `scripts/generate_dashboard.py` and any dynamic dashboard work as documented roadmap items only.

- [x] **Step 3: Record acceptance checkpoints before editing**

Use this checklist while implementing:
1. `dashboard.html` shows data source, last reviewed, and manual status.
2. `styles.css` begins directly with `:root {`.
3. `docs/dashboard-data-map.md` exists with field/source/update-rule mapping.
4. `README.md` explains local open flow and optional GitHub Pages usage.
5. No npm, build step, or backend is introduced.

### Task 2: Dashboard Hygiene And Provenance Note

**Files:**
- Modify: `dashboard.html`
- Modify: `styles.css`

- [x] **Step 1: Clean stylesheet file start**

Edit `styles.css` so the first visible characters in the file are `:root {` with no BOM, blank line, or leading spaces before it.

Run: `Get-Content styles.css -TotalCount 3`
Expected: the first printed line starts with `:root {`.

- [x] **Step 2: Add a visible data provenance block near the dashboard header**

Add a small, readable note in `dashboard.html` near the top metadata area or immediately below the header. It should include these exact concepts:
- `Data source: manual snapshot from data/player_profile.json + latest weekly_planning_*.json + reports/`
- `Last reviewed: YYYY-MM-DD`
- `Data status: Manual / Needs sync`

Keep the copy visible in the page body, not only in the footer.

- [x] **Step 3: Keep the dashboard dependency-free**

While editing `dashboard.html`, do not add script tags, package references, external UI libraries, or any build-generated asset links. Continue using only the existing local stylesheet.

- [x] **Step 4: Keep the footer consistent with the new provenance note**

Adjust the footer text only if needed so it reinforces the same manual-update workflow instead of duplicating conflicting wording.

### Task 3: Dashboard Data Mapping Documentation

**Files:**
- Create: `docs/dashboard-data-map.md`
- Read: `dashboard.html`
- Read: `data/player_profile.json`
- Read: latest weekly planning JSON in `data/`
- Read: relevant report files in `reports/` if a dashboard field summarizes report output

- [x] **Step 1: Create the dashboard data map document**

Add `docs/dashboard-data-map.md` with a concise explanation that the dashboard is currently a manual snapshot surface rather than a generated artifact.

- [x] **Step 2: Add a field mapping table**

Document at least these field families in a Markdown table with columns `Dashboard field`, `Source`, and `Update rule`:
- Bankroll
- Owned Major Assets
- Missing Major Assets
- Weekly Plan / Current Focus
- ROI / Passive Income
- What to Buy / Ignore
- Decision Log
- Last reviewed
- Data status

- [x] **Step 3: Tie each field to canonical repo sources**

Prefer explicit sources already used in this repository:
- `data/player_profile.json`
- latest `data/weekly_planning_*.json`
- `reports/weekly_master_plan_<week_id>.md`
- `reports/weekly_master_plan_<week_id>_income_scenarios.md`
- `reports/event_master_plan_<week_id>.md`

If a dashboard value is curated by hand rather than directly traceable, say so plainly in the `Update rule` column.

### Task 4: README Usage And GitHub Pages Note

**Files:**
- Modify: `README.md`

- [x] **Step 1: Expand the dashboard usage section**

Under `## Static Planning Dashboard`, add a short usage subsection that explains the dashboard is a static visual planning surface derived from repo data and reports.

- [x] **Step 2: Add local-open instructions**

Include a minimal local usage snippet for opening the file directly:

```bash
open dashboard.html
```

If the surrounding README already includes cross-platform guidance elsewhere, keep this snippet as the canonical minimal example and avoid turning the section into a tooling tutorial.

- [x] **Step 3: Clarify GitHub Pages behavior**

Keep the existing hosted links if still valid, and add one short note that GitHub Pages works from `main` / repository root because the dashboard is plain static HTML/CSS.

- [x] **Step 4: Re-state the no-build constraint**

Make sure the README section explicitly says there is no npm, no build step, and no backend for this dashboard.

### Task 5: Optional Generator And Dynamic Dashboard Roadmap

**Files:**
- Modify: `README.md`
- Modify: `docs/dashboard-data-map.md`

- [x] **Step 1: Document the optional generator as future work**

Add a short roadmap note that a future `scripts/generate_dashboard.py` may compile values from:
- `data/player_profile.json`
- latest `data/weekly_planning_*.json`
- latest files in `reports/`

Do not create the script in this issue unless scope is explicitly expanded.

- [x] **Step 2: Guard against premature framework adoption**

State in docs that React, Vue, Next, Tailwind, or any dynamic rewrite should only be considered after the static workflow becomes painful to maintain and there is a concrete need for filtering, sorting, live data loading, or repeated generation.

### Task 6: Verification

**Files:**
- Read: `dashboard.html`
- Read: `styles.css`
- Read: `README.md`
- Read: `docs/dashboard-data-map.md`

- [x] **Step 1: Re-check acceptance criteria by search**

Run: `rg -n "Data source:|Last reviewed:|Data status:|Static Planning Dashboard|GitHub Pages|no npm|no build step|no backend" README.md dashboard.html docs/dashboard-data-map.md`
Expected: all required phrases appear in the edited docs and dashboard.

- [x] **Step 2: Confirm stylesheet start remains clean**

Run: `Get-Content styles.css -TotalCount 1`
Expected: output begins with `:root {`.

- [x] **Step 3: Review final diff**

Run: `git diff -- dashboard.html styles.css README.md docs/dashboard-data-map.md docs/superpowers/plans/2026-05-30-static-dashboard-roadmap.md`
Expected: only static dashboard copy, documentation, and this plan are changed.
