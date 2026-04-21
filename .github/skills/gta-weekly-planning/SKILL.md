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
- Prefer concise Thai output unless the user asks for another language.

## Procedure

1. Identify input source.
   - Prefer a concrete payload in `data/`.
   - If the user pasted JSON, verify `schema_version: 2.0` and `schema_mode: weekly_planning`.
2. Run `validate_weekly_schema_lightweight` logic before specialist analysis.
3. Execute specialist lenses:
   - `Michael` -> `calculate_business_roi`
   - `Franklin` -> `evaluate_vehicles`
   - `Trevor` -> `evaluate_combat_value`
   - `Agent14` -> `assess_operational_readiness`
   - `Tony` -> `analyze_nightclub_feeder`
4. Synthesize via `Lester` using `synthesize_final_report`.
5. Output a concise Master Plan with `Prioritize`, `Consider`, `Skip`, plus warnings and insufficient data.

## Repo Workflow Reference

Load [./references/workflow.md](./references/workflow.md) for canonical file map and execution order.
