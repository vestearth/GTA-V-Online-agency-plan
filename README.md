# 🎮 GTA V Multi-Agent Orchestration Framework

**A sophisticated multi-agent AI analysis system** that analyzes weekly GTA V gameplay activities through the unique perspectives of 8 distinct character agents, each with specialized analytical capabilities and authentic personality-driven insights.

---

## 📚 Documentation Structure

The framework is **fully documented in Markdown format** with dedicated files for each component:

### Framework Documentation
- **[Agent.md](agents/Agent.md)** - Master framework documentation covering:
  - 📋 Project Overview & Agent Portfolio
  - 🔐 Isolation Environment & Architecture
  - 🎯 Multi-Agent Strategy & Analysis Workflow
  - ⚠️ Error Handling & Recovery Protocols
- **[prompt_templates.md](agents/prompt_templates.md)** - Prompt templates for each agent

### Agent Documentation

#### Offline Agents (Single-player Analysis)
- **[michael.md](agents/offline/michael.md)** - Strategic & Financial Analyst
- **[franklin.md](agents/offline/franklin.md)** - Street Activity & Progression Analyst
- **[trevor.md](agents/offline/trevor.md)** - Chaos & Risk Analyst

#### Online Agents (Multiplayer Analysis)
- **[agent14.md](agents/online/agent14.md)** - Special Operations & Efficiency Analyst
- **[lamar.md](agents/online/lamar.md)** - Social & Crew Activity Analyst
- **[english_dave.md](agents/online/english_dave.md)** - Entertainment & Fun Value Analyst
- **[lester.md](agents/online/lester.md)** - Master Coordinator & Weekly Summary
- **[ron.md](agents/online/ron.md)** - Weekly Story Narrator

---

## ✨ Key Features

- **8 Specialized AI Agents** with authentic GTA V character personalities
- **Multi-dimensional Analysis**: Financial, Strategic, Social, Entertainment, Operational, Narrative
- **Isolation Architecture**: Each agent operates independently with personality-driven perspectives
- **Aggregation Engine**: Lester Crest synthesizes all analyses into comprehensive reports
- **OpenAI API Integration** (gpt-4o-mini, gpt-4o, or custom models)
- **Offline/Demo Mode** works without API credentials
- **Markdown-based Documentation** for complete framework transparency

---

## 🎮 The 8-Agent Ensemble

### Offline Agents (Campaign Analysis)
| Agent | Specialty | Perspective |
|-------|-----------|-------------|
| **Michael** | Financial & Strategy | Profit-centric, risk-aware analyst |
| **Franklin** | Progression & Growth | Goal-oriented, team-focused developer |
| **Trevor** | Entertainment & Risk | Chaos-seeking, thrill-factor evaluator |

### Online Agents (Multiplayer Analysis)
| Agent | Specialty | Perspective |
|-------|-----------|-------------|
| **Agent 14** | Operations & Efficiency | Data-driven, metrics-focused operative |
| **Lamar** | Social & Crew Dynamics | Energy-filled team cohesion expert |
| **English Dave** | Entertainment Value | Enthusiastic fun-factor analyst |
| **Ron** | Narrative & Story | Dramatic storyteller & meaning-maker |
| **Lester** | Synthesis & Coordination | Master strategist & report aggregator |

---

## � Current Project Status

This repository has been converted into a **documentation-only specification** for a multi-agent orchestration framework.

- All runtime Python files have been removed.
- The project now focuses on Markdown documentation describing each agent, architecture, and analysis workflow.
- Use the files under `agents/` for design reference and planning.

---

## 📁 Project Structure

```
GTA-V-Online-agency-plan/
├── agents/
│   ├── Agent.md                      # 📚 Framework documentation
│   ├── weekly_input_template.md      # 📝 Weekly activity input form
│   ├── offline/
│   │   ├── michael.md                # 📖 Strategic & Financial Analyst
│   │   ├── franklin.md               # 📖 Progression & Growth Analyst
│   │   ├── trevor.md                 # 📖 Chaos & Risk Analyst
│   └── online/
│       ├── agent14.md                # 📖 Operations & Efficiency Analyst
│       ├── lamar.md                  # 📖 Social & Crew Activity Analyst
│       ├── english_dave.md           # 📖 Entertainment & Fun Value Analyst
│       ├── lester.md                 # 📖 Master Coordinator & Weekly Summary
│       ├── ron.md                    # 📖 Weekly Story Narrator
├── data/
│   ├── sample_week.json              # Example weekly data structure
│   └── weekly_activity_template.json # Example input template
├── requirements.txt                  # Dependencies metadata
├── .env.example                      # Environment variables template (conceptual)
└── README.md                         # This file
```

---

## 🏗️ System Architecture

### Multi-Agent Analysis Pipeline

