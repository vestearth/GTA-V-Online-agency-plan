# Weekly Planning Skills Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add five profile-aware planning skills that improve weekly purchase judgment, report QA, decision memory, week-over-week comparison, and playable route design.

**Architecture:** This repository is a YAML specification and prompt library, so implementation adds focused `src/skills/*.yaml` contracts, wires them into existing agents/workflow docs, and verifies the contract with a lightweight Ruby script. The standard weekly execution order remains intact, with new skills used as helper analysis and post-synthesis checks.

**Tech Stack:** YAML skill specs, Markdown documentation, Ruby contract verification.

---

### Task 1: Contract Test

**Files:**
- Create: `scripts/verify_weekly_planning_contract.rb`

- [x] **Step 1: Write the failing contract test**

Create a Ruby script that loads YAML files and asserts the five new skill files exist, the workflow invokes the helper skills in the expected positions, and the portable `.github` skill documents the expanded process.

- [x] **Step 2: Run test to verify it fails**

Run: `ruby scripts/verify_weekly_planning_contract.rb`

Expected: FAIL because `src/skills/evaluate_purchase_fit.yaml` does not exist yet.

### Task 2: Add Skill Specs

**Files:**
- Create: `src/skills/evaluate_purchase_fit.yaml`
- Create: `src/skills/validate_report_completeness.yaml`
- Create: `src/skills/track_weekly_decisions.yaml`
- Create: `src/skills/compare_week_over_week.yaml`
- Create: `src/skills/design_weekly_route.yaml`

- [x] **Step 1: Implement the five YAML skills**

Each skill must include `name`, `description`, `input_schema`, `execution_logic`, and `output_contract`. Guardrails must preserve uncertainty, avoid invented prices or payouts, and respect budget, ownership, platform, and readiness constraints.

- [x] **Step 2: Run contract test**

Run: `ruby scripts/verify_weekly_planning_contract.rb`

Expected: FAIL until workflow and docs reference the new skills.

### Task 3: Wire Agents And Workflow

**Files:**
- Modify: `src/workflows/weekly_planning.yaml`
- Modify: `src/agents/franklin.yaml`
- Modify: `src/agents/lester.yaml`
- Modify: `src/agents/agent14.yaml`
- Modify: `src/agency.config.yaml`

- [x] **Step 1: Extend workflow without reordering canonical gates**

Add `compare_week_over_week` after normalization, add `track_weekly_decisions` as a synthesis input helper, include `evaluate_purchase_fit` in the specialist group, and run `validate_report_completeness` after Lester synthesis. Keep schema precheck, normalizers, readiness gate, specialist group, and Lester synthesis in the same relative order.

- [x] **Step 2: Assign skills to agents**

Franklin gets `evaluate_purchase_fit`; Agent 14 gets `design_weekly_route`; Lester gets `compare_week_over_week`, `track_weekly_decisions`, and `validate_report_completeness`.

### Task 4: Document Portable Skill Usage

**Files:**
- Modify: `.github/skills/gta-weekly-planning/SKILL.md`
- Modify: `README.md`
- Modify: `docs/assistant-usage.md`

- [x] **Step 1: Update execution instructions**

Document the new helper skills while preserving the standard exactly 3 report files. State that decision memory is advisory unless a concrete history file exists.

- [x] **Step 2: Run contract test**

Run: `ruby scripts/verify_weekly_planning_contract.rb`

Expected: PASS.

### Task 5: Final Verification

**Files:**
- Verify all changed files.

- [x] **Step 1: Run focused checks**

Run:

```bash
ruby scripts/verify_weekly_planning_contract.rb
ruby -e 'require "yaml"; Dir["src/**/*.yaml"].each { |f| YAML.safe_load(File.read(f), aliases: true) }; puts "all yaml ok"'
```

Expected: both PASS.
