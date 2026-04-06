# Multi-Agent Orchestration Framework
## GTA V Character AI Analysis System

---

## 📋 Project Overview

A **multi-agent orchestration framework** that simulates GTA V characters analyzing weekly gameplay activity. Each agent brings a unique perspective, personality, and analytical approach to weekly data, creating a comprehensive, multi-dimensional analysis system.

### Core Purpose
- **Objective**: Extract meaningful insights from weekly activity data through specialized character lenses
- **Method**: Deploy 8 specialized AI agents, each with distinct roles and personalities
- **Output**: Comprehensive weekly reports combining financial, strategic, social, entertainment, and narrative perspectives

### Target System
- **Game**: Grand Theft Auto V (Single-player & Online modes)
- **Data Focus**: Weekly activity logs, missions, heists, crew interactions
- **Integration**: OpenAI GPT API (with offline fallback mode)
- **Language**: Thai (ภาษาไทย) primary, multilingual support

### Agent Portfolio

1. **Michael De Santa** - Strategic & Financial Analyst
   - 💰 Financial efficiency and ROI analysis
   - 📊 Risk vs. Reward assessment
   - 📈 Long-term strategic planning

2. **Franklin Clinton** - Prize Ride & Test Ride Analyst
  - 🚗 Remember Prize Ride Challenge eligible vehicles and matched conditions
  - 🏁 Evaluate Test Ride 1–3 and Premium Test Ride outcomes
  - 💡 Assess value of discounted cars and recommend Buy/Skip/Consider

3. **Trevor Philips** - Chaos & Risk Analyst
   - 🎢 Thrill factor and entertainment value
   - ⚠️ Risk identification and survival instincts
   - 🤪 Chaos potential assessment

4. **Agent 14** - Special Operations & Efficiency Analyst
   - 🕵️ Heist and special mission analysis
   - 📊 Operational metrics and KPIs
   - 🎖️ Efficiency optimization

5. **Lamar Davis** - Social & Crew Activity Analyst
   - 👥 Team performance tracking
   - 🎭 Crew vibes and dynamics
   - ⭐ MVP recognition

6. **Lester Crest** - Master Coordinator & Weekly Summary
   - 🔗 Aggregates all agent perspectives
   - 📑 Definitive weekly report creation
   - 🎯 Strategic priorities ranking

7. **Tony** - Nightclub & Warehouse Operations Analyst
  - 💼 Weekly nightclub income calculation and revenue breakdown
  - 📦 Warehouse stock & technician planning
  - ⚙️ Operational recommendations for technicians and goods

8. **Ron Jakowski** - Weekly Story Narrator
   - 📖 Story arc documentation
   - 🎬 Dramatic narrative weaving
   - 🎪 Character-driven storytelling

---

## 🔐 Isolation Environment

### Agent Isolation Model
Each agent operates in **complete functional isolation** with the following principles:

#### **1. Message Protocol Separation**
- Each agent maintains its own **system prompt** defining personality and role
- **User prompt** contains identical raw data but interpreted differently
- No direct inter-agent communication during analysis phase
- Each agent produces independent analysis output

#### **2. Execution Context**
```
┌─────────────────────────────────────┐
│     Weekly Activity Data (JSON)     │
└────────────┬────────────────────────┘
             │
    ┌────────┴────────┬──────────────┬─────────────┐
    ▼                  ▼              ▼             ▼
[Michael]         [Franklin]      [Trevor]     [Agent14]
Strategic         Progression      Chaos       Operations
    │                  │             │             │
    └────────┬─────────┴─────────────┴─────────┬──┘
             │                                  │
          [Analysis Output Stream 1-8]         │
             │                                  │
             ▼                                  ▼
        [Lester Crest Aggregation]
             │
             ▼
     [Final Weekly Report]
```

#### **3. Data Isolation**
- **Input**: Same raw weekly data (JSON)
- **Processing**: Each agent applies its own analytical lens
- **Output**: 8 independent analysis reports
- **Aggregation**: Lester combines all perspectives into summary

#### **4. Memory & State Management**
- Each agent is **stateless** - no memory between runs
- All context comes from the input JSON data
- No persistent agent state or learning
- Reproducible results with identical inputs

#### **5. Communication Channels**
```
Single-Direction Flow:
Framework → Agent instances → Analysis output → Aggregation
```

- **Input Channel**: Receives JSON activity data
- **Processing Channel**: Internal system/user prompts (isolated per agent)
- **Output Channel**: Individual analysis text
- **Aggregation Channel**: Lester receives all 7 other analyses before summary

#### **6. Error Containment**
- Individual agent failures do NOT crash the orchestrator
- Failures isolated to that agent's output slot
- Other agents continue processing unaffected
- Error logs captured separately

