# Bilingual Dashboard Toggle Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a shared `EN / TH` language toggle to `dashboard.html` and `pixel-dashboard.html`, with remembered preference, bilingual generated content, and universal untranslated chips.

**Architecture:** Keep both dashboards as static HTML pages backed by marker-based Python generators. Add one shared client script that sets the active language on the root element and persists the choice in `localStorage`, then update both generators to emit bilingual markup inside their owned blocks. Toggle behavior, visibility rules, and chips must stay consistent across both pages.

**Tech Stack:** Static HTML, static CSS, small vanilla JavaScript, Python `unittest`, marker-based dashboard generators, GitHub Pages-friendly root files.

---

## File Map

- Create: `dashboard-language.js` - shared client script that applies `EN / TH`, updates `aria-pressed`, and persists the language preference
- Modify: `dashboard.html` - add shared toggle control, wire in the shared script, and prepare static non-generated copy for bilingual rendering
- Modify: `pixel-dashboard.html` - add shared toggle control, wire in the shared script, and prepare static non-generated copy for bilingual rendering
- Modify: `styles.css` - add shared language-toggle styles and generic `[data-lang]` visibility rules for the classic dashboard
- Modify: `pixel-dashboard.css` - add or reuse shared toggle styles where the pixel page needs page-specific placement polish
- Modify: `scripts/generate_dashboard.py` - render bilingual markup for all generator-owned classic dashboard blocks
- Modify: `scripts/generate_pixel_dashboard.py` - render bilingual markup for all pixel markers while keeping chips universal
- Modify: `tests/test_generate_dashboard.py` - add failing tests for toggle markup, bilingual generator output, and universal chip behavior

### Task 1: Lock The Bilingual Toggle Shape With Failing Tests

**Files:**
- Modify: `tests/test_generate_dashboard.py`
- Read: `dashboard.html`
- Read: `pixel-dashboard.html`

- [ ] **Step 1: Add a failing test for the shared toggle markup on the classic dashboard**

Add this test near the existing classic dashboard markup checks:

```python
class DashboardLanguageToggleMarkupTests(unittest.TestCase):
    def test_dashboard_contains_shared_language_toggle(self):
        html = Path("dashboard.html").read_text(encoding="utf-8")

        self.assertIn('class="language-toggle"', html)
        self.assertIn('data-set-language="en"', html)
        self.assertIn('data-set-language="th"', html)
        self.assertIn("dashboard-language.js", html)
```

- [ ] **Step 2: Add a failing test for the shared toggle markup on the pixel dashboard**

Add this test near the existing pixel dashboard markup checks:

```python
class PixelDashboardLanguageToggleMarkupTests(unittest.TestCase):
    def test_pixel_dashboard_contains_shared_language_toggle(self):
        html = Path("pixel-dashboard.html").read_text(encoding="utf-8")

        self.assertIn('class="language-toggle"', html)
        self.assertIn('data-set-language="en"', html)
        self.assertIn('data-set-language="th"', html)
        self.assertIn("dashboard-language.js", html)
```

- [ ] **Step 3: Add a failing test for bilingual classic generator output**

Add a focused rendering test:

```python
class DashboardBilingualRenderingTests(unittest.TestCase):
    def test_render_header_meta_outputs_en_and_th_variants(self):
        weekly_payload = json.loads(Path("data/weekly_planning_2026_w22.json").read_text(encoding="utf-8"))
        player_profile = json.loads(Path("data/player_profile.json").read_text(encoding="utf-8"))
        vehicle_prices = load_vehicle_price_reference(Path("data/references/vehicle_prices.yaml"))
        context = build_phase1_context(weekly_payload, player_profile, vehicle_prices)

        html = render_header_meta(context)

        self.assertIn('data-lang="en"', html)
        self.assertIn('data-lang="th"', html)
        self.assertIn("Week 2026-W22", html)
        self.assertIn("สัปดาห์ 2026-W22", html)
```

- [ ] **Step 4: Add a failing test for bilingual pixel generator output with universal chips**

Add a focused pixel rendering test:

```python
class PixelDashboardBilingualRenderingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.weekly_payload = json.loads(
            Path("data/weekly_planning_2026_w22.json").read_text(encoding="utf-8")
        )
        cls.player_profile = json.loads(
            Path("data/player_profile.json").read_text(encoding="utf-8")
        )
        cls.weekly_report_text = Path("reports/weekly_master_plan_2026_w22.md").read_text(
            encoding="utf-8"
        )

    def test_render_pixel_command_brief_outputs_bilingual_copy_and_universal_chips(self):
        html = render_pixel_command_brief(self.weekly_payload, self.weekly_report_text)

        self.assertIn('data-lang="en"', html)
        self.assertIn('data-lang="th"', html)
        self.assertIn("[4x]", html)
        self.assertNotIn("[ซื้อ]", html)
        self.assertNotIn("[ลำดับความสำคัญ]", html)
```

