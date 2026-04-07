---
name: gta-weekly-planning
description: 'Analyze GTA Online weekly planning payloads and generate character-based reports for this repository. Use when the user asks to review a schema v2 weekly JSON, recommend what to play this week, generate or update Michael, Franklin, Trevor, Agent 14, Lamar, Tony, Ron, or Lester outputs, validate weekly content assumptions, or run the report scripts in this project.'
argument-hint: 'Provide a data/*.json file path or paste a schema v2 weekly payload with the desired agent or output.'
user-invocable: true
disable-model-invocation: false
---

# GTA Weekly Planning

Use this skill for GTA Online weekly analysis tasks in this repository.

## When To Use

- Analyze a `schema v2` weekly planning payload.
- Recommend which activities, vehicles, businesses, or weapons to prioritize this week.
- Generate or revise agent-style outputs for Michael, Franklin, Trevor, Agent 14, Lamar, Tony, Ron, or Lester.
- Compare multiple weekly JSON files in `data/`.
- Run the repository report generators and explain the output.

## Required Ground Rules

- Treat `schema v2` as the canonical planning format.
- Use only facts present in the provided JSON or repository reference files.
- If data is missing, state that clearly instead of inventing values.
- Prefer concise Thai output unless the user asks for another language.
- When making ranked recommendations, cite relevant `id` values from the payload.

## Procedure

1. Identify the input source.
   - Prefer a concrete file in `data/`, such as `data/schema_v2_example.json`.
   - If the user pasted JSON directly, validate that it looks like `schema_version: 2.0` and `schema_mode: weekly_planning`.

2. Determine the requested lens.
   - `Michael`: money, ROI, efficiency, long-term value.
   - `Franklin`: prize ride, podium, discounts, test rides, race fit.
   - `Trevor`: weapons, gear, free claims, combat value.
   - `Agent 14`: readiness, operational bottlenecks, session planning.
   - `Lamar`: crew fit, morale, salvage targets, squad momentum.
   - `Tony`: nightclub loop, feeder businesses, passive income.
   - `Ron`: narrative framing and weekly momentum.
   - `Lester`: aggregate multiple agent outputs into a weekly summary.

3. Use the repository prompts and references.
   - Shared prompt patterns live in [agents/prompt_templates.md](../../../agents/prompt_templates.md).
   - Agent role documents live under [agents/npc](../../../agents/npc).
   - Agent-specific schema and reference files live under [agents/docs](../../../agents/docs).
   - Runtime datasets live under [agents/data](../../../agents/data).

4. Produce the response in two layers when analysis is requested.
   - First, provide a compact structured summary with `agent`, `summary`, `top_recommendations`, `warnings`, and `insufficient_data`.
   - Then provide a concise Thai explanation or report.

5. If the user wants generated report files, use the project scripts.
   - Script entry points are documented in [./references/workflow.md](./references/workflow.md).
   - Match the script to the requested agent and input JSON.

## Expected Inputs

- Weekly planning payloads in `data/*.json`
- Agent prompt documents in `agents/npc/*.md`
- Optional supporting references in `agents/docs/*.yaml`

## Output Style

- Keep conclusions recommendation-focused.
- Separate `Prioritize`, `Consider`, and `Skip` when ranking opportunities.
- Call out acquisition requirements, crew-size assumptions, and uncertainty explicitly.

## Repo Workflow Reference

Load [./references/workflow.md](./references/workflow.md) when you need the exact file map, canonical inputs, or report script entry points.