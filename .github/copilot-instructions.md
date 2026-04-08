# GitHub Copilot — Repository custom instructions

**English (EN)** · **ไทย (TH)** — Both sections describe the same rules; read either or both.

---

## EN — What this repository is

This repo is a **specification and prompt library** for a multi-agent “GTA V Online weekly planning” workflow. It is **not** a runnable application: there is **no** Python/Node entrypoint, `requirements.txt`, or automated orchestrator in-tree.

- **Canonical weekly payload**: `data/schema_v2_example.json` (schema v2).
- **Framework narrative & roles**: `agents/Agent.md`, `agents/npc/*.md`.
- **Copilot integration**: `.github/prompts/`, `.github/agents/`, `.github/skills/`.
- **Optional machine-readable workflow index**: `agents/agency.config.yaml` (for humans/tools; nothing in this repo consumes it automatically).

When editing or generating content:

- Prefer **schema v2** fields and naming when discussing weekly JSON.
- **Do not assume** hidden scripts, APIs, or env files exist unless you add them explicitly.
- **Reports** are usually saved under `reports/` locally; that path is **gitignored** (see `.gitignore`).
- When suggesting code, keep it **minimal and scoped** to the user’s request; this project’s primary artifact is **Markdown + JSON + Copilot prompts**, not a large codebase.

---

## TH — โปรเจกต์นี้คืออะไร

ที่เก็บนี้เป็น **เอกสารสเปกและชุด prompt** สำหรับเวิร์กโฟลว์หลายเอเย่นต์ “วางแผน GTA V Online รายสัปดาห์” **ไม่ใช่แอปที่รันได้ทันที** — ไม่มี entrypoint ภาษา Python/Node, `requirements.txt` หรือตัว orchestrator อัตโนมัติใน repo

- **ตัวอย่าง payload มาตรฐาน**: `data/schema_v2_example.json` (schema v2)
- **บทบาทและกรอบงาน**: `agents/Agent.md`, `agents/npc/*.md`
- **จุดเชื่อม Copilot**: `.github/prompts/`, `.github/agents/`, `.github/skills/`
- **ดัชนีเวิร์กโฟลว์แบบอ่านได้ด้วยเครื่อง (ถ้ามี)**: `agents/agency.config.yaml` — ใช้อ้างอิงสำหรับมนุษย์หรือเครื่องมือภายนอก **ไม่มีส่วนใน repo ที่อ่านไฟล์นี้อัตโนมัติในปัจจุบัน**

เมื่อช่วยแก้หรือสร้างเนื้อหา:

- อ้างอิง **schema v2** และชื่อฟิลด์ให้สอดคล้องเมื่อพูดถึง JSON รายสัปดาห์
- **อย่าสมมติ** ว่ามีสคริปต์ซ่อน, API หรือไฟล์ env ถ้าผู้ใช้ไม่ได้เพิ่มจริง
- **รายงาน** มักบันทึกใน `reports/` บนเครื่อง — path นี้ถูก **gitignore** (ดู `.gitignore`)
- ถ้าเสนอโค้ด ให้**เล็กและตรงงาน** — สิ่งสำคัญของโปรเจกต์คือ **Markdown + JSON + Copilot prompts** ไม่ใช่โค้ดเบสใหญ่

---

## EN — Suggested Copilot usage pattern

1. Prepare or paste weekly data (goal: valid schema v2 JSON).
2. Run **Pavel** / **Vincent** prompts if the payload needs curation or validation.
3. Run specialist prompts (**Michael**, **Franklin**, **Trevor**, **Agent 14**, **Lamar**, **Tony**, **Ron**) as needed.
4. Run **Lester** last to synthesize outputs into one weekly summary.

Order details and file paths are summarized in `agents/agency.config.yaml` and the root `README.md`.

---

## TH — แนวทางใช้ Copilot (ลำดับแนะนำ)

1. เตรียมหรือวางข้อมูลสัปดาห์ (เป้าหมายคือ JSON ที่ถูกต้องตาม schema v2)
2. ใช้ prompt ของ **Pavel** / **Vincent** เมื่อข้อมูลยังดิบหรือต้องตรวจโครงสร้าง
3. รันเอเย่นต์เชิงเจาะจง (**Michael**, **Franklin**, **Trevor**, **Agent 14**, **Lamar**, **Tony**, **Ron**) ตามต้องการ
4. ปิดท้ายด้วย **Lester** เพื่อสังเคราะห์เป็นรายงานสัปดาห์เดียว

รายละเอียดลำดับและ path ไฟล์อยู่ใน `agents/agency.config.yaml` และ `README.md` ที่รากโปรเจกต์

---

## EN — Language preference

Project docs mix **Thai and English**. Unless the user specifies otherwise, **follow the language of the user’s latest message** for new prose; keep technical identifiers (JSON keys, file paths, agent ids) in their **canonical** form.

---

## TH — ภาษา

เอกสารในโปรเจกต์ใช้ทั้ง**ไทยและอังกฤษ** ถ้าผู้ใช้ไม่ระบุ ให้ตอบตาม**ภาษาของข้อความล่าสุด** ส่วนชื่อเทคนิค (คีย์ JSON, path, id ของเอเย่นต์) ใช้แบบ**canonical** ตามใน repo