- [ ] **Step 5: Add a failing test for universal chip behavior in ledger output**

Add this test next to the pixel bilingual rendering tests:

```python
    def test_render_pixel_buy_ledger_keeps_chips_untranslated(self):
        html = render_pixel_buy_ledger(self.weekly_report_text)

        self.assertIn("[BUY]", html)
        self.assertIn("[HOLD]", html)
        self.assertIn("[IGNORE]", html)
        self.assertNotIn("[ซื้อ]", html)
        self.assertNotIn("[ข้าม]", html)
```

- [ ] **Step 6: Run the focused tests and verify they fail first**

Run: `python -m unittest tests.test_generate_dashboard.DashboardLanguageToggleMarkupTests tests.test_generate_dashboard.PixelDashboardLanguageToggleMarkupTests tests.test_generate_dashboard.DashboardBilingualRenderingTests tests.test_generate_dashboard.PixelDashboardBilingualRenderingTests -v`

Expected: `FAIL` because neither HTML page contains a shared toggle yet and both generators still render single-language blocks.

- [ ] **Step 7: Commit the red test state**

```bash
git add tests/test_generate_dashboard.py
git commit -m "test: lock bilingual dashboard toggle behavior"
```

### Task 2: Add The Shared Language Toggle Script

**Files:**
- Create: `dashboard-language.js`

- [ ] **Step 1: Write a failing script-level behavior test inside the existing unittest file**

Add a small static-file test that locks the intended script API:

```python
class DashboardLanguageScriptMarkupTests(unittest.TestCase):
    def test_language_script_contains_shared_storage_key_and_root_attribute(self):
        script = Path("dashboard-language.js").read_text(encoding="utf-8")

        self.assertIn("gta-dashboard-language", script)
        self.assertIn("data-ui-language", script)
        self.assertIn("aria-pressed", script)
        self.assertIn("localStorage", script)
```

- [ ] **Step 2: Run the script test to verify it fails**

Run: `python -m unittest tests.test_generate_dashboard.DashboardLanguageScriptMarkupTests -v`

Expected: `ERROR` or `FAIL` because `dashboard-language.js` does not exist yet.

- [ ] **Step 3: Create the shared script with the minimal language-toggle behavior**

Create `dashboard-language.js` with:

```javascript
(() => {
  const STORAGE_KEY = "gta-dashboard-language";
  const root = document.documentElement;
  const buttons = Array.from(document.querySelectorAll("[data-set-language]"));

  function normalizeLanguage(value) {
    return value === "th" ? "th" : "en";
  }

  function setLanguage(value) {
    const language = normalizeLanguage(value);
    root.lang = language;
    root.setAttribute("data-ui-language", language);
    for (const button of buttons) {
      const active = button.getAttribute("data-set-language") === language;
      button.setAttribute("aria-pressed", active ? "true" : "false");
    }
    try {
      window.localStorage.setItem(STORAGE_KEY, language);
    } catch (_error) {
      // Best effort only.
    }
  }

  let initial = "en";
  try {
    initial = normalizeLanguage(window.localStorage.getItem(STORAGE_KEY));
  } catch (_error) {
    initial = "en";
  }

  for (const button of buttons) {
    button.addEventListener("click", () => {
      setLanguage(button.getAttribute("data-set-language"));
    });
  }

  setLanguage(initial);
})();
```

- [ ] **Step 4: Run the script test to verify it passes**

Run: `python -m unittest tests.test_generate_dashboard.DashboardLanguageScriptMarkupTests -v`

Expected: `PASS`

- [ ] **Step 5: Commit the shared script**

```bash
git add dashboard-language.js tests/test_generate_dashboard.py
git commit -m "feat: add shared dashboard language toggle script"
```

### Task 3: Wire The Shared Toggle Into Both Dashboard Shells

**Files:**
- Modify: `dashboard.html`
- Modify: `pixel-dashboard.html`
- Modify: `styles.css`
- Modify: `pixel-dashboard.css`
- Test: `tests/test_generate_dashboard.py`

- [ ] **Step 1: Add the shared toggle markup to the classic dashboard header**

Add this control in the top metadata/navigation area of `dashboard.html`:

```html
<div class="language-toggle" role="group" aria-label="Language">
  <button type="button" data-set-language="en" aria-pressed="true">EN</button>
  <button type="button" data-set-language="th" aria-pressed="false">TH</button>
</div>
```

- [ ] **Step 2: Add the same shared toggle markup to the pixel dashboard header**

Add the identical control in the top metadata/navigation area of `pixel-dashboard.html` so both pages present the same toggle shape.

- [ ] **Step 3: Include the shared script at the end of both HTML files**

Append this tag before `</body>` in both pages:

