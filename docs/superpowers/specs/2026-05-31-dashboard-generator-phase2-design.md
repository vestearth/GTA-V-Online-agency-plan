# Dashboard Generator Phase 2 Design

**Goal:** Extend `scripts/generate_dashboard.py` so it can refresh the report-derived dashboard sections without blanking curated content when parsing is low-confidence.

## Scope

This phase targets the sections that already exist in `dashboard.html` today:

- `weekly_action_plan`
- `what_to_buy_ignore`
- `asset_overview`

The older conceptual labels `current_focus` and `next_claim_buy` remain deferred for now because the current dashboard markup does not expose dedicated blocks for them. Phase 2 should not invent new layout just to satisfy those names.

## Chosen Approach

Use the existing marker-based generator and extend it with a second set of markers for the report-derived blocks. Each Phase 2 block should:

1. validate its markers independently
2. load the current week bundle
3. parse only the report sections it truly needs
4. preserve the current block unchanged if parse confidence is too low

This keeps the generator safe: structured JSON still drives Phase 1, while Markdown drives Phase 2 only when the section shape is stable enough.

## Data Sources

Phase 2 should use:

- `data/player_profile.json`
- latest `data/weekly_planning_*.json`
- `reports/weekly_master_plan_<week_id>.md`
- `reports/event_master_plan_<week_id>.md`
- `reports/weekly_master_plan_<week_id>_income_scenarios.md`
- `data/references/vehicle_prices.yaml` only when an existing vehicle-link pattern needs to be preserved

## Marker Ownership

Phase 2 should add and own only these markers:

- `weekly_action_plan`
- `what_to_buy_ignore`
- `asset_overview`

Phase 1 must continue to work even if these markers are absent. `--check-markers` should remain Phase 1-only for now, while full generation can validate Phase 2 markers opportunistically before writing those blocks.

## Confidence Rules

### Weekly Action Plan

Primary source:

- `## Action Queue` from `reports/weekly_master_plan_<week_id>.md`

Confidence is high when:

- the `## Action Queue` section exists
- at least 3 ordered items are found

Output shape:

- preserve the existing ordered-list dashboard layout
- each step gets a title from the queue item text
- each step gets a short generated note based on deterministic mappings when available, otherwise a compact generic note such as `Generated from the weekly master plan action queue.`

If confidence is low, preserve the existing block unchanged.

### What to Buy / Ignore

Primary sources:

- `## What to Buy` from `reports/weekly_master_plan_<week_id>.md`
- `## What to Ignore` from `reports/weekly_master_plan_<week_id>.md`
- event/master-plan wording when needed for notes

Confidence is high when:

- both heading blocks exist
- at least 1 buy entry and 1 ignore entry can be parsed

Output shape:

- preserve the current table layout
- map entries into one of: `Claim`, `Check`, `Buy`, `Skip`, `Ignore`, `Do not claim`
- preserve reasoning text from the report where possible

If confidence is low, preserve the existing block unchanged.

### Asset Overview

Primary sources:

- `data/player_profile.json`
- weekly report sections and event context for current-week notes

Confidence is high when:

- the player profile loads cleanly
- at least 5 meaningful rows can be produced

Output shape:

- preserve the curated summary-table style rather than dumping every owned property
- prefer the currently relevant weekly assets:
  - Hands On Car Wash
  - Smoke on the Water
  - Nightclub
  - Agency
  - Bunker
  - The Garment Factory
  - Kosatka + Sparrow
  - Mammoth Avenger
  - Galaxy Super Yacht
  - optional watch row for `Benefactor Terrorbyte` when the week recommends an ownership check

Rules:

- ownership comes from `data/player_profile.json`, not showroom visibility
- weekly note text can be lightly synthesized from report sections
- if the profile and report do not support a row confidently, omit that row rather than inventing it

If confidence is low, preserve the existing block unchanged.

## Parsing Rules

Markdown parsing should stay simple and conservative:

- detect `##` headings by exact English heading text already used in the reports
- collect section content until the next `##` heading
- parse ordered list items with `^\d+\.\s+`
- parse bullet items with `^- `
- do not attempt full Markdown AST parsing

The generator should treat missing or malformed sections as low-confidence input, not as a reason to blank output.

## CLI Behavior

The current CLI interface may stay unchanged:

- `python scripts/generate_dashboard.py`
- `python scripts/generate_dashboard.py --dry-run`
- `python scripts/generate_dashboard.py --weekly <path>`

Phase 2 dry-run should report:

- which Phase 2 blocks are eligible to update
- which blocks are being preserved because parse confidence is low

## Testing

Add focused tests for:

- report section extraction
- low-confidence fallback that preserves existing block content
- `weekly_action_plan` rendering from `Action Queue`
- `what_to_buy_ignore` table rendering from `What to Buy` + `What to Ignore`
- `asset_overview` rendering from profile data plus week-specific notes

## Non-Goals

This phase does not:

- add new dashboard layout for `Current Focus` or `Next Claim / Buy`
- rewrite `Decision Log`
- rewrite ROI/passive-income cards
- redesign CSS or page structure