```
┌─────────────────────────────┐
│   Weekly Activity Data      │
│    (JSON format)            │
└────────────┬────────────────┘
             │
      ┌──────▼──────┐
      │  Validation │
      │   & Parse   │
      └──────┬──────┘
             │
   ┌─────────┼─────────┬──────────┐
   │         │         │          │
   ▼         ▼         ▼          ▼
 Michael  Franklin  Trevor   Agent14
 (Finance)(Progress)(Chaos) (Operations)
   │         │         │          │
   └────┬────┴────┬────┴────┬─────┘
        │         │         │
        ▼         ▼         ▼
      Lamar  English Dave  Ron
      (Team) (Entertainment)(Story)
        │         │         │
        └────┬────┴────┬────┘
             │         │
        ┌────▼─────────▼──┐
        │   Lester Crest  │
        │  (Aggregation)  │
        └────┬────────────┘
             │
        ┌────▼──────────────┐
        │ Final Report      │
        │ - Executive       │
        │   Summary         │
        │ - All Perspectives
        │ - Metrics         │
        │ - Recommendations │
        └───────────────────┘
```

### Isolation Model

Each agent:
- Receives identical raw weekly data
- Processes through personality-specific lens
- Generates independent analysis output
- No direct inter-agent communication
- All outputs aggregated by Lester

---

## 🎯 How It Works

### Phase 1: Data Loading
Framework loads and validates weekly activity JSON data

### Phase 2: Parallel Analysis
- **7 specialized agents** each analyze data independently
- Each applies unique analytical framework
- Each produces specialized report

### Phase 3: Aggregation
- **Lester Crest** receives all 7 reports
- Identifies consensus patterns
- Highlights divergence and trade-offs
- Produces executive summary

### Phase 4: Report Generation
- Combined report saved as Markdown
- Includes all agent perspectives
- Strategic priorities ranked
- Actionable recommendations included

---

## 📖 Agent Specializations

### Michael De Santa – Financial Analysis
- **Focus**: Profit, ROI, efficiency, financial strategy
- **Questions**: How much did we make? Is it worth it? $/hour?
- **Output**: Financial breakdown, profit assessment, strategic recommendations
- **Doc**: [michael.md](agents/offline/michael.md)

### Franklin Clinton – Progression Analysis
- **Focus**: Mission success, skill development, team dynamics, goals
- **Questions**: Did we progress? Skill gains? Goal achievement?
- **Output**: Progress metrics, crew assessment, development priorities
- **Doc**: [franklin.md](agents/offline/franklin.md)

### Trevor Philips – Risk & Entertainment Analysis
- **Focus**: Thrill factor, chaos, risk assessment, excitement
- **Questions**: Was it fun? How risky? Worth the danger?
- **Output**: Thrill ratings, risk analysis, entertainment scores
- **Doc**: [trevor.md](agents/offline/trevor.md)

### Agent 14 – Operations Analysis
- **Focus**: Mission success, operational efficiency, metrics
- **Questions**: Operationally sound? Success rate? Efficiency?
- **Output**: KPIs, tactical assessment, optimization recommendations
- **Doc**: [agent14.md](agents/online/agent14.md)

### Lamar Davis – Social & Team Analysis
- **Focus**: Crew dynamics, morale, team performance, unity
- **Questions**: How's the team? Morale? Who's MVP?
- **Output**: Team assessment, MVPs, crew recommendations
- **Doc**: [lamar.md](agents/online/lamar.md)

### English Dave – Entertainment Analysis
- **Focus**: Fun value, engagement, memorable moments, enjoyment
- **Questions**: How much fun? Entertainment rating? Highlights?
- **Output**: Fun scores, epic moments, engagement assessment
- **Doc**: [english_dave.md](agents/online/english_dave.md)

### Ron Jakowski – Narrative Analysis
- **Focus**: Story arcs, character development, dramatic moments, meaning
- **Questions**: What's the story? Character growth? Dramatic arc?
- **Output**: Narrative summary, character development, themes
- **Doc**: [ron.md](agents/online/ron.md)

### Lester Crest – Orchestration & Summary
- **Focus**: Synthesis of all perspectives, strategic priorities, executive summary
- **Questions**: What's the complete picture? What matters most?
- **Output**: Multi-perspective summary, consensus analysis, strategic priorities
- **Doc**: [lester.md](agents/online/lester.md)

---

## 🔧 Configuration Options

### Environment Variables

```bash
# OpenAI Configuration
OPENAI_API_KEY=sk-...            # Your OpenAI API key (optional)
LLM_MODEL=gpt-4o-mini           # Model to use (default: gpt-4o-mini)
LLM_TEMPERATURE=0.7             # Temperature 0-2 (default: 0.7)

# Agent Configuration
ENABLED_AGENTS=all              # Which agents to run: "all" or comma-separated
                                # e.g., "michael,franklin,lester"

# Output Configuration
REPORTS_DIR=reports/            # Where to save reports (default: reports/)
```

### Command-line Options

