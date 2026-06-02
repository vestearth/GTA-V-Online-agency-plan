# Pixel Operations Room Theme Spec

**Date:** 2026-06-03  
**Scope:** `pixel-dashboard.html`, `pixel-dashboard.css`, `scripts/generate_pixel_dashboard.py`

## Goal

Define the theme layer for `pixel-dashboard.html` so the page can evolve from `GTA Weekly Operations Center` into a real `Pixel Dashboard` without losing operational clarity.

This spec is strict-leaning: core rules are mandatory and should be usable during PR review. Decorative choices remain flexible as long as they do not violate the core rules.

## Strictness Model

### Mandatory Core Rules

These rules are reviewable requirements:

- Layer Model
- Functional Surface Ownership
- Functional Surface hierarchy
- Motion Rules
- Static-First Rule
- Acceptance Criteria

If a change violates these rules, the PR should be rejected or revised.

### Flexible Creative Choices

These choices may evolve over time:

- exact pixel grid treatment
- scanline strength
- glow intensity
- terminal accents
- room hints
- background texture
- panel treatment
- whether the room feels more like `Agency Backroom`, `Executive Strategy Room`, or another compatible operations-room variant

Creative choices are allowed only when they preserve the mandatory core rules.

### Theme Variant Rule

Theme variants may change:

- color palette
- room hints
- decorative accents
- atmospheric texture
- panel treatment

Theme variants may not change:

- information architecture
- Functional Surface Ownership
- visual hierarchy
- Motion Rules
- Static-First Rule
- section order

A theme variant must never become a different dashboard layout in disguise.

## Room Definition

`Pixel Operations Room` is a weekly strategy room for GTA Online planning.

It is not:

- a full game UI
- a pixel-art scene first
- a private player cockpit
- a generic cyber dashboard
- a marketing landing page

It is:

- a public-facing weekly strategy room
- a readable command surface
- a pixel-styled operations dashboard
- a static planning artifact that can be hosted directly from the repository root

The room metaphor exists to clarify section roles. It must never become more important than the weekly recommendations, queue, state, context, and decisions.

## Layer Model

The theme must always follow this order:

1. Information Layer
2. Functional Room Layer
3. Atmospheric Layer
4. Decorative Layer

This order is mandatory.

The page must never drift into:

1. Decorative Layer
2. Atmospheric Layer
3. Information Layer

If decoration or atmosphere becomes the first thing a reviewer understands, the theme has failed.

### Information Layer

The Information Layer is the source of meaning.

Includes:

- weekly payload facts
- generated report recommendations
- player/profile constraints when relevant
- section order
- headings
- recommendations
- queue items
- status chips
- decision chips
- explanatory copy

This layer owns truth and priority. No visual treatment may contradict it.

### Functional Room Layer

The Functional Room Layer turns information into clear operational surfaces.

Includes:

- `WEEKLY COMMAND BRIEF`
- `ACTION QUEUE`
- `OPERATIONS WALL`
- `FIELD INTEL`
- `BUY / IGNORE LEDGER`
- header strategy snapshot
- navigation/tool chrome
- language toggle placement

Functional surfaces may have strong visual identity because they help the user understand what each section does.

### Atmospheric Layer

The Atmospheric Layer gives the page its pixel operations-room mood.

Allowed examples:

- pixel grid
- scanlines
- restrained glow
- low-contrast texture
- terminal-style accents
- panel depth

Atmosphere may support hierarchy, but it may not define hierarchy by itself.

### Decorative Layer

The Decorative Layer provides optional flavor.

Allowed examples:

- small room hints
- non-interactive light details
- subtle background artifacts
- tiny non-data scene cues

Decorative elements must be removable without changing meaning, section responsibility, or scan order.

## Functional Surface Ownership

Each major section owns one primary responsibility.

| Section | Owns |
| --- | --- |
| `WEEKLY COMMAND BRIEF` | recommendations |
| `ACTION QUEUE` | sequencing |
| `OPERATIONS WALL` | operational state |
| `FIELD INTEL` | context |
| `BUY / IGNORE LEDGER` | decisions |

No section may become the primary owner of another section's responsibility.

Examples:

- `FIELD INTEL` may mention a bonus, but it must not become the main recommendation surface.
- `OPERATIONS WALL` may show `[IGNORE]`, but it must not replace the decision role of `BUY / IGNORE LEDGER`.
- `ACTION QUEUE` may imply priority through order, but it must not become a full decision ledger.
- `WEEKLY COMMAND BRIEF` may summarize a buy decision, but it must not contain the full ledger reasoning.

This rule reinforces `No Information Duplication`: sections may reference the same weekly concept, but they must not duplicate another section's job.

## Functional Surfaces

### `WEEKLY COMMAND BRIEF`

The command brief is the strongest visual object on the page.

Rules:

- must remain visually dominant
- must read as one command board, not a deck of unrelated cards
- must contain the four semantic cells: `HAPPENED`, `TO DO`, `BUY`, `WHY`
- must keep text short
- must keep chips stable and readable
- must not contain long body copy
- must not contain decorative motion inside critical text

Reject a change if another section becomes more visually dominant than the command brief.

### `ACTION QUEUE`

The action queue owns execution order.

Rules:

- must read as an ordered sequence
- must keep row order obvious
- must keep time chips visible and stable
- may use hover or focus emphasis
- must not shift layout when hovered or focused
- must not become a generic priority table

### `OPERATIONS WALL`

The operations wall owns operational state.

Rules:

- must group items by operational category
- recommended groups are `ACTIVE`, `OPTIONAL`, and `IGNORE`
- group labels and item chips are different concepts
- item chips describe item state, such as `[ACTIVE]`, `[READY]`, or `[IGNORE]`
- must feel like a status board, not a spreadsheet
- must not become the main recommendation or decision surface

### `FIELD INTEL`

Field intel owns context.

Rules:

- must stay secondary to command brief, action queue, and operations wall
- must be label-driven rather than status-driven
- must explain what else is notable this week
- must not become a promotions feed
- must not become a changelog
- must not become the primary recommendation surface

### `BUY / IGNORE LEDGER`

The ledger owns decisions.

Rules:

- must support committed buy, hold, ignore, or similar decision states
- must appear after the user has seen the command brief, queue, and operations wall
- must feel deliberate and evaluative
- must not discover the week for the first time
- must not be visually louder than the command brief

## Visual Hierarchy

The page priority order is:

1. `WEEKLY COMMAND BRIEF`
2. `ACTION QUEUE`
3. `OPERATIONS WALL`
4. `FIELD INTEL`
5. `BUY / IGNORE LEDGER`
6. atmospheric styling
7. decorative styling

Theme intensity must follow this order.

The strongest contrast, glow, and spatial weight belong to the command brief. Decorative atmosphere must remain the weakest layer.

## Motion Rules

Motion is a strict review area.

Allowed motion:

- page or section reveal on load
- hover/focus border emphasis
- subtle glow change
- active-state transition
- non-critical atmospheric flicker, only when it is low contrast and `prefers-reduced-motion` safe

Must stay static:

- command cell text
- queue row text
- time chips
- decision chips
- section headings
- layout dimensions
- language toggle
- prices
- multipliers
- status labels
- recommendations

Never do:

- perpetual pulsing on critical information
- moving text
- marquee or ticker content for core recommendations
- animated layout shifts
- hover effects that resize rows, cards, boards, or chips
- background animation behind text
- multiple competing motion behaviors inside one section

Each section may have one primary motion behavior at most.

## Static-First Rule

If all atmospheric and decorative styling is removed, the page must still work as a dashboard.

The user must still understand:

1. what happened
2. what to do
3. what to buy
4. what to ignore
5. why the week matters

Theme cannot be the only way a section communicates its role.

## Decorative Rules

Decorative choices are flexible, but bounded.

Allowed:

- subtle pixel grid background
- scanline overlay
- faint board glow
- low-contrast panel texture
- small non-interactive room hints
- restrained terminal accents

Not allowed:

- decorative elements that look clickable
- fake controls that resemble real dashboard controls
- fake monitors with important-looking nonsense data
- large scene artwork that pushes content below the fold
- character sprites that compete with weekly information
- decoration required to understand section meaning

## Visual Companion Boundary

Visual companions are small props that reinforce the room metaphor, such as:

- clipboard
- sticky note
- radio
- crate
- folder

Visual companions may reinforce meaning. Visual companions may not carry meaning.

Removing visual companions must not change comprehension, section identity, or action priority.

Examples:

- a clipboard may reinforce that the queue is executable, but the ordered list must still communicate sequencing without it
- a radio may reinforce field context, but it must not be the only signal that a section is `FIELD INTEL`
- a folder may reinforce ledger behavior, but decisions must still come from labels, chips, and copy

Visual companions must not look clickable unless they are real controls.

## Bilingual Compatibility

The theme must support the shared `EN / TH` language toggle.

Rules:

- no fixed-width text containers that only fit English
- Thai text must not break command cells, queue rows, or ledger items
- chips may remain universal visual tokens
- Thai body copy must stay readable
- monospace styling may be used for labels, chips, and metadata
- longer Thai copy should have access to readable non-monospace font behavior

The theme must not depend on English-only text length.

## Implementation Guidance

Build in this order:

1. preserve information architecture
2. confirm Functional Surface Ownership
3. make each functional surface readable without atmosphere
4. add atmospheric styling
5. add optional decorative hints
6. add motion last

Do not add decorative assets before the functional surfaces already read correctly.

## PR Review Checklist

Use this checklist when reviewing theme changes:

- Does the Layer Model still read as Information, Functional, Atmospheric, Decorative?
- Does `WEEKLY COMMAND BRIEF` remain the strongest visual object?
- Does each section keep its Functional Surface Ownership?
- Does any section duplicate another section's primary responsibility?
- Does `ACTION QUEUE` still read as execution order?
- Does `OPERATIONS WALL` still read as operational state?
- Does `FIELD INTEL` stay contextual and secondary?
- Does `BUY / IGNORE LEDGER` still read as decision support?
- Can all decorative layers be removed without breaking comprehension?
- Are critical text, chips, prices, multipliers, and recommendations static?
- Are motion effects limited to one primary behavior per section?
- Does the design still work in both English and Thai?
- Does any decorative or atmospheric element compete with real weekly data?

## Acceptance Criteria

The theme layer is successful when:

- the user can identify each section's role before reading details
- command brief remains dominant
- action queue reads as executable order
- operations wall reads as status board
- field intel reads as context
- ledger reads as decisions
- removing decorations does not break comprehension
- Thai and English both fit cleanly
- motion never interferes with reading
- no decorative element appears more important than real weekly data

## Out of Scope

- a full pixel-art room scene
- custom animated characters
- canvas-based room rendering
- runtime theme switching between room variants
- new dashboard data model
- new weekly planning workflow order
- replacing the static HTML/CSS architecture

## Summary

Core rules are mandatory. Decorative choices are flexible.

The page may change from `Agency Backroom` to `Executive Strategy Room` over time, but it must always remain an information-first weekly operations dashboard.
