# Pixel Operations Room Theme Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the strict-core Pixel Operations Room theme guardrails from `docs/superpowers/specs/2026-06-03-pixel-operations-room-theme-design.md`.

**Architecture:** Keep `pixel-dashboard.html` static and generator-owned marker blocks intact. Add reviewable ownership metadata to major pixel sections, add CSS hierarchy tokens that make `WEEKLY COMMAND BRIEF` dominant, and add tests that reject hierarchy, motion, and visual companion regressions.

**Tech Stack:** Static HTML, CSS, Python `unittest`, marker-based pixel dashboard generator.

---

## File Map

- Modify: `tests/test_generate_dashboard.py` - add PR-guard tests for theme layer order, section ownership, visual hierarchy, motion boundaries, and visual companion boundaries
- Modify: `pixel-dashboard.html` - add `data-theme-layer`, `data-surface-owner`, and optional decorative visual companions that do not carry meaning
- Modify: `pixel-dashboard.css` - add theme-layer comments/tokens, strict hierarchy variables, motion-safe rules, and companion styling
- Modify: `scripts/generate_pixel_dashboard.py` - keep generated blocks compatible with the static ownership shell

### Task 1: Lock Theme Review Guardrails With Failing Tests

**Files:**
- Modify: `tests/test_generate_dashboard.py`
- Read: `pixel-dashboard.html`
- Read: `pixel-dashboard.css`

- [ ] **Step 1: Add failing tests for section ownership metadata**

Add this class after `PixelDashboardOperationsMarkupTests`:

```python
class PixelDashboardThemeLayerTests(unittest.TestCase):
    def test_pixel_dashboard_declares_functional_surface_ownership(self):
        html = Path("pixel-dashboard.html").read_text(encoding="utf-8")

        expected = {
            'data-surface-owner="recommendations"': "Command brief owns recommendations",
            'data-surface-owner="sequencing"': "Action queue owns sequencing",
            'data-surface-owner="operational-state"': "Operations wall owns operational state",
            'data-surface-owner="context"': "Field intel owns context",
            'data-surface-owner="decisions"': "Ledger owns decisions",
        }

        for marker, message in expected.items():
            with self.subTest(marker=marker):
                self.assertIn(marker, html, message)
```

- [ ] **Step 2: Add failing tests for theme layer order and visual hierarchy tokens**

Add these tests to the same class:

```python
    def test_pixel_css_declares_strict_theme_layer_order(self):
        css = Path("pixel-dashboard.css").read_text(encoding="utf-8")

        self.assertIn("Theme Layer Order: Information > Functional > Atmospheric > Decorative", css)
        self.assertIn("--surface-rank-command: 1", css)
        self.assertIn("--surface-rank-intel: 4", css)
        self.assertIn("--command-brief-strength", css)
        self.assertIn("--field-intel-strength", css)

    def test_command_brief_has_stronger_treatment_than_field_intel(self):
        css = Path("pixel-dashboard.css").read_text(encoding="utf-8")

        self.assertIn("border: 2px solid var(--primary)", css)
        self.assertIn("box-shadow: var(--shadow), var(--glow-primary)", css)
        self.assertIn(".field-intel {\n  --surface-strength: var(--field-intel-strength);", css)
        self.assertNotIn(".field-intel {\n  --surface-strength: var(--command-brief-strength);", css)
```

- [ ] **Step 3: Add failing tests for strict motion boundaries**

Add this test to the same class:

```python
    def test_pixel_css_forbids_motion_on_critical_information(self):
        css = Path("pixel-dashboard.css").read_text(encoding="utf-8")

        forbidden_patterns = [
            ".command-cell h3 { animation:",
            ".command-chip { animation:",
            ".queue-task { animation:",
            ".queue-chip { animation:",
            ".decision-chip { animation:",
            "marquee",
        ]

        for pattern in forbidden_patterns:
            with self.subTest(pattern=pattern):
                self.assertNotIn(pattern, css)

        self.assertIn("@media (prefers-reduced-motion: reduce)", css)
        self.assertIn("transition: none", css)
```

- [ ] **Step 4: Add failing tests for visual companion boundaries**

Add this test to the same class:

```python
    def test_visual_companions_are_decorative_and_nonsemantic(self):
        html = Path("pixel-dashboard.html").read_text(encoding="utf-8")
        css = Path("pixel-dashboard.css").read_text(encoding="utf-8")

        self.assertIn('data-theme-layer="decorative"', html)
        self.assertIn('aria-hidden="true"', html)
        self.assertIn("visual-companion", html)
        self.assertIn(".visual-companion", css)
        self.assertIn("pointer-events: none", css)
```

- [ ] **Step 5: Run the focused tests and verify they fail**

Run:

```bash
python -m unittest tests.test_generate_dashboard.PixelDashboardThemeLayerTests -v
```

Expected: `FAIL` because ownership metadata, hierarchy tokens, and decorative visual companions do not exist yet.

### Task 2: Add Ownership Metadata And Nonsemantic Visual Companions

**Files:**
- Modify: `pixel-dashboard.html`

- [ ] **Step 1: Add functional ownership metadata to the five major sections**

Update section opening tags:

```html
<section id="ops" class="ops-brief" data-theme-layer="functional" data-surface-owner="recommendations" aria-labelledby="ops-brief-title">
<section class="ops-section action-queue" data-theme-layer="functional" data-surface-owner="sequencing" aria-labelledby="action-queue-title">
<section id="assets" class="ops-section operations-wall" data-theme-layer="functional" data-surface-owner="operational-state" aria-labelledby="operations-wall-title">
<section id="intel" class="ops-section field-intel" data-theme-layer="functional" data-surface-owner="context" aria-labelledby="field-intel-title">
<section class="ops-section buy-ledger" data-theme-layer="functional" data-surface-owner="decisions" aria-labelledby="buy-ledger-title">
```

- [ ] **Step 2: Add decorative visual companions that do not carry meaning**

Add a decorative companion span inside each section heading wrapper:

```html
<span class="visual-companion visual-companion-clipboard" data-theme-layer="decorative" aria-hidden="true"></span>
<span class="visual-companion visual-companion-radio" data-theme-layer="decorative" aria-hidden="true"></span>
<span class="visual-companion visual-companion-folder" data-theme-layer="decorative" aria-hidden="true"></span>
```

Use companions only as decoration. Keep real meaning in headings, chips, labels, and copy.

- [ ] **Step 3: Run the ownership and companion tests**

Run:

```bash
python -m unittest tests.test_generate_dashboard.PixelDashboardThemeLayerTests.test_pixel_dashboard_declares_functional_surface_ownership tests.test_generate_dashboard.PixelDashboardThemeLayerTests.test_visual_companions_are_decorative_and_nonsemantic -v
```

Expected: `PASS`

### Task 3: Implement Strict CSS Theme Layer And Motion Boundaries

**Files:**
- Modify: `pixel-dashboard.css`

- [ ] **Step 1: Add theme layer order and hierarchy tokens**

Add to the top comment or `body.pixel-page` area:

```css
/*
  Theme Layer Order: Information > Functional > Atmospheric > Decorative
*/

body.pixel-page {
  --surface-rank-command: 1;
  --surface-rank-queue: 2;
  --surface-rank-wall: 3;
  --surface-rank-intel: 4;
  --surface-rank-ledger: 5;
  --command-brief-strength: 1;
  --action-queue-strength: 0.84;
  --operations-wall-strength: 0.72;
  --field-intel-strength: 0.52;
  --buy-ledger-strength: 0.62;
}
```

- [ ] **Step 2: Assign section strength variables without changing section order**

Add:

```css
.ops-brief {
  --surface-strength: var(--command-brief-strength);
}

.action-queue {
  --surface-strength: var(--action-queue-strength);
}

.operations-wall {
  --surface-strength: var(--operations-wall-strength);
}

.field-intel {
  --surface-strength: var(--field-intel-strength);
}

.buy-ledger {
  --surface-strength: var(--buy-ledger-strength);
}
```

- [ ] **Step 3: Style visual companions as decorative, noninteractive hints**

Add:

```css
.ops-section-head,
.ops-brief-head {
  position: relative;
}

.visual-companion {
  position: absolute;
  right: 0;
  top: 0;
  width: 28px;
  height: 28px;
  opacity: 0.36;
  pointer-events: none;
}

.visual-companion::before,
.visual-companion::after {
  content: "";
  position: absolute;
  inset: 0;
  border: 1px solid currentColor;
}
```

- [ ] **Step 4: Run the CSS guard tests**

Run:

```bash
python -m unittest tests.test_generate_dashboard.PixelDashboardThemeLayerTests -v
```

Expected: `PASS`

### Task 4: Verify Existing Pixel Generation Still Preserves The Shell

**Files:**
- Read: `scripts/generate_pixel_dashboard.py`
- Modify if needed: `scripts/generate_pixel_dashboard.py`
- Test: `tests/test_generate_dashboard.py`

- [ ] **Step 1: Run the pixel generator**

Run:

```bash
python scripts\generate_pixel_dashboard.py
```

Expected: generator updates only marker-owned content and preserves section ownership metadata and visual companions outside markers.

- [ ] **Step 2: Run focused pixel tests**

Run:

```bash
python -m unittest tests.test_generate_dashboard.PixelDashboardOperationsMarkupTests tests.test_generate_dashboard.PixelDashboardThemeLayerTests tests.test_generate_dashboard.PixelDashboardGeneratorRenderingTests -v
```

Expected: `OK`

### Task 5: Final Verification

**Files:**
- Read: `pixel-dashboard.html`
- Read: `pixel-dashboard.css`
- Read: `tests/test_generate_dashboard.py`

- [ ] **Step 1: Run dashboard and vehicle test suites**

Run:

```bash
python -m unittest tests.test_generate_dashboard tests.test_update_vehicle_prices -v
```

Expected: `OK`

- [ ] **Step 2: Review scoped diff**

Run:

```bash
git diff -- pixel-dashboard.html pixel-dashboard.css tests/test_generate_dashboard.py docs/superpowers/plans/2026-06-03-pixel-operations-room-theme.md
```

Expected: changes are limited to Pixel Operations Room theme guardrails and this plan.

- [ ] **Step 3: Commit implementation**

```bash
git add pixel-dashboard.html pixel-dashboard.css tests/test_generate_dashboard.py docs/superpowers/plans/2026-06-03-pixel-operations-room-theme.md
git commit -m "feat: enforce pixel operations room theme hierarchy"
```
