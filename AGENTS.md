# AGENTS.md

Repository-wide guidance for AI assistants working in this project.

## Project Intent

This repository is a specification + prompt library for a GTA Online weekly planning workflow.
It is not a runtime app with a required Python/Node entrypoint.

## Canonical Sources (Use First)

- `src/workflows/weekly_planning.yaml`
- `src/agency.config.yaml`
- `src/agents/*.yaml`
- `src/skills/*.yaml`
- `.github/skills/gta-weekly-planning/SKILL.md`
- `data/examples_bundle.json` (consolidated examples)
- `data/player_profile.json`

When answering, prefer these files over assumptions.

## Required Execution Order

1. Run schema precheck first: `validate_weekly_schema_lightweight`
2. If blocking schema issues exist, stop and return data issues only
3. Run readiness gate: `gate_activity_prerequisites` with `player_profile`
4. If hard readiness blockers exist, stop and return blockers first
5. Run specialist analysis in parallel (Michael, Franklin, Trevor, Agent 14, Tony)
6. Run Lester last: `synthesize_final_report`

Do not reorder workflow nodes unless the user explicitly asks for an alternative flow.

## Lester Responsibilities

- Perform schema precheck gate at workflow start
- Synthesize specialist outputs into one executive plan
- Resolve conflicts using player budget, time, and owned assets
- Apply a shared priority score: payout/hour, reliability, and time-fit
- Output clear sections: What to Play, What to Buy, What to Ignore
- Include time buckets (30m, 1-2h, 3h+) and an ordered action queue
- Preserve uncertainty in warnings / insufficient-data notes when needed

## Output Expectations

- Keep recommendations actionable and ranked
- Call out constraints and assumptions
- Use concise Markdown suitable for saving under `reports/`
- When weekly discount data exists, include a complete discount snapshot grouped by tiers (e.g. 50% / 40% / 30%) with all listed items
- For each weekly run, generate exactly 3 week-id report files:
  1) `reports/weekly_master_plan_<week_id>.md`
  2) `reports/weekly_master_plan_<week_id>_income_scenarios.md`
  3) `reports/event_master_plan_<week_id>.md`
- In `<week_id>`, use lowercase format like `2026_w16` (convert from `2026-W16`)

## Language Policy

Follow the language of the user's latest message for prose.
Keep technical identifiers (file paths, JSON keys, agent/skill ids) in canonical form.

## Guardrails

- Do not invent hidden APIs, scripts, or env files
- Do not claim execution results without grounding in repository context
- If data quality is insufficient, report blockers before analysis
