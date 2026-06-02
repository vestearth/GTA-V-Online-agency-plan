# GTA Weekly Operations Center Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn `pixel-dashboard.html` into a content-first weekly operations center, while also adding the missing pixel-view link and automation status note to `dashboard.html`.

**Architecture:** Keep `dashboard.html` as the classic source-of-truth page and evolve `pixel-dashboard.html` into a themed operations surface that follows the approved information architecture: `WEEKLY COMMAND BRIEF`, `ACTION QUEUE`, `OPERATIONS WALL`, `FIELD INTEL`, and `BUY / IGNORE LEDGER`. Build the structure in tests first, implement the HTML wireframe next, then restyle `pixel-dashboard.css` so the theme supports the information hierarchy instead of carrying it.

**Tech Stack:** Static HTML, static CSS, Python `unittest`, existing dashboard content, GitHub Pages-friendly root files.

---

## File Map

- Modify: `tests/test_generate_dashboard.py` - add structure checks for `pixel-dashboard.html` and `dashboard.html`
- Modify: `dashboard.html` - add pixel-view navigation entry and automation status note
- Modify: `pixel-dashboard.html` - replace the current prototype sections with the approved operations-center information architecture
- Modify: `pixel-dashboard.css` - restyle the page around the new command brief, action queue, operations wall, field intel, and ledger

### Task 1: Lock The New Structure With Failing Tests

**Files:**
- Modify: `tests/test_generate_dashboard.py`
- Read: `dashboard.html`
- Read: `pixel-dashboard.html`

- [ ] **Step 1: Add a failing test for the classic dashboard cross-link and automation note**

Add this test near the existing markup tests:

```python
class DashboardCrossLinkMarkupTests(unittest.TestCase):
    def test_dashboard_links_to_pixel_view_and_shows_automation_note(self):
        html = Path("dashboard.html").read_text(encoding="utf-8")

        self.assertIn('href="pixel-dashboard.html#ops"', html)
        self.assertIn("Operations Center", html)
        self.assertIn("Auto update", html)
        self.assertIn("Thursday", html)
        self.assertIn("08:00", html)
        self.assertIn("Bangkok", html)
```

- [ ] **Step 2: Add a failing test for the new pixel dashboard section order**

Add this test below the existing dashboard markup tests:

```python
class PixelDashboardOperationsMarkupTests(unittest.TestCase):
    def test_pixel_dashboard_contains_operations_center_sections(self):
        html = Path("pixel-dashboard.html").read_text(encoding="utf-8")

        self.assertIn("WEEKLY COMMAND BRIEF", html)
        self.assertIn("ACTION QUEUE", html)
        self.assertIn("OPERATIONS WALL", html)
        self.assertIn("FIELD INTEL", html)
        self.assertIn("BUY / IGNORE LEDGER", html)
        self.assertIn("IGNORE THIS WEEK", html)
```

- [ ] **Step 3: Add a failing test for the command board and action queue grammar**

Add this test in the same class:

```python
    def test_pixel_dashboard_uses_command_brief_and_timed_queue_rows(self):
        html = Path("pixel-dashboard.html").read_text(encoding="utf-8")

        self.assertIn("HAPPENED", html)
        self.assertIn("TO DO", html)
        self.assertIn("BUY", html)
        self.assertIn("WHY", html)
        self.assertIn("[2x]", html)
        self.assertIn("[40% OFF]", html)
        self.assertIn("[20m]", html)
        self.assertIn("Execute Nightclub Sale", html)
```

- [ ] **Step 4: Add a failing test for operations wall / field intel / ledger content shape**

Add this test to keep the section grammar from drifting:

```python
    def test_pixel_dashboard_uses_wall_intel_and_ledger_shapes(self):
        html = Path("pixel-dashboard.html").read_text(encoding="utf-8")

        self.assertIn("Nightclub", html)
        self.assertIn("[ACTIVE]", html)
        self.assertIn("Best weekly income", html)
        self.assertIn("[BONUS]", html)
        self.assertIn("Highest passive income source", html)
        self.assertIn("[BUY]", html)
        self.assertIn("Best unlock if discounted", html)
```

- [ ] **Step 5: Run the focused tests and verify they fail first**

Run: `python -m unittest tests.test_generate_dashboard.DashboardCrossLinkMarkupTests tests.test_generate_dashboard.PixelDashboardOperationsMarkupTests -v`

