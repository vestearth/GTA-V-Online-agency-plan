# Weekly Deals Sidebar Layout Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the dashboard sidebar `Upgrade Checklist` block with `Weekly Deals Snapshot` and `Weekly Vehicle Spotlight`, while preserving upgrade/readiness data in documentation and keeping the dashboard static.

**Architecture:** Keep the existing `#assets` split layout and replace only the sidebar surface in `dashboard.html`. Use `styles.css` to add compact grouped-deal and vehicle-surface presentation rules, and update `docs/dashboard-data-map.md` so readiness/profile data remains documented even though it is no longer the primary sidebar block.

**Tech Stack:** Static HTML, static CSS, Markdown documentation.

---

### Task 1: Sidebar Content Restructure

**Files:**
- Modify: `dashboard.html`

- [ ] **Step 1: Replace the sidebar heading and helper copy**

Replace the current sidebar section heading `Upgrade Checklist` with a new top section title `Weekly Deals Snapshot`, followed by short helper copy that indicates the block is a manual weekly-offer snapshot based on the latest weekly payload.

- [ ] **Step 2: Replace checklist markup with grouped deals markup**

Remove the `<ul class="checklist">` block and replace it with grouped sections that support:
- `Free`
- `50% Off`
- `40% Off`
- `30% Off`

Use a compact row structure with item name on the left and value state on the right.

- [ ] **Step 3: Add value-state examples in the markup**

Ensure the static markup demonstrates the supported value states:
- `Free`
- `GTA$xxx`
- `Check source`
- `Unknown`

At least one row should show a value state that is not a numeric price so the UI contract is clear.

- [ ] **Step 4: Add the second sidebar section**

Under `Weekly Deals Snapshot`, add a second `.section` block named `Weekly Vehicle Spotlight`.

Inside it, add subsections for:
- `LS Car Meet`
- `Luxury Autos`

Each subsection should use a compact list or row layout that prioritizes vehicle name first and optional note second.

- [ ] **Step 5: Add no-empty-shell fallback copy**

Include a compact empty-state pattern in the markup design:
- for deals: helper text or a dedicated small empty-state row when no groups exist
- for spotlight: helper text or a note such as `No spotlight vehicles confirmed`

The implementation may keep real rows in the static example, but the HTML structure should make the empty-state pattern obvious and usable.

### Task 2: CSS For Deals And Spotlight Blocks

**Files:**
- Modify: `styles.css`

- [ ] **Step 1: Remove checklist-specific emphasis from the sidebar design path**

Keep existing checklist styles if they are still used nowhere else only if leaving them is lower risk, but do not rely on `.checklist` styles for the new sidebar content.

- [ ] **Step 2: Add grouped deals styling**

Add styles for the new deals block, including selectors for:
- grouped deal wrappers
- tier labels
- deal rows
- value-state pills or labels

The styles should remain visually consistent with current dashboard surfaces and support a narrow sidebar width.

- [ ] **Step 3: Add vehicle spotlight styling**

Add styles for:
- spotlight subsections
- spotlight lists/rows
- optional availability/context notes

The spotlight block should read as a separate weekly surface, not as another discount table.

- [ ] **Step 4: Add empty-state styling**

Add a compact empty-state style that works for either block without looking like a rendering failure.

- [ ] **Step 5: Check mobile behavior**

Ensure the new sidebar rows do not overflow in the existing mobile table/list behavior. Use stable spacing and wrapping so item names and value labels remain readable below `720px`.

### Task 3: Data Mapping Documentation Update

**Files:**
- Modify: `docs/dashboard-data-map.md`

- [ ] **Step 1: Update the Upgrade Checklist row**

Change the `Upgrade Checklist` row so it no longer claims the field is a primary sidebar block. Preserve it as a documented readiness/profile reference sourced from `data/player_profile.json -> owned_assets.upgrades`.

- [ ] **Step 2: Add Weekly Deals Snapshot row**

Add a row like this, adjusted only if needed for wording consistency:

```md
| Weekly Deals Snapshot | latest `data/weekly_planning_*.json` + reports | Manual grouped summary by tier. Show only confirmed groups and values. |
```

- [ ] **Step 3: Add Weekly Vehicle Spotlight row**

Add a row like this, adjusted only if needed for wording consistency:

```md
| Weekly Vehicle Spotlight | latest `data/weekly_planning_*.json` | Manual summary of showroom/meet vehicle surfaces. Do not imply discount unless confirmed. |
```

- [ ] **Step 4: Preserve source-confidence guidance**

Make sure the data map reflects that ambiguous weekly values should surface as `Check source` or `Unknown` rather than being silently guessed.

### Task 4: Verification

**Files:**
- Read: `dashboard.html`
- Read: `styles.css`
- Read: `docs/dashboard-data-map.md`

- [ ] **Step 1: Verify dashboard content replacement**

Run: `rg -n "Upgrade Checklist|Weekly Deals Snapshot|Weekly Vehicle Spotlight|LS Car Meet|Luxury Autos|Check source|Unknown" dashboard.html`
Expected:
- `Upgrade Checklist` no longer appears as the sidebar title
- new section titles and subsection labels are present

- [ ] **Step 2: Verify documentation mapping**

Run: `rg -n "Weekly Deals Snapshot|Weekly Vehicle Spotlight|Upgrade Checklist" docs/dashboard-data-map.md`
Expected: all three rows exist, and the upgrade row no longer describes the sidebar as its primary home.

- [ ] **Step 3: Review CSS additions**

Run: `rg -n "deal-|spotlight|empty-state|Weekly Deals|Weekly Vehicle" styles.css`
Expected: new selectors or comments clearly support deals, spotlight, and empty-state rendering.

- [ ] **Step 4: Review final diff**

Run: `git diff -- dashboard.html styles.css docs/dashboard-data-map.md docs/superpowers/specs/2026-05-30-weekly-deals-snapshot-design.md docs/superpowers/plans/2026-05-30-weekly-deals-sidebar-layout.md`
Expected: only the sidebar layout, styles, data map, spec, and this plan are changed.