```bash
-h, --help              Show help message
-d, --data FILE         Path to weekly data JSON file
-o, --output DIR        Directory to save reports
--agents LIST           Comma-separated agent names to run
--offline              Force offline mode (no API calls)
--verbose              Verbose output with debugging
--no-save              Print to console, don't save files
```

---

## 📊 Output Format

Reports are generated as **Markdown files** with structure:

```markdown
# Weekly Report – [Week & Date Range]

## Executive Summary
[Overview of the week across all dimensions]

## Agent Analyses
- Michael's Financial Assessment
- Franklin's Progression Report
- Trevor's Risk & Entertainment Analysis
- Agent 14's Operational Review
- Lamar's Team Report
- English Dave's Entertainment Assessment
- Ron's Narrative Summary

## Lester's Synthesis
- Consensus Findings
- Divergence Analysis
- Strategic Priorities
- Final Recommendations

## Key Metrics & Scorecard
[Consolidated metrics across all dimensions]
```

---

## 🚨 Error Handling

The framework implements robust error handling:

- **Individual agent failures don't crash the system**
- **Failures isolated and logged**
- **Continues with remaining agents**
- **Offline mode available as fallback**
- **Detailed error logging for debugging**

See [Agent.md – Error Handling](agents/Agent.md#-error-handling) for details.

---

## 🧪 Status

This repository has been converted into a **documentation-only design specification**. There is no active Python runtime or test suite included in this version.

The Markdown files document the framework architecture, each agent's role, analysis flow, and integration concepts.

For full framework architecture, see [Agent.md](agents/Agent.md).

---

## 💡 Key Concepts

### Isolation Environment
Each agent operates in complete functional isolation, maintaining its own system/user prompts and producing independent analyses. This ensures authentic multi-perspective analysis.

### Multi-Perspective Consensus
Strong consensus (5+ agents aligned) signals high-confidence truth. Divergence reveals multi-faceted perspectives on trade-offs.

### Personality-Driven Analysis
Each agent intentionally biases analysis through character personality:
- Michael prioritizes profit
- Franklin prioritizes growth
- Trevor prioritizes thrill
- etc.

This creates authentic character perspectives that users can weight according to their own priorities.

### Aggregation & Synthesis
Lester Crest synthesizes all perspectives into balanced, actionable recommendations that honor all agent viewpoints.

---

## 📝 License

This project is part of the GTA V Online Agency Plan initiative (Community Project)

---

## 🤝 Contributions

For contributions, please:
1. Update relevant `.md` documentation files
2. Update documentation if the design changes  
3. Maintain agent personality authenticity
4. Follow project structure conventions

---

## 📚 Further Reading

- **[Agent.md](agents/Agent.md)** - Complete framework specification
- **[Michael's Analysis](agents/offline/michael.md)** - Financial framework
- **[Franklin's Analysis](agents/offline/franklin.md)** - Progression framework
- **[Trevor's Analysis](agents/offline/trevor.md)** - Entertainment framework
- **[Agent 14's Analysis](agents/online/agent14.md)** - Operations framework
- **[Lamar's Analysis](agents/online/lamar.md)** - Social framework
- **[English Dave's Analysis](agents/online/english_dave.md)** - Entertainment value
- **[Ron's Analysis](agents/online/ron.md)** - Narrative framework
- **[Lester's Analysis](agents/online/lester.md)** - Aggregation framework

---

**Framework Version**: Multi-Agent Orchestration v1.0  
**Last Updated**: 2026-04-06  
**Status**: ✅ Fully Documented with Markdown-Based Specification

---

## 🧪 Tests

```bash
pytest tests/ -v
```

---

## ⚙️ Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | *(ว่าง)* | OpenAI API key – ถ้าว่างจะใช้ Offline Mode |
| `LLM_MODEL` | `gpt-4o-mini` | OpenAI model ที่ใช้ |
| `LLM_TEMPERATURE` | `0.7` | ระดับ creativity (0–2) |
| `ENABLED_AGENTS` | `all` | Comma-separated agent slugs หรือ `all` |
| `REPORTS_DIR` | `reports` | โฟลเดอร์สำหรับบันทึกรายงาน |

---

## 📄 Sample Output

รายงานจะถูกบันทึกเป็นไฟล์ Markdown ใน `reports/` เช่น:

```
reports/report_2024-W15_20240414_120000.md
```

ประกอบด้วยการวิเคราะห์จากทุก agent ที่รัน โดยแต่ละ section จะมีสไตล์และมุมมองตามบุคลิกตัวละคร GTA V

---

## 🔧 Extending the Framework

This repository now contains **Markdown-based documentation only**. To extend the framework conceptually:

1. Create a new agent spec file under `agents/offline/` or `agents/online/`
2. Define the agent's profile, role, personality, and analytical framework
3. Document the expected output structure and example dialogue
4. Describe integration points, metrics, and use cases
5. Keep the framework design consistent with the existing agent documentation style