```html
<script src="dashboard-language.js"></script>
```

- [ ] **Step 4: Add shared visibility rules and toggle styles to `styles.css`**

Add a compact shared block such as:

```css
:root[data-ui-language="en"] [data-lang="th"] {
  display: none;
}

:root[data-ui-language="th"] [data-lang="en"] {
  display: none;
}

.language-toggle {
  display: inline-flex;
  gap: 0.25rem;
  padding: 0.25rem;
  border: 1px solid rgba(255, 255, 255, 0.14);
  border-radius: 999px;
}

.language-toggle button[aria-pressed="true"] {
  background: rgba(255, 255, 255, 0.16);
}
```

- [ ] **Step 5: Add any pixel-specific placement polish to `pixel-dashboard.css`**

If the pixel header needs local adjustments, add only layout overrides such as:

```css
.pixel-header .language-toggle {
  align-self: flex-start;
}
```

- [ ] **Step 6: Run the toggle markup tests and verify they pass**

Run: `python -m unittest tests.test_generate_dashboard.DashboardLanguageToggleMarkupTests tests.test_generate_dashboard.PixelDashboardLanguageToggleMarkupTests -v`

Expected: `PASS`

- [ ] **Step 7: Commit the shell wiring**

```bash
git add dashboard.html pixel-dashboard.html styles.css pixel-dashboard.css tests/test_generate_dashboard.py dashboard-language.js
git commit -m "feat: add shared dashboard language toggle shell"
```

### Task 4: Make The Classic Dashboard Generator Render Bilingual Blocks

**Files:**
- Modify: `scripts/generate_dashboard.py`
- Test: `tests/test_generate_dashboard.py`

- [ ] **Step 1: Add a tiny helper for paired language spans**

Add a helper near the existing formatting/render helpers:

```python
def render_bilingual_text(tag: str, english: str, thai: str, attrs: str = "") -> str:
    attr_suffix = f" {attrs}" if attrs else ""
    return (
        f"<{tag}{attr_suffix}><span data-lang=\"en\">{html.escape(english)}</span>"
        f"<span data-lang=\"th\">{html.escape(thai)}</span></{tag}>"
    )
```

- [ ] **Step 2: Update `render_header_meta` to output bilingual markup**

Replace single-language lines with bilingual variants, for example:

```python
render_bilingual_text("p", f"Week {context['week_id']}", f"สัปดาห์ {context['week_id']}")
```

Keep factual values identical across languages.

- [ ] **Step 3: Update one Phase 1 block at a time and run focused tests after each**

Convert these renderer outputs to bilingual markup in this order:

1. `render_data_status_note`
2. `render_summary_cards`
3. `render_weekly_deals`
4. `render_weekly_vehicle_spotlight`

Do not translate chips such as `Free`, `Check source`, or value chips if they already act as universal visual tokens for the block.

- [ ] **Step 4: Update the Phase 2 classic renderers to bilingual output**

Convert these functions:

1. `render_current_focus`
2. `render_next_claim_buy`
3. `render_weekly_action_plan`
4. `render_what_to_buy_ignore`
5. `render_asset_overview`

For `render_what_to_buy_ignore` and `render_asset_overview`, keep ruling/status chips universal while localizing the explanatory text and column labels.

- [ ] **Step 5: Run the focused classic bilingual tests**

Run: `python -m unittest tests.test_generate_dashboard.DashboardBilingualRenderingTests tests.test_generate_dashboard.DashboardGeneratorRenderingTests tests.test_generate_dashboard.DashboardGeneratorPhase2RenderingTests -v`

Expected: `PASS`

- [ ] **Step 6: Commit the classic bilingual generator changes**

```bash
git add scripts/generate_dashboard.py tests/test_generate_dashboard.py
git commit -m "feat: render bilingual classic dashboard blocks"
```

### Task 5: Make The Pixel Dashboard Generator Render Bilingual Blocks

**Files:**
- Modify: `scripts/generate_pixel_dashboard.py`
- Test: `tests/test_generate_dashboard.py`

- [ ] **Step 1: Add a small shared helper for bilingual inline content**

Inside `scripts/generate_pixel_dashboard.py`, add a helper similar to:

```python
def render_bilingual_html(tag: str, english: str, thai: str, attrs: str = "") -> str:
    attr_suffix = f" {attrs}" if attrs else ""
    return (
        f"<{tag}{attr_suffix}><span data-lang=\"en\">{html.escape(english)}</span>"
        f"<span data-lang=\"th\">{html.escape(thai)}</span></{tag}>"
    )
```

- [ ] **Step 2: Convert `render_pixel_header_meta` and `render_pixel_command_brief` first**

Make the visible text bilingual while keeping chips untouched, for example:

```python
render_bilingual_html("p", "Strategy Snapshot", "ภาพรวมแผนประจำสัปดาห์")
```

