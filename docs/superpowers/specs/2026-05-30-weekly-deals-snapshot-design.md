# Weekly Deals And Vehicle Spotlight Sidebar Design

**Goal:** Replace the current `Upgrade Checklist` sidebar block area in `dashboard.html` with weekly-offer sidebar content designed around the latest weekly payload structure, while preserving upgrade/readiness data in documentation and dashboard data mapping.

**Scope:** This change is a static dashboard layout/content update only. It prepares the dashboard to present weekly deals grouped by tier plus weekly showroom/meet vehicle surfaces. It does not yet implement automatic HTML generation from `data/weekly_planning_*.json`; that automation belongs to issue `#9`.

## Why This Change

The current sidebar block is hardcoded as an upgrade checklist, which is useful for profile readiness but not ideal for surfacing current weekly opportunities. Weekly payloads can contain:

- `Free` items or claimable weekly opportunities
- multiple discount tiers such as `50% Off`, `40% Off`, and `30% Off`
- vehicles and non-vehicle weekly deals
- showroom/meet surfaces such as `ls_car_meet` and `luxury_autos`

The sidebar should therefore reflect the latest weekly deal structure instead of assuming one fixed vehicle-only tier or collapsing showroom/meet content into discount logic.

## Agreed Direction

Replace the current sidebar block area with two new static sections:

1. `Weekly Deals Snapshot`
2. `Weekly Vehicle Spotlight`

The sidebar design should:

- use the latest `data/weekly_planning_*.json` as the source model for what kinds of deals can appear
- support grouped rendering by tier
- support separate weekly vehicle spotlight surfaces
- remain static HTML/CSS for now
- be easy to map into generator output later in issue `#9`

## Content Model: Weekly Deals Snapshot

Known current groups include:

- `Free`
- `50% Off`
- `40% Off`
- `30% Off`

Future-safe rule:

- render only groups present in the payload
- allow additional future groups if the payload includes them
- do not hardcode the contract to only the current known groups

Only groups that have items should appear.

Each item row should show:

1. item name
2. value label

Value label rules:

- if the weekly item is free, show `Free`
- if the weekly item has a discounted price, show the post-discount price
- if the source is ambiguous but the item should still be listed, show `Check source`
- if the value is genuinely unavailable or unresolved, show `Unknown`
- do not silently imply a missing value is just absent formatting

Recommended value states:

- `Free`
- `GTA$xxx`
- `Check source`
- `Unknown`

## Content Model: Weekly Vehicle Spotlight

Add a second sidebar block named `Weekly Vehicle Spotlight`.

This block should contain separate subsections for current known surfaces:

- `LS Car Meet`
- `Luxury Autos`

Rules:

- these sections represent weekly vehicle surfaces, not automatic discounts
- do not imply a vehicle is discounted unless the weekly payload explicitly supports that conclusion
- keep the model open for future surfaces without redesigning the block, for example:
  - `Premium Deluxe`
  - `Simeon`
  - `HSW`
  - `Prize Ride`
  - `Podium`
- vehicle rows may show:
  - vehicle name only
  - vehicle name plus contextual note
- if source data later confirms a limited-return or special weekly availability signal, the block should be able to show that as a compact note
- if a subsection has no items, hide that subsection

Suggested future-friendly row model:

- `surface`: `LS Car Meet` / `Luxury Autos` / future surfaces
- `name`: vehicle name
- `note`: display-only / test ride / showroom / limited return / discount if confirmed

## Layout

The current `Upgrade Checklist` sidebar card area in the `#assets` split layout is replaced with two stacked sidebar sections:

1. `Weekly Deals Snapshot`
2. `Weekly Vehicle Spotlight`

`Upgrade Checklist` should no longer be the primary sidebar block, but the underlying readiness/profile data must remain documented in the dashboard ecosystem rather than disappearing.

`Weekly Deals Snapshot` structure:

- section title: `Weekly Deals Snapshot`
- short helper copy: indicates that the snapshot is intended to track current weekly offers
- grouped deal subsections beneath the header
- each subsection includes:
  - a tier label
  - a compact two-column table or row list

Recommended presentation:

- left column: item name
- right column: discounted price or `Free`
- tier labels should be visually distinct and easy to scan
- the block should remain compact enough to sit beside `Asset Overview` without overwhelming it

