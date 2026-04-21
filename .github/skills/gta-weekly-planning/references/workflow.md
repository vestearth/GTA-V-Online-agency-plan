# Workflow Reference

This file maps the repository's current, existing assets only.

## Canonical Inputs

- Primary schema example: `data/schema_v2_example.json`
- Weekly samples: `data/weekly_planning_2026_w14.json`, `data/weekly_planning_2026_w15.json`, `data/sample_week.json`
- Capture templates: `data/weekly_activity_template.json`, `data/weekly_activity_simple_template.json`

## Orchestration Sources

- Master manifest: `src/agency.config.yaml`
- Workflow DAG: `src/workflows/weekly_planning.yaml`
- Agent definitions: `src/agents/*.yaml`
- Skill definitions: `src/skills/*.yaml`

## Current Agent Coverage

- Michael: ROI and money efficiency
- Franklin: vehicles and acquisition value
- Agent 14: operational readiness and session constraints
- Tony: passive-income and Nightclub feeder loop
- Lester: final synthesis

## Skill Mapping

- `validate_weekly_schema_lightweight`: required keys and critical null checks
- `calculate_business_roi`: ROI and profit-per-hour normalization
- `evaluate_vehicles`: vehicle pricing/discount and effort-vs-value analysis
- `assess_operational_readiness`: requirements, party-size, and timebox fit
- `analyze_nightclub_feeder`: passive-business readiness and technician guidance
- `synthesize_final_report`: resolve trade-offs and produce final weekly plan

## Typical Execution Pattern

1. Pick one payload from `data/`.
2. Run schema precheck and stop if blocking errors exist.
3. Run specialist analyses in parallel.
4. Aggregate recommendations with Lester.
5. Save or present the weekly Master Plan in Markdown.