and keep:

```python
f'<p class="command-chip">[4x]</p>'
```

- [ ] **Step 3: Convert the remaining pixel sections one block at a time**

Update these functions:

1. `render_pixel_ignore_callout`
2. `render_pixel_action_queue`
3. `render_pixel_operations_wall`
4. `render_pixel_field_intel`
5. `render_pixel_buy_ledger`

Rules:

- localize labels, headings, and body copy
- keep chips universal
- keep the same information architecture and section responsibilities

- [ ] **Step 4: Run the pixel generator to rewrite `pixel-dashboard.html`**

Run: `python scripts\generate_pixel_dashboard.py`

Expected: `updated pixel dashboard: C:\Code\GTA-V-Online-agency-plan\pixel-dashboard.html`

- [ ] **Step 5: Run the focused pixel bilingual tests**

Run: `python -m unittest tests.test_generate_dashboard.PixelDashboardBilingualRenderingTests tests.test_generate_dashboard.PixelDashboardGeneratorRenderingTests tests.test_generate_dashboard.PixelDashboardOperationsMarkupTests -v`

Expected: `PASS`

- [ ] **Step 6: Commit the pixel bilingual generator changes**

```bash
git add scripts/generate_pixel_dashboard.py pixel-dashboard.html tests/test_generate_dashboard.py
git commit -m "feat: render bilingual pixel dashboard blocks"
```

### Task 6: Convert The Remaining Static Shell Copy To Bilingual Markup

**Files:**
- Modify: `dashboard.html`
- Modify: `pixel-dashboard.html`
- Test: `tests/test_generate_dashboard.py`

- [ ] **Step 1: Add bilingual static markup to the classic shell around non-generated labels**

Convert non-generated classic shell copy such as navigation labels, section titles outside marker ownership, and any manual helper text using:

```html
<span data-lang="en">Classic View</span>
<span data-lang="th">มุมมองคลาสสิก</span>
```

- [ ] **Step 2: Add bilingual static markup to the pixel shell around non-generated labels**

Convert shell copy such as:

- eyebrow
- `Weekly Operations Center`
- subtitle
- local nav labels
- section kickers

Keep chips and short symbolic labels universal where required by the spec.

- [ ] **Step 3: Run the markup tests again**

Run: `python -m unittest tests.test_generate_dashboard.DashboardLanguageToggleMarkupTests tests.test_generate_dashboard.PixelDashboardLanguageToggleMarkupTests tests.test_generate_dashboard.PixelDashboardOperationsMarkupTests -v`

Expected: `PASS`

- [ ] **Step 4: Commit the shell localization pass**

```bash
git add dashboard.html pixel-dashboard.html tests/test_generate_dashboard.py
git commit -m "feat: localize static dashboard shell copy"
```

### Task 7: Final Verification And Review

**Files:**
- Read: `dashboard.html`
- Read: `pixel-dashboard.html`
- Read: `dashboard-language.js`
- Read: `scripts/generate_dashboard.py`
- Read: `scripts/generate_pixel_dashboard.py`

- [ ] **Step 1: Run the full dashboard and vehicle test suite**

Run: `python -m unittest tests.test_generate_dashboard tests.test_update_vehicle_prices -v`

Expected: `OK`

- [ ] **Step 2: Regenerate the pixel dashboard one more time to ensure committed output matches generator behavior**

Run: `python scripts\generate_pixel_dashboard.py`

Expected: `updated pixel dashboard: C:\Code\GTA-V-Online-agency-plan\pixel-dashboard.html`

- [ ] **Step 3: Review the diff for the intended file set**

Run: `git diff -- dashboard.html pixel-dashboard.html styles.css pixel-dashboard.css dashboard-language.js scripts/generate_dashboard.py scripts/generate_pixel_dashboard.py tests/test_generate_dashboard.py`

Expected: changes only in the bilingual toggle feature scope

- [ ] **Step 4: Manual browser spot check**

Open both:

- `file:///C:/Code/GTA-V-Online-agency-plan/dashboard.html`
- `file:///C:/Code/GTA-V-Online-agency-plan/pixel-dashboard.html`

Verify:

1. `EN / TH` toggle is visible on both pages
2. the active language persists when moving between the two pages
3. chips remain universal in both languages
4. no section becomes unreadable when Thai is active

- [ ] **Step 5: Stage the final bilingual toggle work**

```bash
git add dashboard.html pixel-dashboard.html styles.css pixel-dashboard.css dashboard-language.js scripts/generate_dashboard.py scripts/generate_pixel_dashboard.py tests/test_generate_dashboard.py docs/superpowers/specs/2026-06-03-bilingual-dashboard-toggle-design.md docs/superpowers/plans/2026-06-03-bilingual-dashboard-toggle.md
```
