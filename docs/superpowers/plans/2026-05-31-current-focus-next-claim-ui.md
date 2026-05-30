# Current Focus / Next Claim UI Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the first two summary-card slots with `Current Focus` and `Next Claim / Buy`, while keeping the dashboard static and ready for future generator ownership through body-only markers.

**Architecture:** Update the existing `summary_cards` markup in `dashboard.html` so the first two cards become `Current Focus` and `Next Claim / Buy`, each with explicit body-only markers. Keep styling changes minimal and update `docs/dashboard-data-map.md` so the new summary-card placement and generator targets are documented.

**Tech Stack:** Static HTML/CSS, light Python test coverage, existing dashboard tokens and summary-grid conventions, documentation in Markdown.

---

## File Map

- Modify: `dashboard.html` - replace the first two summary cards and add body-only generator markers
- Modify: `styles.css` - only adjust styles if the existing summary-card treatment needs light tuning
- Modify: `docs/dashboard-data-map.md` - map `Current Focus` and `Next Claim / Buy` to the summary-card placement
- Modify: `tests/test_generate_dashboard.py` - verify the nested markers live in summary cards

### Task 1: Add the Failing Structure Checks First

**Files:**
- Modify: `tests/test_generate_dashboard.py`
- Read: `dashboard.html`

- [ ] **Step 1: Add a structure test for the summary-card markers**

Add a small HTML structure test that reads the current `dashboard.html` and checks for the future marker shape:

```python
class DashboardFocusRowMarkupTests(unittest.TestCase):
    def test_dashboard_contains_summary_card_markers_for_focus_content(self):
        html = Path("dashboard.html").read_text(encoding="utf-8")

        self.assertIn('class="grid summary-grid"', html)
        self.assertNotIn('class="grid focus-row"', html)
        self.assertIn("<!-- START: current_focus -->", html)
        self.assertIn("<!-- END: current_focus -->", html)
        self.assertIn("<!-- START: next_claim_buy -->", html)
        self.assertIn("<!-- END: next_claim_buy -->", html)
```

- [ ] **Step 2: Run the focused test to verify it fails before markup exists**

Run: `python -m unittest tests.test_generate_dashboard.DashboardFocusRowMarkupTests -v`

Expected: FAIL because the summary-card markers do not exist yet.

### Task 2: Update the Summary Cards Markup

**Files:**
- Modify: `dashboard.html`
- Read: `docs/superpowers/specs/2026-05-31-current-focus-next-claim-ui-design.md`

- [ ] **Step 1: Replace the first two summary cards**

Inside the `summary_cards` block, replace the first two cards so they become:

```html
<article class="card">
  <div>
    <p class="label">Current Focus</p>
    <!-- START: current_focus -->
    <p class="value text">Money Fronts 4x loop</p>
    <p class="card-note">
      Run legal missions first, then rotate into laundering for the strongest active ROI this week.
    </p>
    <!-- END: current_focus -->
  </div>
</article>
<article class="card">
  <div>
    <p class="label">Next Claim / Buy</p>
    <!-- START: next_claim_buy -->
    <p class="value text">Claim Higgins Helitours</p>
    <p class="card-note">
      Free this week and directly relevant to the Money Fronts network before considering optional purchases.
    </p>
    <!-- END: next_claim_buy -->
  </div>
</article>
```

- [ ] **Step 2: Verify markers wrap only card body content**

Re-open the inserted snippet and confirm:
- the `label` lines are outside the markers
- only the actionable content (`value text` + `card-note`) is inside the markers
- the outer `summary-grid` section has no markers wrapped around it

- [ ] **Step 3: Confirm placement with a grep check**

Run: `rg -n "summary-grid|current_focus|next_claim_buy" dashboard.html`

Expected: matches for the `summary-grid` block and the four marker comments inside the first two cards.

### Task 3: Adjust Styling Only If Needed

**Files:**
- Modify: `styles.css`

- [ ] **Step 1: Check whether the existing summary-card styles already fit the new content**

If the new cards already read well, do not add unnecessary CSS.

- [ ] **Step 2: If needed, make only minimal CSS changes**

Check that any change:
- uses existing tokens like `var(--secondary)` and `card-note`
- does not introduce a new shadow system or decorative container treatment
- keeps the summary-grid rhythm intact

### Task 4: Update the Data Map

**Files:**
- Modify: `docs/dashboard-data-map.md`

- [ ] **Step 1: Update the `Current Focus` row**

Change the row so it reflects the new summary-card placement and future generator target:

```md
| Current Focus | latest `data/weekly_planning_*.json` plus `reports/weekly_master_plan_<week_id>.md` | Summary card slot. Generated via the nested `current_focus` marker inside `summary_cards`. |
```

- [ ] **Step 2: Update the `Next Claim / Buy` row**

Change the row so it reflects the new summary-card placement and future generator target:

```md
| Next Claim / Buy | `reports/weekly_master_plan_<week_id>.md` and `reports/event_master_plan_<week_id>.md` | Summary card slot. Generated via the nested `next_claim_buy` marker inside `summary_cards`. |
```

- [ ] **Step 3: Add a modeling note**

Add a bullet like:

```md
- `Current Focus` and `Next Claim / Buy` now occupy the first two summary-card slots instead of a separate row.
```

### Task 5: Verify the UI Change End to End

**Files:**
- Read: `dashboard.html`
- Read: `styles.css`
- Read: `docs/dashboard-data-map.md`

- [ ] **Step 1: Re-run the structure test**

Run: `python -m unittest tests.test_generate_dashboard.DashboardFocusRowMarkupTests -v`

Expected: PASS

- [ ] **Step 2: Run the full dashboard-related test suite**

Run: `python -m unittest tests.test_generate_dashboard tests.test_update_vehicle_prices -v`

Expected: PASS

- [ ] **Step 3: Inspect the relevant diff**

Run: `git diff -- dashboard.html styles.css docs/dashboard-data-map.md tests/test_generate_dashboard.py`

Expected:
- the first two summary cards now represent `Current Focus` and `Next Claim / Buy`
- body-only markers wrap the generated content for both cards
- CSS changes are absent or minimal
- data map reflects the new placement

- [ ] **Step 4: Review the page visually in the in-app browser**

Use the current `file:///C:/Code/GTA-V-Online-agency-plan/dashboard.html` tab and confirm:
- the first two summary cards read cleanly as `Current Focus` and `Next Claim / Buy`
- text fits without overlap
- the summary grid still feels balanced
