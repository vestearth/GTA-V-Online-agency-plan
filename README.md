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
├── scripts/                                # 🛠️ Automation Tools
│   ├── scrape_weekly_update.py             # Auto-discovery & data extraction (v2.6)
│   ├── generate_weekly_report.py           # Dashboard generator (v1.1)
│   ├── update_vehicle_prices.py            # Reference sync
│   └── fetch_gtacar_prices.py              # Price fetcher
├── data/                                   # 📥 Data Payloads
│   ├── references/                         # Lookup catalogs
│   │   ├── scraper_mapping.yaml            # Scraper regex & keywords mapping
│   │   ├── vehicle_prices.yaml             # Used by Franklin
│   │   └── ...
├── reports/                              # 📤 Agent outputs & Final Executive Overviews
├── docs/                                 # 📚 Templates and documentation
└── .github/skills/gta-weekly-planning/   # 🤖 Reusable skill/prompt hook (portable)
```

---

## 🎯 How to Use (Copilot / Cursor / Codex / Gemini)

No Python or Node.js runtime is required for the core workflow. The intelligence lives in prompt templates and YAML specs; your chosen AI assistant acts as the Orchestrator.

> **Optional automation scripts** in `scripts/` require Python 3. They are not part of the primary AI workflow — see [Automation Scripts](#automation-scripts) below if you want to use them.

1. **Bring Data:** Grab the weekly update text from the Rockstar Newswire or GTA Forums.
2. **Set Player Profile:** Update `data/player_profile.json` with your bankroll, owned assets, and time constraints.
3. **Invoke your assistant:** In your preferred client (Copilot Chat, Cursor Agent/Chat, Codex, Gemini), ask:
   > *"Here is the new GTA weekly update data... Please run `src/workflows/weekly_planning.yaml`, use `data/player_profile.json`, follow `.github/skills/gta-weekly-planning/SKILL.md`, and generate the final report in `reports/`."*
4. The assistant should read the `SKILL.md` rulebook, instantiate agents according to `src/agents/*.yaml`, apply logic from `src/skills/`, and output Lester's Final Master Plan.
   - Purchase recommendations should pass through `evaluate_purchase_fit` so discounts are checked against bankroll, reserve floor, ownership, and profile goals.
   - Lester may use `compare_week_over_week` and advisory decision memory from `track_weekly_decisions` when prior payloads, reports, or confirmed user history are available.
   - Before delivery, run `validate_report_completeness` to confirm required sections, discount snapshots, guardrails, and the exactly 3 standard week-id report files.
5. Weekly standard output in `reports/` should contain:
   - `weekly_master_plan_<week_id>.md`
   - `weekly_master_plan_<week_id>_income_scenarios.md`
   - `event_master_plan_<week_id>.md`

Need ready-to-use prompts by platform? See `docs/assistant-usage.md`.
Repository-wide agent rules are documented in `AGENTS.md`.

---

### Automation Scripts

> **Requires Python 3.** These scripts are optional helpers and not part of the core AI workflow.

**Scrape a weekly update from a Newswire URL:**
```bash
python3 scripts/scrape_weekly_update.py --url <newswire_url>
# Add --overwrite to replace an existing file for the same week.
```

**Run a simulation with built-in sample data (no network):**
```bash
python3 scripts/scrape_weekly_update.py --simulate
```

Running the script without `--url` or `--simulate` prints usage help and exits.

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
2. **Activity Normalization** (`normalize_featured_activities` to derive `weekly_content.featured_activities` from `weekly_content.events` when needed)
3. **Vehicle Normalization** (`normalize_vehicle_opportunities` to derive `weekly_content.vehicle_opportunities` from raw weekly vehicle surfaces when needed)
4. **Prerequisite Gate** (`gate_activity_prerequisites` via Agent 14 + `player_profile`)
5. **Parallel Specialist Analysis** (Michael, Franklin, Trevor, Agent 14, Tony)
6. **Executive Synthesis** (Lester via `synthesize_final_report` + priority scoring + action queue)
7. **Post-Synthesis Quality Group** (Agent 14 route design via `design_weekly_route`, Lester decision memory via `track_weekly_decisions`, and final QA via `validate_report_completeness`)

Role split note:

- Michael handles profitability, $/hour, and purchase-value judgments.
- Franklin handles vehicle value and `evaluate_purchase_fit` checks for cars and other weekly purchases before Lester makes the final buy/skip ruling.
- Agent 14 handles feasibility, prerequisites, platform/crew fit, and session planning.
- Lester handles week-over-week context, final synthesis, advisory decision memory, and report completeness validation.
- Agent 14 readiness logic accepts either `weekly_content.featured_activities` or `weekly_content.events` as the activity source.

Decision memory is advisory. Unless a concrete history file, prior report, or user confirmation exists, assistants should not claim that a past recommendation was actually bought, completed, or skipped.

---

## ⚡ Weekly intake และการรีวิวก่อนเผยแพร่

ระบบใช้ **curated-first**: scrape weekly payload ไปยัง `data/candidates/` ก่อน
และบันทึกสถานะใน `data/refresh_status.json` โดยไม่เขียนทับ payload ที่ผ่านรีวิวแล้ว
การดึงข้อมูลสำเร็จไม่ใช่การอนุมัติคำแนะนำหรือยืนยันว่าดึงเนื้อหาครบ

```bash
python scripts/run_weekly_content_refresh.py --url https://www.rockstargames.com/newswire/article/ARTICLE_ID/ARTICLE_SLUG
# ตรวจ candidate กับแหล่งข้อมูล แล้วรัน canonical assistant workflow เพื่อสร้างรายงาน 3 ไฟล์
python scripts/review_weekly_candidate.py data/candidates/weekly_planning_YYYY_wXX.json --reviewer REVIEWER
python scripts/run_weekly_content_refresh.py --publish-reviewed
```

อ่านขั้นตอนและสัญญาข้อมูลใน [คู่มือกู้คืนระบบ](docs/automation-recovery.md)
`generate_weekly_report.py` เป็น helper เก่าสำหรับตรวจข้อมูล ไม่อยู่ในงานรายสัปดาห์และไม่สร้าง Lester Master Plan

---

## 🚗 Vehicle Price Reference Refresh

Use the helper script to sync vehicle names from the latest weekly payload into `data/references/vehicle_prices.yaml`, auto-add stripped-name aliases, and print a null-price report:

`python3 scripts/update_vehicle_prices.py`

The sync script prefers `weekly_content.vehicle_opportunities` when present, but can also fall back to raw weekly surfaces such as `events`, `discounts`, podium/prize/test-ride entries, and showroom-style sections.

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
- งานราคานี้ใช้ `workflow_dispatch` เท่านั้น; งานตามเวลาและราคาใช้ producer เดียวใน Weekly Content Refresh
- ดึงเฉพาะรถราคาขาดของ weekly payload ล่าสุดโดยค่าเริ่มต้น; `--weekly` ระบุสัปดาห์ และ `--refresh-all` ใช้ตรวจ catalog ย้อนหลัง
- รายงาน attempted/succeeded/failed/skipped และเหตุผลใน `data/price_refresh_status.json` และ Actions summary
- ราคาไม่ทราบยังเป็น `null`; GTACars ล่มไม่ขัดขวางรายงานรายสัปดาห์ที่ผ่านรีวิว

### Weekly Content Refresh

- GitHub Actions workflow: `.github/workflows/weekly-content-refresh.yml`
- เวลา Thursday **03:00 UTC / 10:00 Bangkok** (`0 3 * * 4`); ต้องผ่าน source-date gate เสมอ หากข้อมูลรอบใหม่ยังไม่พร้อม ระบบจะหยุดพร้อม diagnostic
- ลำดับแหล่งข้อมูล: `newswire_url`/`--url` → `WEEKLY_UPDATE_URL` → `data/weekly_source_index.json` ที่รีวิวและตรงสัปดาห์
- ไม่ scrape listing ที่เป็น JavaScript shell และไม่เรียก Rockstar API ที่ไม่มีเอกสาร; ไม่มี source ที่ตรวจสอบได้จะหยุดพร้อม `needs_review` diagnostic
- รับ normalized article text จาก JSON-LD หรือ visible `<article>` พร้อม publication metadata; JS-only/ผิดสัปดาห์/GTA+ monthly จะหยุด
- ยังไม่มีรายงานที่อนุมัติ: เก็บ candidate + สถานะ `needs_review` สำเร็จ โดยคง Dashboard สัปดาห์เดิมพร้อมคำเตือน
- เผยแพร่ได้เมื่อ payload สัปดาห์ปัจจุบันเป็น `confirmed` และ `review.approved` ตรง hash ของ payload กับรายงาน canonical ทั้ง 3 ไฟล์
- `workflow_dispatch` input `publish_reviewed` ใช้เผยแพร่หลัง review handoff; ไม่มี dummy report หรือรายงานที่สี่
- ทุก writer ใช้ concurrency group เดียวและปฏิเสธ push เมื่อ remote เปลี่ยนระหว่างรัน; ต้องรันใหม่จาก checkout ล่าสุด
- `content-health.yml` ตรวจทุกวันเวลา 17:00 UTC / 00:00 Bangkok และเมื่อ weekly run จบ ตรวจ failed/missing/disabled runs และ GTA+ rollover
- Health Issues ใช้ชื่อคงที่ เปิดซ้ำ issue เดิมเมื่อปัญหากลับมา และปิดเมื่อสถานะฟื้นตัว; ผู้ติดตาม repository/Issue รับแจ้งตาม GitHub notification settings
- ทั้งสอง Dashboard แสดงอายุข้อมูล/วันหมดอายุ/สถานะรีวิว และตรวจหมดอายุในเบราว์เซอร์ด้วย
- ตรวจเมื่อ 2026-10-14 พบทั้งสอง workflow เดิมเป็น `disabled_inactivity`; ต้อง Enable workflow ใน Actions หลังนำการแก้ไขขึ้น GitHub

### GTA+ และสองตัวละคร

- GTA+ ใช้ membership period จริง ไม่เดาจากชื่อเดือน: `python scripts/gta_plus_intake.py PATH --reviewer REVIEWER`
- ต้องมีแหล่งข้อมูลต่อ benefit และ platform/edition/claim scope; `unknown` แสดงเป็นไม่ทราบ ไม่ใช้เป็นหลักฐานว่าใช้ได้ทุกแพลตฟอร์ม
- ไม่มี current reviewed period หรือมี period ซ้อนกัน: ไม่แสดง perks เก่าเป็นของปัจจุบัน และเปิด health Issue ให้ทำ intake
- Weekly/member multipliers แสดงแยกกัน; effective multiplier ต้องมี documented overlay ที่ตรงกิจกรรม/reward/week เท่านั้น
- `player_profile` v2 แยก `account`, `characters.main`, `characters.secondary`; top-level inventory เป็น compatibility view ของ main
- ใช้ `character_view` ก่อน gate/buy; ไม่รวมคลังและทรัพย์สินสองตัวละคร ตรวจ consistency ด้วย `python scripts/player_profile_state.py`
- Orange Shade Camo บันทึกเฉพาะ observed availability ตาม Issue #21; causal unlock/expiry/cancellation ยังคง `unknown`

### Local cron (optional)

If you also want local automation on your machine:

1. Open crontab:
   `crontab -e`
2. Add (adjust the path if needed):
   ตั้ง timezone ของ cron ให้ชัดเจน: `0 3 * * 4` สำหรับ UTC หรือ `0 10 * * 4` สำหรับ Asia/Bangkok แล้วเรียก `scripts/run_weekly_content_refresh.py` จากโฟลเดอร์ repository

---
**Last Updated**: October 14, 2026
**Framework Version**: Conceptual Multi-Agent Orchestration v2.0

---

## Static Planning Dashboard

Open `dashboard.html` in a browser for a quick visual overview of owned assets, weekly priorities, ROI/passive notes, and decision notes. It is intentionally static HTML + CSS: no npm, no build step, no backend.

The dashboard is a visual planning surface, not a separate app. It now supports a marker-based generator for both deterministic and conservative report-derived blocks. See `docs/dashboard-data-map.md` for field-by-field sourcing.

Local usage:

```bash
open dashboard.html
```

Phase 1 generator usage:

```bash
python scripts/generate_dashboard.py --check-markers
python scripts/generate_dashboard.py --dry-run
python scripts/generate_dashboard.py
```

Optional week override:

```bash
python scripts/generate_dashboard.py --weekly data/weekly_planning_2026_w22.json
```

Current generator scope:
- Phase 1 generated blocks: header metadata, summary cards, weekly deals snapshot, weekly vehicle spotlight, and the data status note
- Phase 2 generated blocks: current focus, next claim / buy, weekly action plan, what to buy / ignore, and asset overview when report parsing is confident enough
- Still manual: ROI notes and the decision log

Current dashboard notes:
- `Current Focus` and `Next Claim / Buy` now occupy the first two summary-card slots.
- `All Cars Needed` excludes Prize Ride and Lucky Wheel reward vehicles from the total, while keeping those vehicles visible and linked in the weekly spotlight.
- Long Gun Van groups collapse by default and can be expanded inline from the weekly deals snapshot.

GitHub Pages is enabled from `main` / root:
- Site: https://vestearth.github.io/GTA-V-Online-agency-plan/
- Dashboard: https://vestearth.github.io/GTA-V-Online-agency-plan/dashboard.html

Because the dashboard is plain static HTML/CSS, it can be hosted directly from the repository root on GitHub Pages without a build pipeline.

Future roadmap:
- Extend `scripts/generate_dashboard.py` further only for report-derived sections whose parsing and fallback rules stay reliable in practice.
- Keep the static HTML/CSS dashboard as the default surface even if generation expands; avoid a heavier app stack unless there is a concrete need for filtering, sorting, or live data loading.
