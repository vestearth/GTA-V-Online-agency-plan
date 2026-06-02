# GTA Weekly Operations Center Design

**Goal:** Evolve `pixel-dashboard.html` from a themed personal prototype into a public-facing weekly strategy surface that makes GTA Online weekly priorities obvious within seconds, while preserving fast readability of real repository data.

## Product Direction

This dashboard is no longer "player dashboard first."

It is a **Weekly Strategy Dashboard** that other people can open and understand immediately, even if they do not know the current player profile or repository structure.

The intended visual mix is:

- `70%` Management Tycoon
- `20%` Office Sim
- `10%` Progression

This should feel like a **GTA Weekly Operations Center**, not a generic analytics dashboard and not a full game UI.

## Core UX Goal

Within the first 5 seconds, the page should answer one complete command brief:

- What happened?
- What should I do?
- What should I buy?
- Why does this week matter?

The page should then naturally answer the next user questions in order:

1. What matters this week?
2. What should I do first?
3. What is currently active or worth tracking?
4. What else is available this week?
5. What decisions should I make?

## Information Architecture

Top-level page order:

1. `WEEKLY COMMAND BRIEF`
2. `ACTION QUEUE`
3. `OPERATIONS WALL`
4. `FIELD INTEL`
5. `BUY / IGNORE LEDGER`

This order is intentional:

- `WEEKLY COMMAND BRIEF` summarizes the week
- `ACTION QUEUE` sequences execution
- `OPERATIONS WALL` reflects operational state
- `FIELD INTEL` adds weekly context
- `BUY / IGNORE LEDGER` supports purchase decisions

## Section Definitions

### 1. `WEEKLY COMMAND BRIEF`

This is the hero section.

It should present a single **2x2 command board** rather than a deck of cards.

The board contains exactly four command cells:

- `HAPPENED`
- `TO DO`
- `BUY`
- `WHY`

Each cell uses:

- one short headline
- one chip

The board is a summary surface, not a report. No long descriptions, no explanatory body copy, and no stacked metadata.

Below the command board, include a small callout:

- `IGNORE THIS WEEK`

This should stay visually secondary to the 2x2 board.

### 2. `ACTION QUEUE`

This section answers:

- what should I do first?

The queue should use:

- **execution order**
- **time chip**

Example structure:

1. `Collect Agency Safe [2m]`
2. `Refill Acid Lab [5m]`
3. `Execute Nightclub Sale [20m]`
4. `Payphone Hit [10m]`

The queue should feel like a mission board or operational checklist, not like a time-management app and not like a priority ranking table.

### 3. `OPERATIONS WALL`

This section answers:

- what is currently active in the world of this week?

It should look like an operations wall or war room board, not a spreadsheet or static table.

The data model for each operation is:

- name
- status chip
- one-line reason

Example:

- `Nightclub [ACTIVE]`
  `Best weekly income`
- `Acid Lab [READY]`
  `Fast resupply cycle`

Recommended operation groups:

- `ACTIVE`
- `OPTIONAL`
- `IGNORE`

`READY` can appear as a chip inside a grouped board where appropriate.

Group and chip are not the same thing:

- a **group** is a wall section or category on the board
- a **chip** is the status of an individual operation item

Example:

- `ACTIVE` can be a group
- `READY` can be a chip on one item inside that group

### 4. `FIELD INTEL`

This section answers:

- what else is available or notable this week?

It should behave like a weekly intelligence board, not a promotions list and not a blog feed.
It must not turn into a changelog or a long news feed.

Each intel item uses exactly:

- label
- item
- implication

Example:

- `[BONUS]`
  `Nightclub Sales`
  `Highest passive income source`

- `[DISCOUNT]`
  `Agency Upgrades`
  `Best value unlock this week`

This section exists to provide context, not instructions.

### 5. `BUY / IGNORE LEDGER`

This section supports explicit decision-making once the reader already understands the week.

It should not appear before the user has seen:

- the weekly command brief
- the action queue
- the operations wall

This section is for committed decisions, not discovery.

Recommended data shape for each ledger item:

- item
- decision chip
- reason
- condition

Example:

- `Agency Upgrade [BUY]`
  `Best unlock if discounted`

## Content System

### Chips

Use only two chip languages:

#### Metric chips

Use when a metric communicates immediate meaning:

- `[2x]`
- `[3x]`
- `[40% OFF]`
- `[$500K]`

#### Decision chips

Use when no meaningful metric exists:

- `[PRIORITY]`
- `[BEST VALUE]`
- `[FAST CASH]`
- `[SKIP]`

### Chip Priority Rule

**Metric > Decision**

