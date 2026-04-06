# GTA V Online – AI Agent Weekly Analyzer

ระบบ AI Agent สำหรับประมวลสรุปกิจกรรมแต่ละสัปดาห์, วิเคราะห์ความคุ้มค่า และเรื่องราว (story) ตัวละครต่างๆ ในรูปแบบ GTA V

---

## ✨ Features

- **8 AI Agents** ที่มีชื่อและบุคลิกตามตัวละคร GTA V Online / Offline
- วิเคราะห์ครบ 5 มิติ: การเงิน, กิจกรรม, ทีม, ความสนุก, ปฏิบัติการพิเศษ
- รองรับ **OpenAI API** (gpt-4o-mini, gpt-4o, หรือโมเดลอื่นๆ)
- ทำงานใน **Offline/Demo Mode** โดยไม่ต้องมี API Key
- Export รายงานเป็น **Markdown**

---

## 🎮 Agents

### GTA V Offline Characters

| Agent | ชื่อ | บทบาท |
|-------|------|-------|
| `michael` | **Michael De Santa** | นักวิเคราะห์เชิงกลยุทธ์และการเงิน |
| `trevor` | **Trevor Philips** | นักวิเคราะห์ความสนุกและความเสี่ยง |
| `franklin` | **Franklin Clinton** | นักวิเคราะห์กิจกรรมภาคสนามและความก้าวหน้า |

### GTA V Online Characters

| Agent | ชื่อ | บทบาท |
|-------|------|-------|
| `lester` | **Lester Crest** | ผู้ประสานงานหลักและผู้สรุปรายงานประจำสัปดาห์ |
| `ron` | **Ron Jakowski** | นักเล่าเรื่องและบันทึก Story ประจำสัปดาห์ |
| `lamar` | **Lamar Davis** | นักวิเคราะห์กิจกรรมทีมและบรรยากาศสังคม |
| `english_dave` | **English Dave** | นักวิเคราะห์ความสนุกและความบันเทิง |
| `agent14` | **Agent 14** | นักวิเคราะห์ปฏิบัติการพิเศษและประสิทธิภาพ |

---

## 🚀 Quick Start

### 1. ติดตั้ง

```bash
pip install -r requirements.txt
```

### 2. ตั้งค่า API Key (ไม่บังคับ – ใช้ Offline Mode ได้)

สร้างไฟล์ `.env` ที่ root ของ project:

```env
OPENAI_API_KEY=sk-...your-key-here...
LLM_MODEL=gpt-4o-mini
LLM_TEMPERATURE=0.7
```

### 3. เตรียมข้อมูลสัปดาห์

แก้ไข `data/sample_week.json` หรือสร้างไฟล์ JSON ใหม่ตามรูปแบบ:

```json
{
  "week": "2024-W15 (8-14 April 2024)",
  "player": "YourGTAName",
  "crew": "Your Crew Name",
  "playtime_hours": 18.5,
  "financials": {
    "earnings_total": 4250000,
    "expenses_total": 890000,
    "net_profit": 3360000,
    "currency": "GTA$"
  },
  "missions_completed": [ "..." ],
  "highlights": [ "..." ]
}
```

ดูตัวอย่างเต็มได้ที่ [`data/sample_week.json`](data/sample_week.json)

### 4. รันระบบ

```bash
# รันทุก agents (บันทึกรายงานในโฟลเดอร์ reports/)
python main.py

# รัน agents เฉพาะที่ต้องการ
python main.py --agents lester,michael,ron

# พิมพ์รายงานออกหน้าจอโดยไม่บันทึกไฟล์
python main.py --no-save

# ระบุไฟล์ข้อมูลและโฟลเดอร์ output
python main.py --data data/week_15.json --output reports/april/
```

---

## 📁 Project Structure

```
GTA-V-Online-agency-plan/
├── agents/
│   ├── base_agent.py          # Base class สำหรับทุก agent
│   ├── offline/
│   │   ├── michael.py         # Michael De Santa
│   │   ├── trevor.py          # Trevor Philips
│   │   └── franklin.py        # Franklin Clinton
│   └── online/
│       ├── lester.py          # Lester Crest
│       ├── ron.py             # Ron Jakowski
│       ├── lamar.py           # Lamar Davis
│       ├── english_dave.py    # English Dave
│       └── agent14.py         # Agent 14
├── data/
│   └── sample_week.json       # ตัวอย่างข้อมูลสัปดาห์
├── tests/
│   └── test_agents.py         # Unit tests (27 tests)
├── config.py                  # การตั้งค่าระบบ
├── main.py                    # Orchestrator หลัก
├── requirements.txt
└── README.md
```

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

## 🔧 Adding a New Agent

1. สร้างไฟล์ใหม่ใน `agents/offline/` หรือ `agents/online/`
2. สืบทอดจาก `BaseAgent` และกำหนดค่า `name`, `character_type`, `role`, `personality`
3. implement เมธอด `get_analysis_instruction()` ที่คืน prompt instruction
4. ลงทะเบียนใน `AGENT_REGISTRY` ใน `main.py`
5. เพิ่ม import ใน `agents/__init__.py`
