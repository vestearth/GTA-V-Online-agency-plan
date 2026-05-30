# Dashboard Generator Design

**Goal:** Add an optional generator for `dashboard.html` that updates only data-driven dashboard blocks from the latest weekly planning payload, the player profile, and the standard weekly reports.

**Scope:** This design covers the first generator for issue `#9`. It keeps the dashboard as a static HTML/CSS page, but automates refresh of weekly and profile snapshot sections. It does not redesign the dashboard, replace CSS, or fetch new prices from the web.

## Why This Change

The dashboard is now structured clearly enough to support automated refresh, but it is still maintained by hand. Weekly content changes often enough that the manual workflow is likely to drift:

- weekly discount groups change every week
- weekly showroom, podium, prize ride, and other vehicle surfaces change every week
- weekly recommendations and asset priorities shift with the event week
- summary totals become more useful if they are recalculated consistently instead of edited by hand

The generator should therefore update the existing page structure without taking over the whole document.

## Chosen Approach

Use a **marker-based generator**.

The generator will update only explicitly marked regions inside `dashboard.html`, instead of rewriting the entire file. Each generated block will be bounded by clear HTML comments such as:

```html
<!-- START: weekly_deals -->
...
<!-- END: weekly_deals -->
```

This approach was chosen because:

- it keeps diffs smaller than full-file regeneration
- it preserves hand-tuned layout and copy outside generated blocks
- it matches the current repository style, where `dashboard.html` is a curated static file
- it reduces the risk of fragile DOM rewriting based only on incidental structure

## Data Sources

The generator should use these canonical inputs:

1. `data/player_profile.json`
2. latest `data/weekly_planning_*.json`, unless overridden by CLI flag
3. matching weekly reports for the same week id:
   - `reports/weekly_master_plan_<week_id>.md`
   - `reports/weekly_master_plan_<week_id>_income_scenarios.md`
   - `reports/event_master_plan_<week_id>.md`
4. `data/references/vehicle_prices.yaml` for known vehicle base prices and GTACars links

The generator should not fetch external web data during dashboard generation.

## Phase Split

Issue `#9` should be handled in two phases inside the same generator effort.

### Phase 1: deterministic generation

This phase should only update blocks whose data can be derived with high confidence from structured repository inputs:

- `header_meta`
- `summary_cards`
- `weekly_deals`
- `weekly_vehicle_spotlight`
- `data_status_note`

Phase 1 should require only **Phase 1 markers** to exist before writing. It must not fail solely because Phase 2 markers are still absent.

### Phase 2: curated / synthesized generation

This phase may update blocks that depend more heavily on report parsing or lightweight synthesis:

- `current_focus`
- `next_claim_buy`
- `weekly_action_plan`
- `what_to_buy_ignore`
- `asset_overview`

The first implementation should target **Phase 1 first**. Phase 2 may be deferred or partially implemented only after Phase 1 is stable.

## `data_status_note` Definition

`data_status_note` is the small provenance/status surface near the top of the dashboard that communicates:

- data source
- last reviewed date
- whether the page is currently manual, generated, or generated-with-warnings

Phase 1 should own this block so the generator can update status text consistently with each run.

## Non-Targets

The first version should not automatically rewrite:

- `Decision Log`
- footer copy
- CSS
- navigation links
- broader static explanatory copy outside generated blocks

Those remain hand-maintained unless a later issue expands generator ownership.

## Marker Layout

The generator should introduce start/end markers for each generated block. Recommended marker ids:

- `header_meta`
- `summary_cards`
- `weekly_deals`
- `weekly_vehicle_spotlight`
- `current_focus`
- `next_claim_buy`
- `weekly_action_plan`
- `what_to_buy_ignore`
- `asset_overview`
- `data_status_note`

Markers should be stable and human-readable.

Generated content should remain valid HTML and preserve existing indentation style closely enough that diffs stay readable.

## Summary Card Semantics

### Owned Major Assets

Derived from:

- `data/player_profile.json -> owned_assets.properties`

### Missing Major Assets

Derived from:

- `data/player_profile.json -> owned_assets.missing_properties`

### Discounted Items Total

Represents:

- total discounted purchase value for all weekly discounted items that have resolvable prices

