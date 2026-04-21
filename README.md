# 🎮 GTA V Online Multi-Agent Orchestrator

**Conceptual Multi-Agent AI Framework**

A YAML-based intelligent workflow that analyzes weekly GTA V Online content through 6 specialized agent personas (Michael, Franklin, Trevor, Agent 14, Tony, Lester).

---

## 🏗️ Architecture (src/)

The project is structured as a Conceptual Multi-Agent Orchestrator (resembling LangGraph, CrewAI, AutoGen in blueprint format). Execution is **assistant-agnostic** and can be operated from modern AI coding/chat clients (for example: **GitHub Copilot, Cursor, Codex, Gemini**) via the same prompt + workflow assets.

- 📂 **`src/workflows/`**: The main execution DAGs (e.g., `weekly_planning.yaml`) tying agents and data together.
- 📂 **`src/agents/`**: Model parameters, backstories, goals, and output formats for each NPC (e.g., `michael.yaml`, `franklin.yaml`).
- 📂 **`src/skills/`**: The logical tools or schemas given to agents so they can evaluate context accurately (e.g., `calculate_business_roi.yaml`).

---

## 📁 Repository Layout

```
GTA-V-Online-agency-plan/
├── src/                                  # 🧠 The Core Orchestrator
│   ├── agency.config.yaml                # Master Manifest
│   ├── workflows/weekly_planning.yaml    # Step-by-Step execution sequence
│   ├── agents/                           # Agent definitions (Michael, Lester, etc.)
│   └── skills/                           # Agent capabilites/tools
├── data/                                 # 📥 Data Payloads
│   ├── schema_v2_example.json            # Reference payload for the week
│   └── references/                       # Lookup catalogs
│       ├── vehicle_prices.yaml           # Used by Franklin
│       ├── vehicle_gtacars_slugs.json    # Optional name→GTACars slug map for price fetch
│       ├── weapon_stats.yaml             # Used by Trevor
│       └── agent14-cayo.yaml             # Used by Agent 14
├── reports/                              # 📤 Agent outputs & Final Executive Overviews
├── docs/                                 # 📚 Templates and documentation
└── .github/skills/gta-weekly-planning/   # 🤖 Reusable skill/prompt hook (portable)
```

---

## 🎯 How to Use (Copilot / Cursor / Codex / Gemini)

There is no Python or Node.js runtime required. The intelligence lives in prompt templates and YAML specs; your chosen AI assistant acts as the Orchestrator.

1. **Bring Data:** Grab the weekly update text from the Rockstar Newswire or GTA Forums.
2. **Set Player Profile:** Update `data/player_profile.json` with your bankroll, owned assets, and time constraints.
3. **Invoke your assistant:** In your preferred client (Copilot Chat, Cursor Agent/Chat, Codex, Gemini), ask:
   > *"Here is the new GTA weekly update data... Please run `src/workflows/weekly_planning.yaml`, use `data/player_profile.json`, follow `.github/skills/gta-weekly-planning/SKILL.md`, and generate the final report in `reports/`."*
4. The assistant should read the `SKILL.md` rulebook, instantiate agents according to `src/agents/*.yaml`, apply logic from `src/skills/`, and output Lester's Final Master Plan.
5. Weekly standard output in `reports/` should contain:
   - `weekly_master_plan_<week_id>.md`
   - `weekly_master_plan_<week_id>_income_scenarios.md`
   - `event_master_plan_<week_id>.md`

Need ready-to-use prompts by platform? See `docs/assistant-usage.md`.
Repository-wide agent rules are documented in `AGENTS.md`.

---

## 📖 The Agents

| Agent | Expertise | Role in the Workflow |
|-------|-----------|----------------------|
| **Michael** | Financials | Evaluates overall ROI and highest paying activities. |
| **Franklin** | Vehicles | Reviews Prize Rides, Test Track, and Showroom discounts. |
| **Trevor** | Combat Value| Analyzes Gun Van items, weapon discounts, and free armor/ammo. |
| **Agent 14** | Logistics | Matches activities to your available time and crew size constraints. |
| **Tony** | Passive Income | Optimizes Nightclub, Bunker, and MC Businesses. |
| **Lester** | Synthesis | Takes inputs from everyone else and outputs the Executive Summary. |

## 🔄 Current Workflow (v2)

`src/workflows/weekly_planning.yaml` currently runs in this order:

1. **Schema Precheck** (`validate_weekly_schema_lightweight`)
2. **Prerequisite Gate** (`gate_activity_prerequisites` via Agent 14 + `player_profile`)
3. **Parallel Specialist Analysis** (Michael, Franklin, Trevor, Agent 14, Tony)
4. **Executive Synthesis** (Lester via `synthesize_final_report` + priority scoring + action queue)

---

## 🚗 Vehicle Price Reference Refresh

Use the helper script to sync vehicle names from the latest weekly payload into `data/references/vehicle_prices.yaml`, auto-add stripped-name aliases, and print a null-price report:

`python3 scripts/update_vehicle_prices.py`

After new rows appear with `base_price: null`, fill prices from GTACars (HTTP fetch, stdlib only):

`python3 scripts/fetch_gtacar_prices.py`

- Add unknown names by editing `data/references/vehicle_gtacars_slugs.json` (`slug_by_vehicle_name`) or set `source_url` to `https://gtacars.net/gta5/<slug>`
- `--dry-run` lists vehicles and GTACars URLs that would be fetched (no HTTP; no file write)
- `--refresh-all` re-fetches every vehicle that has a resolvable slug (use sparingly; uses `--sleep` between requests)

Optional:
- Use a specific weekly file: `python3 scripts/update_vehicle_prices.py --weekly data/weekly_planning_2026_w14.json`
- Preview only: `python3 scripts/update_vehicle_prices.py --dry-run`
- Override tiers manually: edit `data/references/vehicle_tier_overrides.json` (manual overrides win over inferred tiers)
- Add per-class race tiers: edit `data/references/vehicle_race_tiers.json` (sourced from GTACars)
- The sync script validates tier strings against `allowed_tiers` / `tier_scale` and prints warnings to stderr for bad entries

### Weekly automation

- GitHub Actions workflow: `.github/workflows/auto-update-vehicle-prices.yml`
- It runs automatically when:
  - a `data/weekly_planning_*.json` file is pushed
  - every Thursday at 03:00 UTC
  - manually via `workflow_dispatch`

### Local cron (optional)

If you also want local automation on your machine:

1. Open crontab:
   `crontab -e`
2. Add (adjust the path if needed):
   `0 10 * * 4 cd /Users/earth/Documents/GH-Games/GTA-V-Online-agency-plan && /usr/bin/python3 scripts/update_vehicle_prices.py >> /tmp/gta_vehicle_prices.log 2>&1`

---
**Last Updated**: April 21, 2026 (docs freshness rule enforced)  
**Framework Version**: Conceptual Multi-Agent Orchestration v2.0
