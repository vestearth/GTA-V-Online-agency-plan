---
name: gta-weekly-planning
description: Analyze GTA Online weekly planning payloads and generate role-based recommendations using the repository's current workflow.
argument-hint: Provide a `data/*.json` payload path or paste a schema v2 weekly payload.
user-invocable: true
disable-model-invocation: false
---

# GTA Weekly Planning

Use this skill for GTA Online weekly analysis tasks in this repository.

## When To Use

- Analyze a `schema v2` weekly planning payload.
- Recommend which activities, vehicles, businesses, or weapons to prioritize this week.
- Generate or revise outputs for agents that exist in `src/agents/` (Michael, Franklin, Trevor, Agent 14, Tony, Lester).
- Explain or follow `src/workflows/weekly_planning.yaml`.

## Required Ground Rules

- Treat `src/workflows/weekly_planning.yaml` as the canonical orchestration logic.
- Validate schema basics before specialist analysis.
- Use only facts from provided JSON and repository references.
- If data is missing, state uncertainty explicitly instead of inventing values.
- Treat Salvage Yard robbery vehicles conservatively: do not call them claimable unless the source data explicitly says they can be kept.
- Respect readiness blockers, platform restrictions, ownership/budget constraints, and the distinction between discounted / on-display / test-ride / claimable content.
- Prefer concise Thai output unless the user asks for another language.

## Procedure

1. Identify input source.
   - Prefer a concrete payload in `data/`.
   - If the user pasted JSON, verify `schema_version: 2.0` and `schema_mode: weekly_planning`.
2. Run `validate_weekly_schema_lightweight` logic before specialist analysis.
3. Normalize activities with `normalize_featured_activities` so downstream steps can rely on `weekly_content.featured_activities` even when the payload starts with `weekly_content.events`.
4. Normalize vehicles with `normalize_vehicle_opportunities` so Franklin and downstream tooling can rely on `weekly_content.vehicle_opportunities` even when the payload starts with raw showroom or event lists.
5. Run `gate_activity_prerequisites` using `data/player_profile.json`.
   - If hard readiness blockers exist, stop and report blockers first.
6. Execute specialist lenses:
   - `Lester` -> `compare_week_over_week` for advisory change context when prior payloads are available
   - `Michael` -> `calculate_business_roi`
   - `Michael` -> `calculate_activity_loop_roi`
   - `Franklin` -> `evaluate_vehicles`
   - `Franklin` -> `evaluate_purchase_fit`
   - `Trevor` -> `evaluate_combat_value`
   - `Agent14` -> `assess_operational_readiness`
   - `Tony` -> `analyze_nightclub_feeder`
7. Synthesize via `Lester` using `synthesize_final_report`.
8. After synthesis, run post-synthesis helpers:
   - `Agent14` -> `design_weekly_route` to turn the executive plan into realistic 30m / 60m / 120m routes.
   - `Lester` -> `track_weekly_decisions` to produce advisory decision memory. Do not claim prior outcomes unless a concrete history file, previous report, or user confirmation exists.
   - `Lester` -> `validate_report_completeness` before final delivery.
9. Output a concise Master Plan with `Prioritize`, `Consider`, `Skip`, plus:
   - Time buckets: `Quick Win (30m)`, `Core Loop (1-2h)`, `Extended Session (3h+)`
   - Ordered `Action Queue`
   - `Weekly Discounts Snapshot` grouped by each discount tier (include all listed items, not only recommended picks)
   - Warnings and insufficient data
10. Save outputs under `reports/` as exactly 3 week-id files per weekly run:
   - `weekly_master_plan_<week_id>.md`
   - `weekly_master_plan_<week_id>_income_scenarios.md`
   - `event_master_plan_<week_id>.md`
   where `<week_id>` is lowercase with underscore (example: `2026_w16`).

## Repo Workflow Reference

Load [./references/workflow.md](./references/workflow.md) for canonical file map and execution order.
