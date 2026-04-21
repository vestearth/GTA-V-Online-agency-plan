# Assistant Usage Guide (Copilot / Cursor / Codex / Gemini)

Use this page as a copy-paste promptbook to run the same workflow from different AI assistants.

## Prerequisites

1. Prepare weekly data in schema v2 format (or close to it).
2. Keep these files in scope for the assistant:
   - `src/workflows/weekly_planning.yaml`
   - `src/agents/*.yaml`
   - `src/skills/*.yaml`
   - `.github/skills/gta-weekly-planning/SKILL.md`
3. Ask the assistant to output the final result as Markdown for `reports/`.

## Universal Prompt Template

Use this baseline prompt with any assistant:

```text
Here is the new GTA Online weekly update data:
[PASTE DATA]

Please execute the workflow in `src/workflows/weekly_planning.yaml`.
Follow `.github/skills/gta-weekly-planning/SKILL.md` strictly.
Use `src/agents/*.yaml` and `src/skills/*.yaml` as the source of truth.

Execution order:
1) Run `validate_weekly_schema_lightweight` first.
2) If blocking schema issues exist, stop and report only data issues.
3) Otherwise run specialist analyses (Michael, Franklin, Trevor, Agent 14, Tony).
4) Run Lester last with `synthesize_final_report`.

Return:
- A concise executive summary
- Prioritized activity plan by payout/time efficiency
- Risks/constraints
- Suggested next actions
Format as Markdown suitable for saving under `reports/`.
```

## Assistant-Specific Notes

### GitHub Copilot

- Best in VS Code with repo opened at root.
- If context is incomplete, explicitly mention file paths in the prompt.

Suggested opener:

```text
Use repository files as context, especially:
`src/workflows/weekly_planning.yaml`, `.github/skills/gta-weekly-planning/SKILL.md`, `src/agents/*.yaml`, `src/skills/*.yaml`.
```

### Cursor

- Use Agent/Chat mode with workspace context enabled.
- Ask Cursor to cite which files it used before giving final output.

Suggested opener:

```text
Before producing the final report, list the files you used and confirm workflow order matches `src/workflows/weekly_planning.yaml`.
```

### Codex

- Keep prompts explicit and deterministic (order, stop conditions, output format).
- Paste the universal template and include the weekly JSON inline.

Suggested opener:

```text
Be deterministic: do not skip steps and do not reorder workflow nodes.
```

### Gemini

- Works best when instructions are short and structured.
- Prefer bullet-style constraints and expected output sections.

Suggested opener:

```text
Follow constraints exactly; if data is invalid, return only validation issues and required fixes.
```

## Recommended Validation Prompt (Optional)

Run this first if the weekly payload quality is uncertain:

```text
Validate this weekly payload against schema v2 expectations using `validate_weekly_schema_lightweight`.
Return:
1) blocking issues
2) non-blocking warnings
3) minimal fix suggestions
Do not run full analysis yet.
```