`Weekly Vehicle Spotlight` structure:

- section title: `Weekly Vehicle Spotlight`
- short helper copy: indicates that these are current weekly showroom/meet surfaces from the latest payload
- subsection: `LS Car Meet`
- subsection: `Luxury Autos`
- each subsection uses a compact list or table
- presentation should prioritize vehicle names first, with optional availability/context notes second

Upgrade/readiness handling:

- remove `Upgrade Checklist` from the sidebar
- preserve the corresponding field mapping in `docs/dashboard-data-map.md`
- if useful, preserve important readiness/data-quality context in another note surface instead of discarding it completely

No empty section shell:

- if `Weekly Deals Snapshot` has no groups, show a compact empty state instead of rendering blank groups
- if `Weekly Vehicle Spotlight` has no surfaces, either hide the block or show a compact note such as `No spotlight vehicles confirmed`

Sample static content shape:

```md
Weekly Deals Snapshot
- 50% Off
  - Buckingham Nimbus — GTA$950,000
- 30% Off
  - Benefactor Terrorbyte — GTA$962,500
- Free
  - Higgins Helitours — Free

Weekly Vehicle Spotlight
- LS Car Meet
  - Übermacht Cypher — test ride
  - Karin Futo GTX — prize ride
- Luxury Autos
  - Grotti Itali GTO Stinger TT — showroom
```

## Styling Direction

Follow existing dashboard styling:

- keep the current static CSS token system
- no new framework or dependency
- keep the sidebar visually consistent with existing `.section` surfaces
- use compact rows and restrained hierarchy so both blocks read like snapshots, not full reports

Mobile behavior:

- stacked rows should remain readable
- price/value labels should not wrap awkwardly
- grouped tiers should remain visually separated
- vehicle spotlight subsections should remain visually distinct after stacking

## Non-Goals

This design does not include:

- live parsing of the latest payload inside the browser
- React/Vue/Next/Tailwind migration
- replacing the rest of the dashboard information architecture
- introducing generator code in this specific design step

## Data Mapping Impact

If this design is implemented, `docs/dashboard-data-map.md` should be updated to include rows such as:

```md
| Weekly Deals Snapshot | latest `data/weekly_planning_*.json` + reports | Manual grouped summary by tier. Show only confirmed groups and values. |
| Weekly Vehicle Spotlight | latest `data/weekly_planning_*.json` | Manual summary of showroom/meet vehicle surfaces. Do not imply discount unless confirmed. |
| Upgrade Checklist | `data/player_profile.json` -> `owned_assets.upgrades` | No longer shown as primary sidebar; keep as profile readiness reference if needed. |
```

## Implementation Notes

This design should be implemented in two phases:

1. static dashboard layout update in `dashboard.html` and `styles.css`
2. later automation in issue `#9` so the block can be generated from the latest weekly payload and standard reports

Issue sequencing:

- `#10` owns the static sidebar layout/model
- `#9` should wait until the sidebar structure is settled, then target that finalized shape for generator automation

Implementation hint:

```html
<section class="section">
  <div class="section-head">
    <h2>Weekly Deals Snapshot</h2>
    <p>Latest weekly grouped offers.</p>
  </div>
  <div class="deal-group">
    <h3>30% Off</h3>
    <div class="deal-row">
      <span>Benefactor Terrorbyte</span>
      <span>GTA$962,500</span>
    </div>
  </div>
</section>
```

## Verification

When implemented, verify:

- `Upgrade Checklist` no longer appears in the sidebar
- `Weekly Deals Snapshot` appears in the sidebar
- `Weekly Vehicle Spotlight` appears beneath it
- grouped tiers render cleanly in desktop and mobile layout
- `LS Car Meet` and `Luxury Autos` render as separate subsections inside the vehicle spotlight block
- the content shape clearly supports current known groups such as `Free`, `50% Off`, `40% Off`, and `30% Off`, while allowing additional payload groups in the future
- value labels can express `Free`, `GTA$xxx`, `Check source`, and `Unknown`
- showroom/meet vehicles are not mislabeled as discounted by default
- `docs/dashboard-data-map.md` preserves upgrade/readiness data as documented reference even though the sidebar block is replaced
- no new dependency or build step is introduced
