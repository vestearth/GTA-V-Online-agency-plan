# 🎮 GTA V Online Multi-Agent Orchestrator

**Conceptual Multi-Agent AI Framework**

A YAML-based intelligent workflow that analyzes weekly GTA V Online content through 6 specialized agent personas (Michael, Franklin, Trevor, Agent 14, Tony, Lester).

---

## 🏗️ Architecture (src/)

The project is structured as a Conceptual Multi-Agent Orchestrator (resembling LangGraph, CrewAI, AutoGen in blueprint format). Execution is currently handled natively by **GitHub Copilot** via defined Prompts and Skills.

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
│       ├── weapon_stats.yaml             # Used by Trevor
│       └── agent14-cayo.yaml             # Used by Agent 14
├── reports/                              # 📤 Agent outputs & Final Executive Overviews
├── docs/                                 # 📚 Templates and documentation
└── .github/skills/gta-weekly-planning/   # 🤖 GitHub Copilot Skill hook
```

---

## 🎯 How to Use (with GitHub Copilot)

There is no Python or Node.js runtime required. The intelligence lives in the prompt templates, and Copilot acts as the Orchestrator.

1. **Bring Data:** Grab the weekly update text from the Rockstar Newswire or GTA Forums.
2. **Invoke Copilot:** In VS Code with the GitHub Copilot Chat extension, ask:
   > *"Here is the new GTA weekly update data... Please run the `src/workflows/weekly_planning.yaml` and generate the final report in the `reports/` folder."*
3. Copilot will automatically read the `.github/skills/gta-weekly-planning/SKILL.md` rulebook, instantiate the necessary agents according to `src/agents/*.yaml`, apply the rules from `src/skills/`, and provide Lester's Final Master Plan.

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
2. **Parallel Specialist Analysis** (Michael, Franklin, Trevor, Agent 14, Tony)
3. **Executive Synthesis** (Lester via `synthesize_final_report`)

---

## 🚗 Vehicle Price Reference Refresh

Use the helper script to sync vehicle names from the latest weekly payload into `data/references/vehicle_prices.yaml`, auto-add stripped-name aliases, and print a null-price report:

`python3 scripts/update_vehicle_prices.py`

Optional:
- Use a specific weekly file: `python3 scripts/update_vehicle_prices.py --weekly data/weekly_planning_2026_w14.json`
- Preview only: `python3 scripts/update_vehicle_prices.py --dry-run`

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
**Last Updated**: April 21, 2026  
**Framework Version**: Conceptual Multi-Agent Orchestration v2.0
