# Lester Workflow Reference

Use this reference when the task is specifically about the final weekly synthesis.

## Canonical Inputs

- Weekly payload examples: `data/schema_v2_example.json`, `data/weekly_activity_apr2-9.json`
- Lester role document: `agents/npc/lester.md`
- Shared prompt contract: `agents/prompt_templates.md`
- Prompt entry point: `.github/prompts/lester-weekly-summary.prompt.md`

## Structured Report Dependency

The Lester generator expects specialist structured outputs to exist first. These normally live in the runtime structured output directory created by the report scripts.

## Generator Script

- `scripts/generate_lester_report.py`

## Practical Flow

1. Load the weekly schema v2 payload.
2. Verify whether structured specialist reports already exist.
3. If they exist, aggregate them into a final Lester summary.
4. If they do not exist, tell the user Lester's confidence is limited or generate prerequisite specialist outputs if requested.
5. Present consensus targets, divergence targets, warnings, and priority actions.