If a meaningful metric exists, use the metric and do not add a second interpretive chip.

Good:

- `Sell Nightclub Stock [2x]`

Avoid:

- `Sell Nightclub Stock [2x] [BEST VALUE]`

### Naming Rule

Use **Mixed by Context** language.

Use real GTA activity names when the activity is known primarily by its in-game name:

- `Payphone Hit`
- `Security Contract`
- `Cayo Perico`
- `Cluckin Bell Raid`

Use command tone when the task is operational or systemic:

- `Execute Nightclub Sale`
- `Refill Acid Lab`
- `Collect Agency Safe`
- `Claim Weekly Reward`

### Do Not Get Too Clever

Do not rename familiar GTA tasks into over-stylized business language that forces users to translate.

Avoid language like:

- `Initiate Revenue Liquidation Procedure`
- `Trigger Contract Payout`

The dashboard should feel distinctive, but immediate comprehension matters more than theatrical wording.

## Visual Grammar

The visual system must make section type obvious before the user reads detail text.

### `WEEKLY COMMAND BRIEF`

- strongest visual weight on the page
- one unified hero board
- 2x2 internal structure
- command surface, not a card deck

### `ACTION QUEUE`

- list-like and directional
- obvious sequence
- time chips visually tied to each row

### `OPERATIONS WALL`

- grouped operational clusters
- status-first scanning
- looks like a planning wall, not a data grid

### `FIELD INTEL`

- lighter surface than the operations wall
- reads like weekly intelligence notes
- label-driven rather than status-driven

### `BUY / IGNORE LEDGER`

- more deliberate and evaluative
- supports compare/commit behavior

## Content First Rule

If all theme layers are removed, including:

- pixel characters
- background scene
- decorative objects
- atmospheric styling

the page must still work completely as a dashboard.

The information architecture, section hierarchy, and content grammar must remain strong in a plain wireframe or grayscale version.

Theme is a supporting layer, never the load-bearing layer.

## Motion Rules

### Motion Purpose

Motion should make the page feel like an operations center coming online, not a pixel scene demanding attention.

Motion must reinforce hierarchy and scanning.

### Recommended Primary Motion by Section

- `WEEKLY COMMAND BRIEF` -> reveal
- `ACTION QUEUE` -> focus highlight
- `OPERATIONS WALL` -> hover separation
- `FIELD INTEL` -> underline or glow
- `BUY / IGNORE LEDGER` -> comparison emphasis

### Interaction Budget

Each section may have **one primary motion behavior only**.

Do not stack multiple competing behaviors inside a single section such as:

- hover
- pulse
- glow
- float
- scale
- slide

at the same time.

The goal is comprehension speed, not animation density.

### No Perpetual Motion on Critical Information

Critical content in:

- `WEEKLY COMMAND BRIEF`
- `ACTION QUEUE`

must remain stable and readable.

Any persistent decorative motion belongs only in secondary, non-essential layers.

## Boundary Rules

### No Information Duplication

Information should have one primary home.

- `WEEKLY COMMAND BRIEF` summarizes
- `ACTION QUEUE` sequences
- `OPERATIONS WALL` reflects status
- `FIELD INTEL` provides context
- `BUY / IGNORE LEDGER` supports decisions

Sections may reference the same concept, but they should not duplicate the same information in the same form.

Examples:

- if an item appears in `ACTION QUEUE`, it should not be restated with the same emphasis in `FIELD INTEL`
- if an operation status lives in `OPERATIONS WALL`, that same status should not be repeated as a pseudo-summary elsewhere

### Theme Boundary

This project should not drift into full game UI territory.

The direction is:

- strategy dashboard first
- themed operations center second

not:

- decorative pixel scene first
- useful dashboard second

## Rejected Directions

### Generic Card Dashboard

Rejected because it weakens the command-center identity and makes all top-level information feel equally weighted.

### Pure Data / Analytics Surface

Rejected because it loses GTA-specific character and makes the product feel interchangeable.

### Full Game UI

Rejected because it risks burying operational clarity under theme, motion, and decorative layout.

### Player-First Personal Dashboard

Rejected because the new direction is a public-facing weekly strategy brief, not a private player cockpit.

## Implementation Guidance

For implementation, treat the page in this order:

1. Build the wireframe and information hierarchy first
2. Validate that every section still works without theme
3. Add visual grammar that differentiates section types
4. Add only the minimum theme layer needed to create the GTA Weekly Operations Center feel
5. Add motion last, under the interaction budget rules

The implementation should be judged first on:

- information clarity
- section distinction
- scan speed
- decision support

and only then on atmosphere.
