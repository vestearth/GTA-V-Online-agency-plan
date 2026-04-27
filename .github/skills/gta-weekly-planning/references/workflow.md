# Workflow Reference

This file maps the repository's current, existing assets only.

This reference is assistant-agnostic and can be used from Copilot, Cursor, Codex, or Gemini as long as the assistant can read repository files and follow YAML/Markdown instructions.

## Canonical Inputs

-- Primary schema example: `data/examples_bundle.json` (key: `schema_v2_example`)
-- Player profile baseline: `data/player_profile.json`
-- Weekly samples: `data/weekly_planning_2026_w14.json`, `data/weekly_planning_2026_w15.json`, `data/examples_bundle.json` (key: `sample_week`)
-- Capture templates: `data/examples_bundle.json` (keys: `weekly_activity_template`, `weekly_activity_simple_template`)

## Orchestration Sources

- Master manifest: `src/agency.config.yaml`
- Workflow DAG: `src/workflows/weekly_planning.yaml`
- Agent definitions: `src/agents/*.yaml`
- Skill definitions: `src/skills/*.yaml`

## Current Agent Coverage

- Michael: ROI and money efficiency
- Franklin: vehicles and acquisition value
- Trevor: combat value, Gun Van discounts, and weapon utility
- Agent 14: operational readiness and session constraints
- Tony: passive-income and Nightclub feeder loop
- Lester: final synthesis

## Skill Mapping

- `validate_weekly_schema_lightweight`: required keys and critical null checks
- `gate_activity_prerequisites`: strict readiness gate (assets, crew fit, time fit)
- `calculate_business_roi`: ROI and profit-per-hour normalization
- `evaluate_vehicles`: vehicle pricing/discount and effort-vs-value analysis
- `evaluate_combat_value`: weapon discount and combat utility analysis
- `assess_operational_readiness`: requirements, party-size, and timebox fit
- `analyze_nightclub_feeder`: passive-business readiness and technician guidance
- `synthesize_final_report`: resolve trade-offs and produce final weekly plan
- `synthesize_final_report`: includes priority scoring, time buckets, and action queue

## Typical Execution Pattern

1. Pick one payload from `data/`.
2. Load/update `data/player_profile.json` (budget, assets, constraints).
3. Run schema precheck and stop if blocking errors exist.
4. Run prerequisite gate and stop if hard readiness blockers exist.
5. Run specialist analyses in parallel.
6. Aggregate recommendations with Lester.
7. Save or present the weekly Master Plan in Markdown.
