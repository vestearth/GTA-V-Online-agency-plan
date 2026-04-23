# 🚀 Quickstart: วิธีใช้งานสำหรับสัปดาห์ถัดไป (How to Run Next Week)

คู่มือฉบับย่อสำหรับก๊อปปี้ไปวางในผู้ช่วย AI (เช่น Copilot/Cursor/Codex/Gemini) เพื่อสั่งงานระบบ Multi-Agent Orchestrator ในสัปดาห์ต่อๆ ไป

ก่อนใช้งาน แนะนำให้อ้างอิงกติกากลางของโปรเจกต์ใน `AGENTS.md` ร่วมด้วย
และอัปเดต `data/player_profile.json` ให้ตรงกับบัญชีของคุณ (เงิน, ทรัพย์สิน, เวลาที่เล่นได้)

---

## 📋 แบบที่ 1: มีข่าวสัปดาห์ใหม่เป็น "ข้อความดิบ" (Raw Text)
ก็อปปี้อัปเดตจากเว็บ Rockstar Newswire หรือบอร์ดเกม แล้วใช้คำสั่งนี้เลย:

> *"นี่คือข้อมูลอัปเดต GTA ของสัปดาห์ใหม่: [วางเนื้อหาข่าวตรงนี้] ...ช่วยนำข้อมูลนี้ไปรันผ่าน `src/workflows/weekly_planning.yaml` โดยใช้ `data/player_profile.json` ด้วย ให้ทีมงานเปรียบเทียบกับเป้าหมายของผู้เล่นใน `data/schema_v2_example.json` แล้วสร้างรายงานสรุปแผนการเล่น (Master Plan) โดย Lester เซฟลงในโฟลเดอร์ `reports/` แบบ Markdown ให้ด้วยนะ และต้องมี time buckets (30m, 1-2h, 3h+) กับ action queue"*

---

## 📄 แบบที่ 2: มีไฟล์ข้อมูล JSON ของสัปดาห์นั้นแล้ว
ถ้าคุณทำไฟล์ JSON ของสัปดาห์นั้นๆ ไว้แล้ว (เช่น `data/weekly_planning_2026_w15.json`):

> *"รัน `src/workflows/weekly_planning.yaml` ให้หน่อย โดยใช้ข้อมูลกิจกรรมวิเคราะห์จากไฟล์ `data/weekly_planning_2026_w15.json` และ `data/player_profile.json` (ข้ามขั้นตอน Ingestion ไปดึงข้อมูลมาวิเคราะห์ได้เลย) จากนั้นสรุป Final Report จากมุมมองของ Lester ออกมาให้ที โดยต้องมี time buckets (30m, 1-2h, 3h+) และ action queue และสรุป Weekly Discounts ให้ครบทุก tier (50/40/30) แบบไม่ตกหล่น"*

---

## 🎯 แบบที่ 3: สั่งวิเคราะห์เจาะจงเฉพาะเรื่อง (เลือก Agent)
ถ้าไม่อยากได้รายงานเต็มรูปแบบ แต่อยากถามเจาะจงรายคน:

**ถามเรื่องรถ (Franklin):**
> *"ให้ Franklin ช่วยวิเคราะห์รถลดราคา รถ Test Ride และ Prize Ride ประจำสัปดาห์นี้จากเนื้อหาที่ให้มาที อ้างอิงเงื่อนไขจาก `src/agents/franklin.yaml` แล้วบอกมาว่าคันไหนควรซื้อ คันไหนควรข้าม"*

**ถามเรื่อง Nightclub & ธุรกิจ (Tony):**
> *"ให้ Tony Prince เช็คข้อมูลสัปดาห์นี้ โฟกัสตามหน้าที่ใน `src/agents/tony.yaml` ว่ามีธุรกิจ Passive ไหนลดราคา หรือมีธุรกิจไหนได้โบนัสบ้าง ควรโยก Technician ไปคุมอะไรดี?"*

**ถามเรื่องความคุ้มค่าและเงิน (Michael):**
> *"ให้ Michael คำนวณ ROI ประจำสัปดาห์นี้ตามกฎใน `src/skills/calculate_business_roi.yaml` กิจกรรมไหนทำเงินต่อชั่วโมงได้คุ้มที่สุด?"*

---

## 🧩 Discount Template (ใส่ใน weekly JSON ได้ทันที)

วางโครงนี้ใต้ `weekly_content` ของไฟล์ `data/weekly_planning_<week_id>.json`:

```json
"discounts": [
  {
    "tier_percent": 50,
    "items": [
      "รายการลด 50% #1",
      "รายการลด 50% #2"
    ]
  },
  {
    "tier_percent": 40,
    "items": [
      "รายการลด 40% #1"
    ]
  },
  {
    "tier_percent": 30,
    "items": [
      "รายการลด 30% #1",
      "รายการลด 30% #2"
    ]
  }
]
```

Checklist ก่อนรัน:
- ต้องมีทุก tier ที่ประกาศในสัปดาห์นั้น (เช่น 50/40/30)
- `items` ต้องไม่ว่าง
- ชื่อ item ควรใช้คำเต็มแบบ Rockstar

---

💡 **Tip:** ไม่ว่าคุณใช้ผู้ช่วยตัวไหน ให้ระบุ `src/workflows/weekly_planning.yaml`, `.github/skills/gta-weekly-planning/SKILL.md` และ `AGENTS.md` ใน prompt จะช่วยให้ผลลัพธ์สม่ำเสมอขึ้นมาก  
และถ้ามีส่วนลดประจำสัปดาห์ ให้กำชับว่า payload ต้องมี `weekly_content.discounts` (เช่น tiers 50/40/30 + items ครบ)