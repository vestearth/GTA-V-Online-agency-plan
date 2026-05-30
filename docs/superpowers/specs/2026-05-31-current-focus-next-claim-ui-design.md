# Current Focus / Next Claim UI Design

**Goal:** Add explicit dashboard UI blocks for `Current Focus` and `Next Claim / Buy` by using the first two summary-card slots, while keeping them ready for future generator ownership.

## Scope

This issue is UI-first and layout-first.

It should:

- add visible dedicated dashboard blocks for `Current Focus`
- add visible dedicated dashboard blocks for `Next Claim / Buy`
- place them in a way that fits the current dashboard reading flow
- preserve the static HTML/CSS structure already established in `dashboard.html`
- leave generator ownership as a follow-up concern rather than the main implementation target

This issue should not:

- redesign unrelated sections
- collapse existing `Highlights`, `Weekly Plan`, `ROI`, `Decisions`, or `Assets` sections
- force broader generator/parser changes beyond obvious marker placeholders

## Why This Change

The current dashboard generator now owns deterministic and report-derived sections, but the dashboard no longer has dedicated visual surfaces for:

- `Current Focus`
- `Next Claim / Buy`

Those concepts still matter. They express the "what matters most right now" layer before the user scans weekly highlights and the detailed action queue.

Without explicit UI blocks, they are only implied by surrounding content, which makes the page less scannable and also blocks future generator ownership.

## Chosen Layout

Use the **first two summary-card slots** for `Current Focus` and `Next Claim / Buy`.

New top-of-page order:

1. summary cards
   - `Current Focus`
   - `Next Claim / Buy`
   - `Discounted Items Total`
   - `All Cars Needed`
2. `Highlights`
3. `Weekly Plan`
4. `ROI`
5. `Decisions`
6. `Assets`

This keeps the hierarchy compact:

- summary cards answer: what matters most right now?
- highlights answer: what is in this event week?
- weekly plan answers: what should I do step-by-step?

## Rejected Approaches

### Put both blocks in a separate Focus Row

Rejected after review because the dashboard already has a strong summary-card surface, and adding another dedicated row above the plan created extra vertical weight without improving the information hierarchy enough.

### Put both blocks inside `Highlights`

Rejected because it would blur the distinction between:

- weekly surfaces and deals
- recommendation interpretation

### Put both blocks at the top of `Weekly Plan`

Rejected because it would make `Weekly Plan` carry too many responsibilities and weaken the clarity of the action queue section.

## Component Shape

Both blocks should reuse the existing summary-card language:

- same `card` shell
- label at the top
- one short primary line
- one short supporting explanation line

They should feel like first-class dashboard priorities without introducing a separate card family.

## Content Intent

### Current Focus

Purpose:

- summarize the main play theme or weekly loop
- communicate what the week is really about in one glance

Expected content shape:

- title: `Current Focus`
- primary line: one concise focus statement
- supporting line: short explanation of why this is the focus

Example intent:

- `Money Fronts 4x loop`
- `Run legal missions first, then rotate into laundering for the strongest active ROI this week.`

### Next Claim / Buy

Purpose:

- summarize the top immediate acquisition action
- favor actions that are time-sensitive, free, or high-utility

Expected content shape:

- title: `Next Claim / Buy`
- primary line: one concise action target
- supporting line: short reason or condition

Example intent:

- `Claim Higgins Helitours`
- `Free this week and directly relevant to the Money Fronts network before considering optional purchases.`

## Responsive Behavior

The existing summary-card responsive behavior should continue to apply.

Rules:

- on desktop, the four summary cards remain part of the existing summary grid
- on narrow layouts, the summary grid already collapses to a single column and the new cards should follow that behavior
- no text should overflow or create unstable card heights that feel broken

## Empty-State Rules

These two summary-card slots should not produce empty shells.

Rules:

- if both fields have content, show both
- if one field is missing in a later generator phase, the existing static fallback content should remain
- if future generator ownership leaves one unresolved, do not render an empty card with only a label

For the UI-first version, seed both blocks with explicit static content.

## Generator Follow-Up

This issue is still UI-first, but it should make one deliberate generator-facing decision now:

- add markers now
- keep them limited to card body content only

That means the summary-card shell and label remain manual UI structure, while future generator ownership can update only the actionable body content.

Recommended markers:

- `current_focus`
- `next_claim_buy`

Recommended shape:

```html
<article class="card">
  <div>
    <p class="label">Current Focus</p>
    <!-- START: current_focus -->
    <p class="value text">Money Fronts 4x loop</p>
    <p class="card-note">
      Run legal missions first, then rotate into laundering for strongest active ROI.
    </p>
    <!-- END: current_focus -->
  </div>
</article>
```

```html
<article class="card">
  <div>
    <p class="label">Next Claim / Buy</p>
    <!-- START: next_claim_buy -->
    <p class="value text">Claim Higgins Helitours</p>
    <p class="card-note">
      Free this week and relevant to the Money Fronts network before optional purchases.
    </p>
    <!-- END: next_claim_buy -->
  </div>
</article>
```

Marker rules:

- explicit
- stable
- limited to card bodies
- do not wrap the entire summary-card shell
- do not wrap the outer `summary-grid` container

## Data Mapping Impact

This issue should update `docs/dashboard-data-map.md` so the dashboard documentation matches the new placement.

Required updates:

- `Current Focus` should be mapped as a dedicated summary-card slot
- `Next Claim / Buy` should be mapped as a dedicated summary-card slot
- both fields should remain future generator targets via `current_focus` and `next_claim_buy`

This keeps the data map from becoming a record of an older dashboard layout.

## Styling Guidance

The updated summary cards should follow existing dashboard conventions:

- use current tokens and spacing rhythm from `styles.css`
- avoid introducing a new card language that fights the rest of the page
- keep borders/radius/shadows aligned with the current dashboard tone
- prioritize compact readability over decorative emphasis

No new layout-specific CSS should be required if the existing summary-card styles already support the content comfortably.

## Acceptance Criteria

- dashboard includes a dedicated `Current Focus` block
- dashboard includes a dedicated `Next Claim / Buy` block
- both blocks replace the first two summary-card slots
- desktop and mobile follow the existing summary-grid behavior cleanly
- no empty-shell behavior is introduced
- `docs/dashboard-data-map.md` reflects the new summary-card placement
- generator markers wrap only the generated panel body content, not the whole layout shell
- resulting layout remains consistent with the static dashboard style
- future generator ownership can target these blocks without needing a larger layout redesign