Rules:

- include discounted vehicles with known discounted prices from the weekly payload
- include other discounted items only when the generator has a reliable numeric total for them
- skip unresolved prices
- report skipped items clearly

### All Cars Needed

Represents:

- total base-price cost of all vehicles surfaced during the current week, when reference prices are available

Include vehicles from:

- discount vehicle tiers
- LS Car Meet
- Luxury Autos
- Premium Deluxe Motorsport
- Premium Test Ride
- Prize Ride
- Podium
- other weekly vehicle surfaces if present in the payload and price data exists

Rules:

- if a vehicle appears more than once across surfaces, count it once
- use price data from `data/references/vehicle_prices.yaml`
- skip unresolved prices
- report skipped vehicles clearly

## Missing Price Handling

Chosen behavior: **skip but report**

If a vehicle or discounted item has no reliable price in the reference data:

- do not include it in totals
- keep the dashboard generation running
- report the omission in generator output
- add a visible dashboard note if totals exclude unresolved prices

Recommended dashboard note shape:

```text
Totals exclude 2 unresolved vehicle prices.
```

Recommended CLI stderr/output shape:

```text
warning: skipped 2 unresolved vehicle prices for All Cars Needed
```

The generator must not silently hide incompleteness.

## Weekly Deals Snapshot Rules

The generated `Weekly Deals Snapshot` must:

- show every confirmed discount group present in the current weekly payload
- show every confirmed item inside each group
- preserve future-safe support for new tiers
- use explicit value states:
  - `Free`
  - `GTA$xxx`
  - `Check source`
  - `Unknown`

Rules:

- do not hardcode only current known tiers
- render only groups present in the selected payload
- use discounted price when the payload provides it or when the repository has a reliable matching derived value
- do not imply a price if only a discount percentage is known

## Weekly Vehicle Spotlight Rules

The generated `Weekly Vehicle Spotlight` must:

- show every confirmed vehicle surface present in the selected weekly payload
- keep showroom/test-ride/prize/podium semantics separate from discounts
- not imply a discount unless the payload explicitly confirms one

Possible current surfaces include:

- `LS Car Meet`
- `Luxury Autos`
- `Premium Deluxe Motorsport`
- `Premium Test Ride`
- `Prize Ride`
- `Podium`

Future surfaces should be allowed without redesign.

Each row should include:

- vehicle name
- optional note such as `Prize Ride`, `Test Track`, `Showroom`, `Lucky Wheel`, or platform/access note

If the vehicle exists in `vehicle_prices.yaml` with a GTACars `source_url`, the generated row should preserve the external vehicle link behavior used by the current static page.

## Report Parsing and Confidence Rules

Structured data should be preferred whenever available.

Markdown report parsing is inherently less stable than JSON-backed generation, so the generator must distinguish between:

- deterministic blocks that should always regenerate from structured data
- report-derived blocks that may need a confidence gate

Rule:

- if a report-derived block cannot be parsed confidently, do not blank it
- instead, either preserve the existing marked block unchanged or render `Check source`, depending on block type

Recommended behavior:

- deterministic blocks: regenerate every run
- report-derived recommendation blocks: preserve existing content if parse confidence is low

This protects hand-written or previously curated copy from being overwritten by low-confidence parsing failures.

## Recommendation Block Rules

### Current Focus

Derived from:

- latest weekly payload summary
- `reports/weekly_master_plan_<week_id>.md`

The generator should produce a short summary phrase suitable for the summary card.

If confidence is low, preserve the existing block content.

### Next Claim / Buy

Derived from:

- weekly master plan
- event master plan
- ownership checks against `data/player_profile.json`

The generator should surface the top actionable claim or buy, not a generic recommendation.

If confidence is low, preserve the existing block content.

### Weekly Action Plan

Derived from:

- `reports/weekly_master_plan_<week_id>.md`

The generator should extract or synthesize a concise ordered list, preserving static dashboard readability rather than dumping the whole report.

If confidence is low, preserve the existing block content.

### What to Buy / Ignore

Derived from:

- weekly master plan
- event master plan
- ownership checks
- guardrails from repository rules

The generator should preserve explicit rulings such as:

- claim
- check
- skip
- ignore
- do not claim

