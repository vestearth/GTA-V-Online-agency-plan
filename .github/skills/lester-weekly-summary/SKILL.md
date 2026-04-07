---
name: lester-weekly-summary
description: 'Generate only the Lester weekly summary for this repository. Use when the user asks for a consolidated weekly summary, executive synthesis, cross-agent consensus, divergence analysis, or a Lester-only report from schema v2 data and structured specialist outputs.'
argument-hint: 'Provide a weekly JSON path and, if relevant, mention whether existing structured reports already exist.'
user-invocable: true
disable-model-invocation: false
---

# Lester Weekly Summary

Use this skill when the task is specifically to produce Lester Crest's consolidated weekly summary.

## When To Use

- The user wants only the final Lester summary.
- The task is to synthesize multiple specialist outputs into one executive view.
- The user asks for consensus, divergence, priority actions, or final weekly verdict.
- The user wants the Lester generator script run and the output explained.

## Scope

- Focus on aggregation and synthesis.
- Do not rewrite every specialist report unless the user asks.
- Prefer existing structured reports in the repository when available.

## Procedure

1. Confirm the weekly payload source.
   - Prefer a concrete file in `data/`.
   - If none is provided, use an obvious repository sample only if the user clearly wants an example run.

2. Check for specialist structured outputs.
   - Lester works best when specialist JSON outputs already exist.
   - If they do not exist, say that explicitly and either summarize from available evidence or generate prerequisite reports if the user requested file output.

3. Build the synthesis around these questions.
   - Which targets show consensus across agents?
   - Which targets show meaningful disagreement?
   - What are the top priority actions for the next session or week?
   - What warnings or data gaps limit confidence?

4. Use Lester's voice and structure.
   - Favor concise executive synthesis, not raw dump.
   - Prioritize `summary`, `top_recommendations`, `warnings`, and `insufficient_data`.
   - Then provide a short Thai explanation of the week.

5. If the user wants generated files, use the Lester script described in [./references/workflow.md](./references/workflow.md).

## References

- Lester role and output intent: [agents/npc/lester.md](../../../agents/npc/lester.md)
- Shared output contract: [agents/prompt_templates.md](../../../agents/prompt_templates.md)
- Exact repo workflow: [./references/workflow.md](./references/workflow.md)