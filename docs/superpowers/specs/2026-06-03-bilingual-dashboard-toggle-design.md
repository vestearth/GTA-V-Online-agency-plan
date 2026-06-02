# GTA Dashboard Bilingual Toggle Design

**Date:** 2026-06-03  
**Scope:** [dashboard.html](C:/Code/GTA-V-Online-agency-plan/dashboard.html), [pixel-dashboard.html](C:/Code/GTA-V-Online-agency-plan/pixel-dashboard.html), [scripts/generate_dashboard.py](C:/Code/GTA-V-Online-agency-plan/scripts/generate_dashboard.py), [scripts/generate_pixel_dashboard.py](C:/Code/GTA-V-Online-agency-plan/scripts/generate_pixel_dashboard.py)

## Goal

Add a shared `EN / TH` language toggle to both dashboard surfaces so users can switch the entire visible experience between English and Thai without leaving the page, while preserving the current static HTML + generator architecture and GitHub Pages compatibility.

## Product Direction

This feature should feel like a lightweight viewing preference, not a separate product mode.

- The same language preference applies to both dashboard pages.
- Switching language updates the full visible page, including generated sections.
- The default language is `EN`.
- If a user previously selected a language, that preference should be restored on the next visit.

## Design Principles

- **Content First:** the dashboards must remain readable even if JavaScript fails; the page should still contain both language variants in the HTML.
- **One Preference, Two Surfaces:** `dashboard.html` and `pixel-dashboard.html` must use the same persistence key and behavior.
- **No Information Duplication:** each section keeps one primary information role; bilingual support adds presentation variants, not new content structures.
- **Generator-Friendly:** bilingual output should be produced by the existing dashboard generators rather than by a second post-processing layer.
- **GitHub Pages Safe:** no framework, no build step, no backend dependency.

## Interaction Model

Both pages will include a compact segmented control with two options:

- `EN`
- `TH`

Behavior:

1. On first load, the page defaults to `EN`.
2. If `localStorage` contains a saved language preference, the page uses it.
3. Clicking a toggle option updates the page immediately without reload.
4. The chosen language is saved and reused by both pages.

Recommended storage key:

- `gta-dashboard-language`

## Information Architecture Impact

No section ordering changes are introduced by this feature.

The current information architecture remains:

- Classic dashboard: existing section order
- Pixel dashboard:
  - `WEEKLY COMMAND BRIEF`
  - `ACTION QUEUE`
  - `OPERATIONS WALL`
  - `FIELD INTEL`
  - `BUY / IGNORE LEDGER`

Language switching changes only presentation, not layout or section responsibility.

## Markup Strategy

Each translatable visible string should render as paired language variants in the HTML.

Recommended pattern:

```html
<span data-lang="en">Weekly Command Brief</span>
<span data-lang="th">สรุปคำสั่งประจำสัปดาห์</span>
```

Rules:

- One container may hold both language variants.
- CSS controls visibility based on the active language.
- The page root should carry a language state attribute such as:

```html
<html lang="en" data-ui-language="en">
```

When Thai is active, the root changes to:

```html
<html lang="th" data-ui-language="th">
```

## Toggle Component

The toggle should be visually consistent across both pages:

- segmented control
- one active state at a time
- keyboard accessible
- no animation beyond a single emphasis transition

Suggested semantics:

```html
<div class="language-toggle" role="group" aria-label="Language">
  <button type="button" data-set-language="en" aria-pressed="true">EN</button>
  <button type="button" data-set-language="th" aria-pressed="false">TH</button>
</div>
```

## Shared Client Script

Introduce one small shared client script for both dashboards.

Responsibilities:

1. Read saved language from `localStorage`
2. Fall back to `en`
3. Set root state attributes
4. Update toggle pressed states
5. Persist language on click

Non-responsibilities:

- no DOM injection from large translation dictionaries
- no data fetching
- no section-specific business logic

## Generator Strategy

### Classic Dashboard

[scripts/generate_dashboard.py](C:/Code/GTA-V-Online-agency-plan/scripts/generate_dashboard.py) will render bilingual markup for every generator-owned block it controls today.

This includes:

- header meta
- summary cards
- weekly deals snapshot
- vehicle spotlight
- data status note
- current focus
- next claim / buy
- weekly action plan
- what to buy / ignore
- asset overview

### Pixel Dashboard

[scripts/generate_pixel_dashboard.py](C:/Code/GTA-V-Online-agency-plan/scripts/generate_pixel_dashboard.py) will render bilingual markup for all pixel markers:

- `pixel_header_meta`
- `pixel_command_brief`
- `pixel_ignore_callout`
- `pixel_action_queue`
- `pixel_operations_wall`
- `pixel_field_intel`
- `pixel_buy_ledger`

### Translation Boundary

The generators should own wording for both languages. Repository data remains the source of facts, but the generator decides how each fact is phrased in English and Thai.

This is especially important for:

- action queue command tone
- public-facing decision copy
- status explanations
- buy / ignore reasoning

## Translation Rules

- English and Thai variants should express the same meaning, not different recommendations.
- Chips may remain metric-first where useful:
  - `[4x]`
  - `[30% OFF]`
  - `[BUY]`
  - `[IGNORE]`
- Decision chips may stay in English if that becomes the chosen visual language system, but if localized, they must be localized consistently across both pages.

Recommended first implementation:

- metric chips remain language-neutral where possible
- decision chips localize only if the full dashboard language system localizes them everywhere

## Accessibility

- Toggle buttons must be keyboard reachable.
- The active language must be reflected in `aria-pressed`.
- Root `lang` attribute must follow the active language.
- Hidden language variants must not create confusing duplicate announcements for screen readers; the implementation should use a consistent visibility strategy.

## Failure Modes

If JavaScript fails:

- the page must still load
- visible content must remain readable
- the default presentation should remain English

If a generator cannot produce a bilingual block confidently:

- preserve existing marker behavior patterns
- do not blank the block
- do not mix incomplete English/Thai output in the same language variant

## Styling Rules

- The toggle must feel like tool chrome, not a hero element.
- It should live in the top metadata/navigation area on both pages.
- It must not disrupt current hierarchy or section scanning.
- Each section still has only one primary motion behavior, consistent with the approved `Interaction Budget`.

## Verification

Minimum verification scope:

1. Markup tests confirm both pages contain the shared language toggle.
2. Generator tests confirm bilingual output exists for generated blocks.
3. Client-side tests confirm:
   - default language is `en`
   - clicking `TH` updates root state
   - preference persists
4. Existing dashboard and vehicle-price suites remain green.

## Out of Scope

- Separate translated pages such as `dashboard-th.html`
- Browser locale auto-detection
- Per-section language preferences
- Runtime translation services
- CMS-style translation storage

## Implementation Boundary

This feature should add a bilingual presentation layer without changing the core weekly planning workflow, report generation rules, or dashboard section responsibilities.

The result should feel like one dashboard with a remembered language preference, not two competing versions of the same product.
