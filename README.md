# 🎮 GTA V Online Multi-Agent Orchestrator

**Conceptual Multi-Agent AI Framework** 

A YAML-based intelligent workflow that analyzes weekly GTA V Online content through the perspectives of 10 specialized agent personas (Michael, Franklin, Trevor, Tony, Agent 14, etc.).

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
│   └── references/                       # Lookup catalogs (e.g., vehicle stats, nightclub data)
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
| **Trevor** | Combat | Analyzes weapon discounts and combat vehicles. |
| **Agent 14** | Logistics | Matches activities to your available time and crew size constraints. |
| **Tony** | Passive Income | Optimizes Nightclub, Bunker, and MC Businesses. |
| **Lester** | Synthesis | Takes inputs from everyone else and outputs the Executive Summary. |
| **Pavel & Vincent** | Data Integrity | Ingest raw news and format into `schema_v2` JSON. |

---
**Last Updated**: April 2026  
**Framework Version**: Conceptual Multi-Agent Orchestration v2.0