Expected: `FAIL` because `dashboard.html` does not yet link to `pixel-dashboard.html#ops`, does not mention the Thursday `08:00 Bangkok` automation note, and `pixel-dashboard.html` still uses the older prototype structure.

- [ ] **Step 6: Commit the red test state**

```bash
git add tests/test_generate_dashboard.py
git commit -m "test: lock weekly operations center dashboard structure"
```

### Task 2: Add The Missing Classic Dashboard Navigation And Automation Note

**Files:**
- Modify: `dashboard.html`
- Test: `tests/test_generate_dashboard.py`

- [ ] **Step 1: Add a pixel-view navigation link in the classic dashboard header**

Inside the existing `<nav class="nav" aria-label="Dashboard sections">`, add:

```html
<a href="pixel-dashboard.html#ops">
  Operations Center
</a>
```

Place it after the existing `Assets` link so the classic page keeps its current local anchors first.

- [ ] **Step 2: Extend the provenance block with the weekly automation status**

Inside the existing `<section class="provenance" aria-label="Dashboard data source">`, add this extra line inside `.provenance-grid`:

```html
<p>
  <strong>
    Auto update:
  </strong>
  Thursday 08:00 Bangkok
</p>
```

- [ ] **Step 3: Run the targeted cross-link test and verify it passes**

Run: `python -m unittest tests.test_generate_dashboard.DashboardCrossLinkMarkupTests -v`

Expected: `PASS`

- [ ] **Step 4: Commit the classic dashboard support changes**

```bash
git add dashboard.html tests/test_generate_dashboard.py
git commit -m "feat: add operations center link and automation note"
```

### Task 3: Rebuild `pixel-dashboard.html` As A Content-First Operations Center

**Files:**
- Modify: `pixel-dashboard.html`
- Read: `docs/superpowers/specs/2026-06-02-gta-weekly-operations-center-design.md`
- Test: `tests/test_generate_dashboard.py`

- [ ] **Step 1: Replace the current hero trio with a single command-brief hero**

Replace the current top `#ops` interior structure with a semantic hero section like:

```html
<section id="ops" class="ops-brief" aria-labelledby="ops-brief-title">
  <div class="ops-brief-head">
    <p class="ops-kicker">GTA Weekly Operations Center</p>
    <h2 id="ops-brief-title">WEEKLY COMMAND BRIEF</h2>
    <p class="ops-subtitle">What happened, what to run, what to buy, and why this week matters.</p>
  </div>

  <div class="command-board" aria-label="Weekly command brief">
    <article class="command-cell">
      <p class="command-label">HAPPENED</p>
      <h3>Nightclub Sales Lead The Week</h3>
      <p class="command-chip">[2x]</p>
    </article>
    <article class="command-cell">
      <p class="command-label">TO DO</p>
      <h3>Execute Nightclub Sale</h3>
      <p class="command-chip">[2x]</p>
    </article>
    <article class="command-cell">
      <p class="command-label">BUY</p>
      <h3>Agency Upgrades</h3>
      <p class="command-chip">[40% OFF]</p>
    </article>
    <article class="command-cell">
      <p class="command-label">WHY</p>
      <h3>Nightclub Drives The Best Passive Return</h3>
      <p class="command-chip">[BEST VALUE]</p>
    </article>
  </div>

  <aside class="ignore-callout" aria-label="Ignore this week">
    <p class="command-label">IGNORE THIS WEEK</p>
    <ul>
      <li>Taxi Work</li>
      <li>Document Forgery</li>
    </ul>
  </aside>
</section>
```

- [ ] **Step 2: Add the new `ACTION QUEUE` section directly after the command brief**

Insert a section like this after `#ops`:

```html
<section class="ops-section action-queue" aria-labelledby="action-queue-title">
  <div class="ops-section-head">
    <p class="ops-kicker">Execution Order</p>
    <h2 id="action-queue-title">ACTION QUEUE</h2>
  </div>
  <ol class="queue-list">
    <li><span class="queue-task">Collect Agency Safe</span><span class="queue-chip">[2m]</span></li>
    <li><span class="queue-task">Refill Acid Lab</span><span class="queue-chip">[5m]</span></li>
    <li><span class="queue-task">Execute Nightclub Sale</span><span class="queue-chip">[20m]</span></li>
    <li><span class="queue-task">Payphone Hit</span><span class="queue-chip">[10m]</span></li>
    <li><span class="queue-task">Claim Weekly Reward</span><span class="queue-chip">[1m]</span></li>
  </ol>
</section>
```