---

## 🎯 Strategy

### Multi-Perspective Analysis Strategy

#### **1. Layer 1: Specialized Analysis** (Agents 1-7)
Each offline and online agent performs **focused domain analysis**:

| Agent | Domain | Questions Answered |
|-------|--------|------------------|
| **Michael** | Finance | Is this profitable? ROI? Long-term value? |
| **Franklin** | Prize Ride & Test Rides | Prize Ride eligibility, Test Ride evaluation, discount car valuation |
| **Trevor** | Entertainment | Was it fun? Thrilling? Worth the chaos? |
| **Agent14** | Operations | Efficient? Successful? Data-backed? |
| **Lamar** | Sociology | Team vibes? MVP? Crew dynamics? |
| **Tony** | Nightclub & Warehouse | Nightclub income, stock management, technician planning |
| **Ron** | Narrative | What's the story? Plot arcs? Drama? |

#### **2. Layer 2: Aggregation** (Agent Lester)
Lester Crest synthesizes all 7 agent analyses into:
- **Executive Summary**: One-page overview
- **Key Metrics**: Financial, progression, efficiency, satisfaction scores
- **Strategic Insights**: Patterns, trends, opportunities
- **Action Items**: Prioritized next steps
- **Risk Assessment**: Challenges and bottlenecks

#### **3. Analysis Workflow**
```
Phase 1: Data Loading
  └─ Parse weekly_data.json
  └─ Validate data integrity

Phase 2: Parallel Execution
  └─ Deploy 7 specialized agents → Independent analyses
  └─ Each agent processes same raw data through own lens
  └─ Collect all outputs synchronously or asynchronously

Phase 3: Aggregation
  └─ Lester receives all 7 analyses
  └─ Creates comprehensive summary report
  └─ Identifies consensus vs. divergence

Phase 4: Output Generation
  └─ Format multi-perspective report
  └─ Save to reports/ directory with timestamp
  └─ Optional: Structured JSON output
```

#### **4. Personality-Driven Analysis Bias**
Each agent **intentionally biases** analysis through personality:

- **Michael**: Sees financial efficiency, dismisses "non-profitable" activities
-- **Franklin**: Focuses on vehicle event eligibility and car valuation
- **Trevor**: Prioritizes chaos and thrill, undervalues caution
- **Agent14**: Cold logic, data-only, dismisses narrative
- **Lamar**: Social optimization, crew harmony, team dynamics
 - **Tony**: Nightclub & Warehouse operations — focuses on nightclub income, warehouse stock management, and technician planning
- **Ron**: Narrative, drama, emotional arcs
- **Lester**: Holistic, balanced, synthesizing all views

#### **5. Consensus & Divergence Pattern**
```
When all agents agree → Core truth emerges (high confidence)
When agents diverge → Multi-faceted perspective revealed
Lester highlights both → Complete decision-support picture
```

Example: A heist might be:
-- **High ROI** (Michael ✓)
-- **Prize Ride fit** (Franklin ✓)
-- **High chaos/risk** (Trevor ✓)
-- **Operationally efficient** (Agent14 ✓)
-- **Good team bonding** (Lamar ✓)
-- **Nightclub value** (Tony ✓✓✓)
-- **Dramatic story** (Ron ✓✓✓)
- **Net recommendation** (Lester: PRIORITY)

---

## ⚠️ Error Handling

### Error Classification & Response

#### **1. Data Input Errors**

| Error Type | Detection | Response |
|-----------|-----------|----------|
| **Invalid JSON** | Parse failure | Log error, show fallback format, graceful exit |
| **Missing fields** | Validation fails | Use defaults, warn user, continue with available data |
| **Type mismatch** | Type validation | Coerce types if possible, error if critical |
| **Empty dataset** | Length check | All agents receive empty data, return "no data" response |

#### **2. API Errors** (OpenAI Integration)

```
Error Type                → Retry Strategy        → Fallback
─────────────────────────────────────────────────────────
Network timeout           → Retry 3x, exp backoff → Offline mode
API rate limit (429)      → Wait & retry          → Offline mode
Authentication (401/403)  → Check API key         → Offline mode
Invalid request (400)     → Log & skip agent      → Continue others
Insufficient quota (429)  → Operator notification → Offline mode
Server error (5xx)        → Retry with backoff    → Offline mode
```

#### **3. Agent-Specific Errors**

```python
"""
For each agent:
1. Try → Run analysis against data
2. Catch ImportError → Log missing dependency
3. Catch Exception → Generic error handler
4. Return fallback message
5. Log to errors.log
6. Continue with next agent
"""
```

