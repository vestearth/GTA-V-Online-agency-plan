# Workflow Reference

This skill is designed around the existing repository layout and should reuse the current source material instead of duplicating it.

## Canonical Inputs

- Primary example payload: `data/schema_v2_example.json`
- Other sample payloads: `data/sample_week.json`, `data/sample_franklin_week.json`, `data/sample_tony_week.json`, `data/weekly_activity_apr2-9.json`
- Weekly capture templates: `data/weekly_activity_template.json`, `data/weekly_activity_simple_template.json`

## Core Documentation

- Framework overview: `agents/Agent.md`
- Shared prompt patterns: `agents/prompt_templates.md`
- Quick weekly capture checklist: `agents/weekly_checklist.md`
- Input helper: `agents/weekly_input_template.md`

## Prompt Entry Points

- `/.github/prompts/michael-weekly-analysis.prompt.md`
- `/.github/prompts/franklin-vehicle-analysis.prompt.md`
- `/.github/prompts/trevor-combat-value.prompt.md`
- `/.github/prompts/agent14-operations-analysis.prompt.md`
- `/.github/prompts/lamar-crew-analysis.prompt.md`
- `/.github/prompts/tony-passive-income-analysis.prompt.md`
- `/.github/prompts/ron-weekly-story.prompt.md`
- `/.github/prompts/lester-weekly-summary.prompt.md`

## Agent Documents

- Michael: `agents/npc/michael.md`
- Franklin: `agents/npc/franklin.md`
- Trevor: `agents/npc/trevor.md`
- Agent 14: `agents/npc/agent14.md`
- Lamar: `agents/npc/lamar.md`
- Tony: `agents/npc/tony.md`
- Lester: `agents/npc/lester.md`
- Ron: `agents/npc/ron.md`

## Supporting References

- Franklin reference data: `agents/docs/franklin.yaml`
- Brand schema: `agents/docs/brand.schema.yaml`
- Agent 14 benchmarks: `agents/docs/agent14-cayo.yaml`
- Tony runtime catalog: `agents/data/tony.json`

## Report Scripts

- `scripts/generate_michael_report.py`
- `scripts/generate_franklin_report.py`
- `scripts/generate_trevor_report.py`
- `scripts/generate_agent14_report.py`
- `scripts/generate_lamar_report.py`
- `scripts/generate_tony_report.py`
- `scripts/generate_ron_report.py`
- `scripts/generate_lester_report.py`

## Typical Execution Pattern

1. Pick a payload from `data/`.
2. Match the requested lens to the relevant agent document.
3. Use `agents/prompt_templates.md` for the structured-output contract.
4. If a file output is needed, run the matching generator script.
5. If the task spans multiple lenses, collect agent outputs first and reserve synthesis for Lester.