- [ ] **Step 3: Replace the old assets section with the operations wall, field intel, and ledger**

Replace the current `#assets` block with three new sections:

```html
<section class="ops-section operations-wall" aria-labelledby="operations-wall-title">
  <div class="ops-section-head">
    <p class="ops-kicker">Operational State</p>
    <h2 id="operations-wall-title">OPERATIONS WALL</h2>
  </div>
  <div class="wall-groups">
    <article class="wall-group">
      <h3>ACTIVE</h3>
      <div class="wall-item">
        <div class="wall-item-head"><span>Nightclub</span><span class="status-chip">[ACTIVE]</span></div>
        <p>Best weekly income</p>
      </div>
      <div class="wall-item">
        <div class="wall-item-head"><span>Acid Lab</span><span class="status-chip">[READY]</span></div>
        <p>Fast resupply cycle</p>
      </div>
    </article>
    <article class="wall-group">
      <h3>OPTIONAL</h3>
      <div class="wall-item">
        <div class="wall-item-head"><span>Bunker</span><span class="status-chip">[OPTIONAL]</span></div>
        <p>Good but not priority</p>
      </div>
    </article>
    <article class="wall-group">
      <h3>IGNORE</h3>
      <div class="wall-item">
        <div class="wall-item-head"><span>Taxi Work</span><span class="status-chip">[IGNORE]</span></div>
        <p>Lower value than weekly bonuses</p>
      </div>
    </article>
  </div>
</section>

<section class="ops-section field-intel" aria-labelledby="field-intel-title">
  <div class="ops-section-head">
    <p class="ops-kicker">Weekly Context</p>
    <h2 id="field-intel-title">FIELD INTEL</h2>
  </div>
  <div class="intel-list">
    <article class="intel-item"><p class="intel-label">[BONUS]</p><h3>Nightclub Sales</h3><p>Highest passive income source</p></article>
    <article class="intel-item"><p class="intel-label">[DISCOUNT]</p><h3>Agency Upgrades</h3><p>Best value unlock this week</p></article>
    <article class="intel-item"><p class="intel-label">[PRIZE]</p><h3>Podium Vehicle</h3><p>Limited-time claim</p></article>
    <article class="intel-item"><p class="intel-label">[LIMITED]</p><h3>Special Cargo</h3><p>Bonus ends this week</p></article>
  </div>
</section>

<section class="ops-section buy-ledger" aria-labelledby="buy-ledger-title">
  <div class="ops-section-head">
    <p class="ops-kicker">Decision Support</p>
    <h2 id="buy-ledger-title">BUY / IGNORE LEDGER</h2>
  </div>
  <div class="ledger-list">
    <article class="ledger-item"><div class="ledger-head"><h3>Agency Upgrade</h3><span class="decision-chip">[BUY]</span></div><p>Best unlock if discounted</p></article>
    <article class="ledger-item"><div class="ledger-head"><h3>Benefactor Terrorbyte</h3><span class="decision-chip">[CHECK]</span></div><p>Only if not already owned and utility matters</p></article>
    <article class="ledger-item"><div class="ledger-head"><h3>Document Forgery</h3><span class="decision-chip">[IGNORE]</span></div><p>Weak value relative to this week's bonuses</p></article>
  </div>
</section>
```

- [ ] **Step 4: Run the new pixel markup tests and verify they pass**

Run: `python -m unittest tests.test_generate_dashboard.PixelDashboardOperationsMarkupTests -v`

Expected: `PASS`

- [ ] **Step 5: Commit the HTML wireframe rewrite**

```bash
git add pixel-dashboard.html tests/test_generate_dashboard.py
git commit -m "feat: rebuild pixel dashboard as operations center wireframe"
```

### Task 4: Restyle `pixel-dashboard.css` Around The New Information Hierarchy

**Files:**
- Modify: `pixel-dashboard.css`
- Read: `pixel-dashboard.html`
- Test: `tests/test_generate_dashboard.py`