If confidence is low, preserve the existing block content.

## Asset Overview Rules

`Asset Overview` is profile-driven but weekly-aware.

It should:

- use `data/player_profile.json` as the source of truth for ownership state
- use weekly payload plus weekly reports for current priority and note text
- avoid inferring ownership from showroom/test ride visibility
- allow a conditional/watch row such as `Benefactor Terrorbyte` when it is a meaningful weekly purchase candidate

The generator does not need to expand this into a full inventory dump. It should preserve the current curated-table style.

If confidence is low, preserve the existing block content.

## CLI Behavior

Recommended command:

```bash
python scripts/generate_dashboard.py
```

Recommended options:

- `--weekly <path>` to force a specific weekly payload
- `--output <path>` to write to a different HTML file for preview/testing
- `--dry-run` to print what would change without writing
- `--check-markers` to validate required markers and exit without writing

Default behavior:

- choose the latest `data/weekly_planning_*.json`
- derive the matching week id
- locate matching reports
- rewrite only marked blocks in `dashboard.html`

Marker validation behavior:

- `--dry-run` must validate markers before reporting planned updates
- `--check-markers` may be provided as a dedicated validation-only mode if implementation remains clean

## Error Handling

Hard failures:

- no weekly payload found
- required `dashboard.html` markers missing
- matching weekly report set missing in a way that blocks requested synthesized generated blocks

Soft warnings:

- unresolved vehicle prices
- unresolved non-vehicle discount values
- profile note inconsistencies that do not block rendering
- low-confidence report parsing for synthesized blocks

On hard failure, do not partially rewrite the dashboard.

Report availability rule:

- missing reports must not block Phase 1 if the selected run updates only deterministic blocks
- missing reports may block only the synthesized blocks that depend on them
- if synthesized blocks are requested but the needed reports are missing, preserve existing synthesized blocks and emit warnings unless the selected mode explicitly requires strict failure

## Testing Strategy

The first implementation should include focused tests for:

- latest-week file selection
- week-id matching between payload and report files
- marker replacement logic
- summary total calculation
- duplicate vehicle de-duplication in `All Car Total Needs`
- unresolved-price reporting behavior
- generated HTML fragments for weekly deals and vehicle spotlight

Prefer parsing/snapshot testing of generated fragments over brittle whole-file golden snapshots.

## Documentation Impact

When implemented, update:

- `README.md` to document generator usage
- `docs/dashboard-data-map.md` to reflect which blocks are generated vs still manual

The dashboard should still be described as static HTML/CSS, but no longer fully manual once the generator lands.

## GTACars Link Rules

If a generated vehicle row has a matching `source_url` in `data/references/vehicle_prices.yaml`, preserve the external vehicle-link behavior used by the current static page.

Preferred HTML pattern:

```html
<a href="https://gtacars.net/gta5/example" target="_blank" rel="noopener noreferrer">
```

If the page currently already uses a consistent external-link pattern, preserve that pattern. Otherwise, use the explicit safe pattern above.

## Sample Flow

```text
1. Choose latest weekly payload
2. Resolve matching week id
3. Load player profile
4. Validate all required markers exist
5. Load weekly reports for that week
6. Load vehicle price reference data
7. Build deterministic HTML fragments per marker
8. Build synthesized fragments only when parse confidence is sufficient
9. Preserve existing synthesized blocks when confidence is low
10. Replace marked regions in dashboard.html
11. Print warnings for skipped totals, unresolved prices, or low-confidence report parsing
12. Write output file
```

## Verification

When implemented, verify:

- `dashboard.html` keeps the same overall structure and styling
- generated blocks update for a new weekly payload without hand-editing HTML
- `Discounted Items Total` and `All Cars Needed` recalculate correctly
- totals visibly report unresolved prices instead of silently hiding them
- `Weekly Deals Snapshot` shows all confirmed groups/items for the chosen week
- `Weekly Vehicle Spotlight` shows all confirmed current vehicle surfaces for the chosen week
- GTACars links remain present where `vehicle_prices.yaml` has `source_url`
- `--dry-run` validates markers and reports planned block updates without writing
- low-confidence parsing does not blank synthesized dashboard blocks
- manual-only sections such as `Decision Log` remain untouched