**Example Error Responses:**
```
[ERROR] Michael's analysis failed: Connection timeout
→ Michael's slot in report: "[OFFLINE] Michael unavailable"
→ Continue with Franklin, Trevor, etc.
```

#### **4. Aggregation Errors** (Lester)

If some agents fail before Lester aggregates:
```
- Lester receives: [Michael ✓, Franklin ✓, Trevor ✗, Agent14 ✓]
- Action: Generate summary from available agents
- Note: "Trevor's analysis unavailable - see error log"
- Still produce valid report with 7/8 perspectives
```

#### **5. Output Storage Errors**

| Error | Fallback |
|-------|----------|
| Directory doesn't exist | Create reports/ directory automatically |
| Permission denied | Try alternate path, warn user |
| Disk full | Continue to stdout, warn about incomplete save |
| Filename collision | Append timestamp, ensure uniqueness |

#### **6. Offline Mode Fallback**

When OPENAI_API_KEY is missing or API unavailable:
```
System enters OFFLINE_MODE:
├─ All agents return placeholder responses
├─ Format: [OFFLINE MODE – Agent Name]
├─ System prompt shown (for transparency)
├─ User prompt shown (for transparency)
├─ No actual LLM call made
└─ Useful for testing/demo without credentials
```

#### **7. Error Logging Strategy**

```
Log File: errors.log (auto-created in project root)
Log Entries:
  TIMESTAMP | LEVEL | AGENT | ERROR_CODE | MESSAGE | CONTEXT
  ─────────────────────────────────────────────────────────
  2026-04-06 10:30:45 | ERROR | Michael | API_TIMEOUT | Connection timeout after 30s | weekly_summary_2026w14.json
  2026-04-06 10:30:46 | WARN | Franklin | MISSING_DATA | Field 'missions' not found | available_fields: [...]
```

#### **8. Recovery & Retry Logic**

```
Critical Path Errors (Fail Fast):
  ├─ Invalid JSON structure → Stop, report data problem
  └─ No agents available → Stop, check configuration

Non-Critical Errors (Fail Graceful):
  ├─ Single agent fails → Mark as failed, continue others
  ├─ API temporarily down → Retry with exponential backoff
  └─ Output save fails → Log, continue to next process
```

#### **9. User Reporting**

When errors occur, provide:
```
✗ Agent Trevor: Failed
  Reason: Connection timeout
  Action: See error_log.txt for details
  Workaround: Try again or use --offline flag

✓ Other agents: OK (7/8 completed)
```

#### **10. Monitoring & Debugging**

```
Run modes:
  python main.py                    # Normal (logs errors quietly)
  python main.py --verbose          # Show all errors + details
  python main.py --debug            # Full traceback, API logs, etc.
  python main.py --offline          # Force offline mode
```

---

## 📊 Data Flow Diagram

```
┌─────────────────────────┐
│   weekly_data.json      │
│   (Activity Records)    │
└────────────┬────────────┘
             │
      ┌──────▼──────┐
      │ Validation  │
      │   & Parse   │
      └──────┬──────┘
             │
   ┌─────────┼─────────┬───────────┬────────────┐
   │         │         │           │            │
   ▼         ▼         ▼           ▼            ▼
[Michael] [Franklin] [Trevor] [Agent14]    [Lamar]
  │          │         │         │          │
  └─────────┬┴────────┬┴────────┬┴──────────┴─┐
            │                                 │
      ┌────▼──────────────────────────────┐  │
      │ [Tony] [Ron]                      │  │
       └────┬────────────────────────────┬─┘  │
            │                            │    │
       ┌────▼────────────────────────────▼──┐ │
       │  Lester (Aggregation & Summary)    │◄─┘
       └────┬──────────────────────────────┐
            │                               │
       ┌────▼─────────────────────────────┐
       │  Final Weekly Report (JSON/MD)   │
       │  - Executive Summary             │
       │  - All Agent Perspectives        │
       │  - Combined Metrics              │
       │  - Strategic Recommendations     │
       └─────────────────────────────────┘
```

---

## 🔧 Configuration & Environment

```bash
# .env file
OPENAI_API_KEY=sk-your-key-here
LLM_MODEL=gpt-4o-mini
LLM_TEMPERATURE=0.7
ENABLED_AGENTS=all  # or: michael,franklin,trevor
REPORTS_DIR=reports/
```

---

## 📚 Implementation Reference

See individual agent documentation:
- [trevor.md](./npc/trevor.md)
- [michael.md](./npc/michael.md)
- [franklin.md](./npc/franklin.md)
- [agent14.md](./npc/agent14.md)
- [lamar.md](./npc/lamar.md)
- [lester.md](./npc/lester.md)
- [ron.md](./npc/ron.md)
- [tony.md](./online/tony.md)