- [ ] **Step 1: Replace the old three-column ops-room layout with section-based layout primitives**

Add or replace the top-level layout rules with:

```css
.pixel-shell {
  max-width: 1280px;
  width: min(100% - 32px, 1280px);
  margin: 0 auto;
  padding-bottom: 48px;
}

.ops-brief,
.ops-section {
  margin-bottom: 28px;
}

.ops-section-head,
.ops-brief-head {
  display: grid;
  gap: 8px;
  margin-bottom: 16px;
}
```

- [ ] **Step 2: Add command-board styling that reads as one board, not four cards**

Add rules like:

```css
.command-board {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0;
  border: 2px solid var(--primary);
  background: rgba(7, 12, 18, 0.9);
}

.command-cell {
  min-height: 160px;
  padding: 20px;
  border-right: 1px solid rgba(187, 243, 81, 0.22);
  border-bottom: 1px solid rgba(187, 243, 81, 0.22);
}

.command-cell:nth-child(2n) {
  border-right: 0;
}

.command-chip {
  display: inline-flex;
  padding: 4px 10px;
  border: 1px solid var(--secondary);
  font-family: ui-monospace, monospace;
  font-weight: 800;
}
```

- [ ] **Step 3: Style the queue, wall, intel, and ledger as distinct section types**

Add rules that keep each section visually distinct:

```css
.queue-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: 10px;
}

.queue-list li {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  padding: 14px 16px;
  border: 1px solid rgba(187, 243, 81, 0.18);
  background: rgba(12, 18, 28, 0.82);
}

.wall-groups {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
}

.wall-group,
.intel-item,
.ledger-item {
  border: 1px solid rgba(187, 243, 81, 0.18);
  background: rgba(12, 18, 28, 0.82);
}

.intel-list,
.ledger-list {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}
```

Keep the pixel grid, scanline treatment, and monospace accent language, but remove or demote any old scene rules that no longer support the new hierarchy.

- [ ] **Step 4: Add responsive rules that preserve content-first behavior on narrow screens**

Add a mobile breakpoint like:

```css
@media (max-width: 900px) {
  .command-board,
  .wall-groups,
  .intel-list,
  .ledger-list {
    grid-template-columns: 1fr;
  }

  .queue-list li,
  .wall-item-head,
  .ledger-head {
    flex-direction: column;
    align-items: flex-start;
  }
}
```

- [ ] **Step 5: Run the full dashboard/unit test suite and verify green**

Run: `python -m unittest tests.test_generate_dashboard tests.test_update_vehicle_prices -v`

Expected: `OK`

- [ ] **Step 6: Commit the styling pass**

```bash
git add pixel-dashboard.css pixel-dashboard.html tests/test_generate_dashboard.py
git commit -m "feat: style weekly operations center dashboard"
```

### Task 5: Verify The Final Surface Against The Spec

**Files:**
- Read: `docs/superpowers/specs/2026-06-02-gta-weekly-operations-center-design.md`
- Read: `dashboard.html`
- Read: `pixel-dashboard.html`
- Read: `pixel-dashboard.css`

- [ ] **Step 1: Run the focused classic and pixel markup tests again**

Run: `python -m unittest tests.test_generate_dashboard.DashboardCrossLinkMarkupTests tests.test_generate_dashboard.PixelDashboardOperationsMarkupTests -v`

Expected: all tests `PASS`

- [ ] **Step 2: Run the generator dry-run to confirm the classic dashboard pipeline still orients correctly**

Run: `python scripts/generate_dashboard.py --dry-run`

Expected:

- `week: 2026-W22 (weekly_planning_2026_w22.json)`
- planned updates listed for existing generator-owned regions

- [ ] **Step 3: Review the final diff for scope control**

Run: `git diff -- dashboard.html pixel-dashboard.html pixel-dashboard.css tests/test_generate_dashboard.py docs/superpowers/specs/2026-06-02-gta-weekly-operations-center-design.md`

Expected: changes only in the classic dashboard link/status note, the pixel dashboard structure, the pixel dashboard styling, and the new structure tests.

- [ ] **Step 4: Commit the verified operations center feature**

```bash
git add dashboard.html pixel-dashboard.html pixel-dashboard.css tests/test_generate_dashboard.py
git commit -m "feat: launch weekly operations center dashboard"
```
