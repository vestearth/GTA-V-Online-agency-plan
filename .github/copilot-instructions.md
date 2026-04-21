# AI Assistant — Repository custom instructions (Copilot/Cursor/Codex/Gemini)

**English (EN)** · **ไทย (TH)** — Both sections describe the same rules; read either or both.

---

## EN — What this repository is

This repo is a **specification and prompt library** for a multi-agent “GTA V Online weekly planning” workflow. It is **not** a runnable application: there is **no** Python/Node entrypoint, `requirements.txt`, or automated orchestrator in-tree.

- **Canonical weekly payload**: `data/schema_v2_example.json` (schema v2).
- **Framework narrative & roles**: `README.md`, `src/agents/*.yaml`, `src/skills/*.yaml`.
- **Assistant integration promptbook**: `.github/skills/gta-weekly-planning/SKILL.md`.
- **Workflow index**: `src/agency.config.yaml` and `src/workflows/weekly_planning.yaml`.

When editing or generating content:

- Prefer **schema v2** fields and naming when discussing weekly JSON.
- **Do not assume** hidden scripts, APIs, or env files exist unless you add them explicitly.
- **Reports** are usually saved under `reports/` locally; that path is **gitignored** (see `.gitignore`).
- When suggesting code, keep it **minimal and scoped** to the user’s request; this project’s primary artifact is **Markdown + JSON + assistant prompts**, not a large codebase.

---

## TH — โปรเจกต์นี้คืออะไร

ที่เก็บนี้เป็น **เอกสารสเปกและชุด prompt** สำหรับเวิร์กโฟลว์หลายเอเย่นต์ “วางแผน GTA V Online รายสัปดาห์” **ไม่ใช่แอปที่รันได้ทันที** — ไม่มี entrypoint ภาษา Python/Node, `requirements.txt` หรือตัว orchestrator อัตโนมัติใน repo

- **ตัวอย่าง payload มาตรฐาน**: `data/schema_v2_example.json` (schema v2)
- **บทบาทและกรอบงาน**: `README.md`, `src/agents/*.yaml`, `src/skills/*.yaml`
- **จุดเชื่อมผู้ช่วย AI**: `.github/skills/gta-weekly-planning/SKILL.md`
- **ดัชนีเวิร์กโฟลว์**: `src/agency.config.yaml` และ `src/workflows/weekly_planning.yaml`

เมื่อช่วยแก้หรือสร้างเนื้อหา:

- อ้างอิง **schema v2** และชื่อฟิลด์ให้สอดคล้องเมื่อพูดถึง JSON รายสัปดาห์
- **อย่าสมมติ** ว่ามีสคริปต์ซ่อน, API หรือไฟล์ env ถ้าผู้ใช้ไม่ได้เพิ่มจริง
- **รายงาน** มักบันทึกใน `reports/` บนเครื่อง — path นี้ถูก **gitignore** (ดู `.gitignore`)
- ถ้าเสนอโค้ด ให้**เล็กและตรงงาน** — สิ่งสำคัญของโปรเจกต์คือ **Markdown + JSON + prompts สำหรับผู้ช่วย AI** ไม่ใช่โค้ดเบสใหญ่

---

## EN — Suggested assistant usage pattern

1. Prepare or paste weekly data (goal: valid schema v2 JSON).
2. Run schema precheck first (`validate_weekly_schema_lightweight`) and stop if blocking errors exist.
3. Load `data/player_profile.json` and run readiness gate (`gate_activity_prerequisites`).
4. If readiness has hard blockers, report blockers before any specialist analysis.
5. Run specialist analysis (**Michael**, **Franklin**, **Trevor**, **Agent 14**, **Tony**) as needed.
6. Run **Lester** last (`synthesize_final_report`) to synthesize outputs into one weekly summary with time buckets and action queue.

Order details and file paths are summarized in `src/agency.config.yaml`, `src/workflows/weekly_planning.yaml`, and the root `README.md`.

---

## TH — แนวทางใช้ผู้ช่วย AI (ลำดับแนะนำ)

1. เตรียมหรือวางข้อมูลสัปดาห์ (เป้าหมายคือ JSON ที่ถูกต้องตาม schema v2)
2. รัน schema precheck ก่อนเสมอ (`validate_weekly_schema_lightweight`) และหยุดทันทีถ้าพบ blocking errors
3. โหลด `data/player_profile.json` แล้วรัน readiness gate (`gate_activity_prerequisites`)
4. ถ้ามี blockers ด้านความพร้อม ให้รายงาน blockers ก่อนวิเคราะห์เชิงลึก
5. รันเอเย่นต์เชิงเจาะจง (**Michael**, **Franklin**, **Trevor**, **Agent 14**, **Tony**) ตามต้องการ
6. ปิดท้ายด้วย **Lester** (`synthesize_final_report`) เพื่อสังเคราะห์รายงานพร้อม time buckets และ action queue

รายละเอียดลำดับและ path ไฟล์อยู่ใน `src/agency.config.yaml`, `src/workflows/weekly_planning.yaml` และ `README.md` ที่รากโปรเจกต์

---

## EN — Language preference

Project docs mix **Thai and English**. Unless the user specifies otherwise, **follow the language of the user’s latest message** for new prose; keep technical identifiers (JSON keys, file paths, agent ids) in their **canonical** form.

---

## TH — ภาษา

เอกสารในโปรเจกต์ใช้ทั้ง**ไทยและอังกฤษ** ถ้าผู้ใช้ไม่ระบุ ให้ตอบตาม**ภาษาของข้อความล่าสุด** ส่วนชื่อเทคนิค (คีย์ JSON, path, id ของเอเย่นต์) ใช้แบบ**canonical** ตามใน repo

---

## EN — Documentation freshness rule

When a change updates core workflow semantics (agents, skills, orchestration order, references, or automation behavior), update the relevant docs in the same change and refresh `README.md` `Last Updated`.

## TH — กติกาความสดใหม่ของเอกสาร

ถ้ามีการเปลี่ยนสาระสำคัญของ workflow (agent, skill, ลำดับ orchestration, references หรือ automation behavior) ให้ปรับเอกสารที่เกี่ยวข้องใน change เดียวกัน และอัปเดต `Last Updated` ใน `README.md` ทุกครั้ง
