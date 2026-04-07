---
name: Lester Weekly Summary
description: 'Generate a Lester-only consolidated weekly summary from schema v2 data and available specialist outputs in this repository.'
argument-hint: 'Provide a data/*.json file path and any preference such as summarize only or run the generator script.'
agent: 'Lester Weekly Summary'
---

Generate the final Lester weekly summary for this repository.

Instructions:
- Use the provided schema v2 weekly payload as the primary source.
- Check whether specialist structured outputs already exist before claiming strong consensus.
- If the user asked for a generated report file, run the Lester generator script.
- If prerequisite specialist outputs are missing, say so explicitly and lower confidence.

Use these repository references when needed:
- [Lester role document](../../agents/npc/lester.md)
- [Shared prompt templates](../../agents/prompt_templates.md)
- [Lester skill workflow](../skills/lester-weekly-summary/references/workflow.md)

Return:

1. A compact JSON object with `agent`, `summary`, `top_recommendations`, `warnings`, and `insufficient_data`
2. A concise Thai executive summary and ranked next actions