# 🎮 กรอบงานการจัดการ Multi-Agent GTA V

**ระบบวิเคราะห์ AI หลายตัวขั้นสูง** ที่วิเคราะห์กิจกรรมการเล่น GTA V รายสัปดาห์ผ่านมุมมองเฉพาะของตัวละคร 10 ตัว โดยแบ่งเป็น analyst agents และ support agents สำหรับจัดการข้อมูลก่อนวิเคราะห์

---

## 📚 โครงสร้างเอกสาร

กรอบงานนี้ถูก **บันทึกเอกสารทั้งหมดในรูปแบบ Markdown** โดยแยกไฟล์ตามส่วนประกอบต่าง ๆ:

### เอกสารกรอบงาน
- **[Agent.md](agents/Agent.md)** - เอกสารหลักของกรอบงานครอบคลุม:
  - 📋 ภาพรวมโครงการและพอร์ตโฟลิโอของเอเย่นต์
  - 🔐 สภาพแวดล้อมแยกและสถาปัตยกรรม
  - 🎯 กลยุทธ์หลายเอเย่นต์และเวิร์กโฟลว์การวิเคราะห์
  - ⚠️ การจัดการข้อผิดพลาดและโปรโตคอลการกู้คืน
- **[prompt_templates.md](agents/prompt_templates.md)** - แม่แบบ prompt สำหรับแต่ละเอเย่นต์

### เอกสารเอเย่นต์

#### เอเย่นต์ออฟไลน์ (วิเคราะห์ผู้เล่นคนเดียว)
- **[michael.md](agents/npc/michael.md)** - นักวิเคราะห์เชิงกลยุทธ์และการเงิน
- **[franklin.md](agents/npc/franklin.md)** - นักวิเคราะห์ Prize Ride & Test Ride และการประเมินมูลค่ารถ
- **[trevor.md](agents/npc/trevor.md)** - นักวิเคราะห์อาวุธ ของฟรี และความคุ้มค่าเชิงต่อสู้

#### เอเย่นต์ออนไลน์ (วิเคราะห์ผู้เล่นหลายคน)
- **[agent14.md](agents/npc/agent14.md)** - นักวิเคราะห์ปฏิบัติการพิเศษและประสิทธิภาพ
- **[lamar.md](agents/npc/lamar.md)** - นักวิเคราะห์สังคมและกิจกรรมทีม
- **[tony.md](agents/npc/tony.md)** - นักวิเคราะห์รายได้ Nightclub และการจัดการ Warehouse
- **[lester.md](agents/npc/lester.md)** - ผู้ประสานหลักและสรุปประจำสัปดาห์
- **[ron.md](agents/npc/ron.md)** - ผู้เล่าเรื่องประจำสัปดาห์

---

## ✨ คุณสมบัติสำคัญ

- **เอเย่นต์ AI เฉพาะทาง 10 ตัว** พร้อมบุคลิกตัวละคร GTA V ที่สมจริง
- **การวิเคราะห์หลายมิติ**: การเงิน, กลยุทธ์, สังคม, ความบันเทิง, ปฏิบัติการ, เนื้อเรื่อง, และการเตรียม/ตรวจสอบข้อมูล
- **สถาปัตยกรรมแยกการทำงาน**: แต่ละเอเย่นต์ทำงานแยกด้วยมุมมองตามบุคลิก
- **เอนจินรวบรวมผล**: Lester Crest สังเคราะห์การวิเคราะห์ทั้งหมดเป็นรายงานเชิงลึก
- **รวม OpenAI API** (gpt-4o-mini, gpt-4o หรือโมเดลอื่น)
- **โหมดออฟไลน์/เดโม** ใช้งานได้โดยไม่ต้องใช้คีย์ API
- **เอกสารในรูปแบบ Markdown** เพื่อความโปร่งใสของกรอบงาน

---

## 🎮 ชุดเอเย่นต์หลักและ support agents

### เอเย่นต์ออฟไลน์ (วิเคราะห์แคมเปญ)
| Agent | ความเชี่ยวชาญ | มุมมอง |
|-------|---------------|--------|
| **Michael** | การเงิน & กลยุทธ์ | นักวิเคราะห์มุ่งเน้นกำไรและความเสี่ยง |
| **Franklin** | Vehicle Opportunities | วิเคราะห์ `weekly_content.vehicle_opportunities` และความคุ้มค่ารถประจำสัปดาห์ |
| **Trevor** | Weapons & Combat Value | นักประเมินของฟรี อาวุธ และรถที่เพิ่มความพร้อมเชิงต่อสู้ |

### เอเย่นต์ออนไลน์ (วิเคราะห์ผู้เล่นหลายคน)
| Agent | ความเชี่ยวชาญ | มุมมอง |
|-------|---------------|--------|
| **Agent 14** | ปฏิบัติการ & ประสิทธิภาพ | เจ้าหน้าที่ข้อมูลมุ่งเน้นตัวชี้วัด |
| **Lamar** | Salvage Yard & Vehicle Watch | ผู้เชี่ยวชาญ spotting เป้ารถ salvage และ loot ที่คุ้มค่า |
| **Tony** | Nightclub & Warehouse | วิเคราะห์รายได้ Nightclub และการจัดการ Warehouse |
| **Ron** | เนื้อเรื่อง & เรื่องเล่า | นักเล่าเรื่องเชิงดราม่า |
| **Lester** | สังเคราะห์ & ประสานงาน | นักวางกลยุทธ์และรวบรวมรายงาน |
| **Pavel** | Data Curation | จัดการข้อมูล weekly และแปลงเป็น schema v2 |
| **Vincent** | Schema Validation | ตรวจสอบความถูกต้องของ payload และ field structure |

---

## สถานะโครงการปัจจุบัน

ที่เก็บนี้ใช้ `schema v2` เป็น canonical weekly planning payload สำหรับกรอบงานการจัดการหลายเอเย่นต์

- เอกสารใน `agents/` อธิบาย role และ prompt ของแต่ละ agent
- `agents/docs/` เก็บ schema/reference สำหรับ logic ของ agent
- `agents/data/` เก็บ machine-readable runtime datasets สำหรับ agent ที่ต้องใช้ catalog เพิ่มเติม
- ตัวอย่าง payload หลักอยู่ที่ `data/schema_v2_example.json`
- สคริปต์ Python ฝั่ง `scripts/` ถูกปรับให้ consume `schema v2` และ emit structured outputs ก่อน markdown

### Copilot Entry Points

| NPC | Prompt | Custom Agent |
|-----|--------|--------------|
| Michael | [`michael-weekly-analysis.prompt.md`](.github/prompts/michael-weekly-analysis.prompt.md) | [`michael-weekly-analysis.agent.md`](.github/agents/michael-weekly-analysis.agent.md) |
| Franklin | [`franklin-vehicle-analysis.prompt.md`](.github/prompts/franklin-vehicle-analysis.prompt.md) | [`franklin-vehicle-analysis.agent.md`](.github/agents/franklin-vehicle-analysis.agent.md) |
| Trevor | [`trevor-combat-value.prompt.md`](.github/prompts/trevor-combat-value.prompt.md) | Prompt only |
| Agent 14 | [`agent14-operations-analysis.prompt.md`](.github/prompts/agent14-operations-analysis.prompt.md) | [`agent14-operations-analysis.agent.md`](.github/agents/agent14-operations-analysis.agent.md) |
| Lamar | [`lamar-crew-analysis.prompt.md`](.github/prompts/lamar-crew-analysis.prompt.md) | Prompt only |
| Tony | [`tony-passive-income-analysis.prompt.md`](.github/prompts/tony-passive-income-analysis.prompt.md) | [`tony-passive-income-analysis.agent.md`](.github/agents/tony-passive-income-analysis.agent.md) |
| Ron | [`ron-weekly-story.prompt.md`](.github/prompts/ron-weekly-story.prompt.md) | Prompt only |
| Lester | [`lester-weekly-summary.prompt.md`](.github/prompts/lester-weekly-summary.prompt.md) | [`lester-weekly-summary.agent.md`](.github/agents/lester-weekly-summary.agent.md) |
| Pavel | [`pavel-weekly-data-curation.prompt.md`](.github/prompts/pavel-weekly-data-curation.prompt.md) | [`pavel-weekly-data-curation.agent.md`](.github/agents/pavel-weekly-data-curation.agent.md) |
| Vincent | [`vincent-schema-validation.prompt.md`](.github/prompts/vincent-schema-validation.prompt.md) | [`vincent-schema-validation.agent.md`](.github/agents/vincent-schema-validation.agent.md) |

Prompt files อยู่ใน `.github/prompts/` และ custom agent files อยู่ใน `.github/agents/`

#### วิธีเรียกใช้งานใน Copilot

- เปิดแชท แล้วพิมพ์ `/` เพื่อค้นหา prompt ที่ต้องการ
- ลองพิมพ์ตัวอย่างเช่น `Michael`, `Franklin`, `Agent 14`, `Tony`, `Lester`, หรือ `Ron` เพื่อเลือกคำสั่งที่เกี่ยวข้อง
- หากต้องการใช้ mode agent ให้เลือก agent จาก picker เมื่อมีชื่อ `Michael Weekly Analysis`, `Franklin Vehicle Analysis`, `Agent 14 Operations Analysis`, `Tony Passive Income Analysis`, หรือ `Lester Weekly Summary`
- ถ้าต้องการใช้งานแบบ prompt-only ให้เลือก prompt ที่มีชื่อเดียวกันกับตารางด้านบน

---

## 📁 โครงสร้างโครงการ

```
GTA-V-Online-agency-plan/
├── agents/
│   ├── Agent.md                      # 📚 เอกสารกรอบงาน
│   ├── weekly_input_template.md      # 📝 แบบฟอร์มป้อนข้อมูลกิจกรรมรายสัปดาห์
│   ├── docs/                         # reference/schema สำหรับ agent logic
│   ├── data/                         # runtime datasets เฉพาะ agent
│   ├── npc/
│   │   ├── michael.md                # 📖 นักวิเคราะห์เชิงกลยุทธ์และการเงิน
│   │   ├── franklin.md               # 📖 นักวิเคราะห์ Prize Ride & Test Ride
│   │   ├── trevor.md                 # 📖 นักวิเคราะห์ความโกลาหลและความเสี่ยง
│   └── npc/
│       ├── agent14.md                # 📖 นักวิเคราะห์ปฏิบัติการและประสิทธิภาพ
│       ├── lamar.md                  # 📖 นักวิเคราะห์สังคมและกิจกรรมทีม
│       ├── tony.md                   # 📖 นักวิเคราะห์รายได้ Nightclub และการจัดการ Warehouse
│       ├── lester.md                 # 📖 ผู้ประสานหลักและสรุปประจำสัปดาห์
│       ├── ron.md                    # 📖 ผู้เล่าเรื่องประจำสัปดาห์
│       ├── pavel.md                  # 📖 นักจัดการข้อมูลรายสัปดาห์และ schema v2
│       ├── vincent.md               # 📖 นักตรวจสอบ schema payload
├── data/
│   ├── sample_week.json              # ตัวอย่างโครงสร้างข้อมูลรายสัปดาห์
│   └── weekly_activity_template.json # ตัวอย่างเทมเพลตป้อนข้อมูล
├── requirements.txt                  # ข้อมูลการพึ่งพา
├── .env.example                      # เทมเพลตตัวแปรแวดล้อม (เชิงแนวคิด)
└── README.md                         # ไฟล์นี้
```

---

## 🏗️ สถาปัตยกรรมระบบ

### โฟลว์การวิเคราะห์แบบหลายเอเย่นต์

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
  Pavel   Vincent  Michael   Franklin
 (Normalize) (Validate) (Finance) (Vehicles)
             │         │          │
             │         │          │
             ▼         ▼          ▼
           Trevor   Agent14   Lamar
          (Chaos)  (Operations) (Salvage)
             │         │          │
             └────┬────┴────┬─────┘
                  │         │
                  ▼         ▼
                 Tony      Ron
               (Nightclub)(Story)
                  │         │
                  └────┬────┘
                       │
                  ┌────▼─────────┐
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
```        └───────────────────┘
```

### โมเดลการแยกการทำงาน

แต่ละเอเย่นต์:
- รับข้อมูลดิบรายสัปดาห์เหมือนกัน
- ประมวลผลผ่านเลนส์บุคลิกภาพของตัวเอง
- สร้างผลวิเคราะห์เป็นเอกสารอิสระ
- ไม่มีการสื่อสารโดยตรงระหว่างเอเย่นต์
- ผลลัพธ์ทั้งหมดถูกรวบรวมโดย Lester

---

## 🎯 วิธีการทำงาน

### ขั้นตอน 1: โหลดข้อมูล
กรอบงานโหลดและตรวจสอบความถูกต้องของข้อมูลกิจกรรมรายสัปดาห์ในรูปแบบ JSON

### ขั้นตอน 2: เตรียมและวิเคราะห์
- **Pavel** และ **Vincent** ทำหน้าที่ support agents: normalize และ validate payload ก่อนการวิเคราะห์
- **7 เอเย่นต์เฉพาะทาง** ทำหน้าที่วิเคราะห์ข้อมูลอย่างอิสระ
- แต่ละตัวใช้กรอบการวิเคราะห์เฉพาะตัว
- แต่ละตัวส่งรายงานเฉพาะทางของตนเอง

### ขั้นตอน 3: รวบรวมผล
- **Lester Crest** รับรายงานจาก agent ทุกตัว
- ระบุรูปแบบความเห็นสอดคล้องกัน
- เน้นความแตกต่างและข้อแลกเปลี่ยน
- สร้างสรุปเชิงบริหาร

### ขั้นตอน 4: สร้างรายงาน
- บันทึกรายงานร่วมเป็น Markdown
- รวมมุมมองจากเอเย่นต์ทั้งหมด
- จัดลำดับความสำคัญเชิงกลยุทธ์
- ให้คำแนะนำที่ปฏิบัติได้จริง

---

## 📖 ความเชี่ยวชาญของเอเย่นต์

### Michael De Santa – การวิเคราะห์ทางการเงิน
- **โฟกัส**: กำไร, ROI, ประสิทธิภาพ, กลยุทธ์การเงิน
- **คำถาม**: เราทำกำไรได้เท่าไหร่? คุ้มหรือไม่? ต่อชั่วโมงเป็นอย่างไร?
- **ผลลัพธ์**: การแยกวิเคราะห์การเงิน, ประเมินกำไร, คำแนะนำเชิงกลยุทธ์
- **เอกสาร**: [michael.md](agents/npc/michael.md)

### Franklin Clinton – Vehicle Opportunity Analyst
- **โฟกัส**: วิเคราะห์ `weekly_content.vehicle_opportunities`, Prize Ride, Test Ride, และรถลดราคาที่ควรให้ความสำคัญ
- **คำถาม**: รถใดเป็น limited unlock? คันไหนคุ้มกับเป้าหมายสัปดาห์นี้? รถใดเหมาะกับ time trial หรือ race?
- **ผลลัพธ์**: รายการรถที่ควร prioritize, การประเมินความคุ้มค่า, และคำแนะนำเชิงซื้อ/ปลดล็อก
- **เอกสาร**: [franklin.md](agents/npc/franklin.md)

### Trevor Philips – Weapons, Gear & Combat Value
- **โฟกัส**: ของฟรีจาก Gun Van, ส่วนลดอาวุธ, และรถที่เพิ่มความพร้อมเชิงต่อสู้
- **คำถาม**: ของฟรีใดต้องรีบเก็บ? ส่วนลดไหน useful จริง? GTA+ เปลี่ยนความคุ้มค่าอย่างไร?
- **ผลลัพธ์**: รายการ must-claim, buy/skip guidance, และการจัดลำดับความสำคัญเชิง combat
- **เอกสาร**: [trevor.md](agents/npc/trevor.md)

### Agent 14 – การวิเคราะห์ปฏิบัติการ
- **โฟกัส**: ความสำเร็จของภารกิจ, ประสิทธิภาพปฏิบัติการ, ตัวชี้วัด
- **คำถาม**: ปฏิบัติการเป็นระเบียบไหม? อัตราความสำเร็จเท่าไหร่? มีประสิทธิภาพหรือไม่?
- **ผลลัพธ์**: ตัวชี้วัด KPI, การประเมินเชิงกลยุทธ์, คำแนะนำปรับปรุง
- **เอกสาร**: [agent14.md](agents/npc/agent14.md)

### Lamar Davis – Salvage Yard & Vehicle Watch
- **โฟกัส**: เป้ารถ Salvage Yard, loot value, และ vehicle watch opportunities
- **คำถาม**: เป้ารถ salvage ใดคุ้มค่าที่สุด? ภารกิจไหนควรไล่? รถไหนควรเก็บหรือข้าม?
- **ผลลัพธ์**: แนะนำ salvage targets, แยก pickup/avoid, และให้การประเมินมูลค่ารถ
- **เอกสาร**: [lamar.md](agents/npc/lamar.md)

### Tony – การวิเคราะห์ Nightclub และ Warehouse
- **โฟกัส**: คำนวณรายได้ Nightclub ต่อสัปดาห์, การจัดการสต็อก Warehouse, การจัดสรรงานสำหรับ Technicians
- **คำถาม**: รายได้ Nightclub เท่าไหร่? สต็อกเพียงพอหรือไม่? Technicians ควรกระจายงานอย่างไร?
- **ผลลัพธ์**: รายงานรายได้สัปดาห์, แผนหมุนเวียนสต็อก, ตารางงาน Technicians
- **เอกสาร**: [tony.md](agents/npc/tony.md)

### Ron Jakowski – การวิเคราะห์เนื้อเรื่อง
- **โฟกัส**: โครงเรื่อง, การพัฒนาตัวละคร, ช่วงดราม่า, ความหมาย
- **คำถาม**: เรื่องราวคืออะไร? ตัวละครเติบโตไหม? มีจังหวะดราม่าอย่างไร?
- **ผลลัพธ์**: สรุปเนื้อเรื่อง, การพัฒนาตัวละคร, ธีมหลัก
- **เอกสาร**: [ron.md](agents/npc/ron.md)

### Lester Crest – การประสานงานและสรุป
- **โฟกัส**: สังเคราะห์มุมมองทั้งหมด, ลำดับความสำคัญเชิงกลยุทธ์, สรุปเชิงบริหาร
- **คำถาม**: ภาพรวมทั้งหมดคืออะไร? อะไรสำคัญที่สุด?
- **ผลลัพธ์**: สรุปหลายมุมมอง, การวิเคราะห์ความเห็นสอดคล้อง, ลำดับความสำคัญเชิงกลยุทธ์
- **เอกสาร**: [lester.md](agents/npc/lester.md)

### Pavel – Data Curation Support
- **โฟกัส**: normalize weekly input, map raw data to schema v2, identify missing or malformed fields
- **คำถาม**: ข้อมูลนี้อยู่ในรูปแบบ schema v2 หรือยัง? ต้องแก้ไขอะไรบ้างก่อนวิเคราะห์?
- **ผลลัพธ์**: candidate payload skeleton และ missing field checklist
- **เอกสาร**: [pavel.md](agents/npc/pavel.md)

### Vincent – Schema Validation Support
- **โฟกัส**: validate payload structure, field types, canonical naming, and schema integrity
- **คำถาม**: payload นี้ถูกต้องสำหรับ agent analysis หรือไม่? มี field ไหนต้องแก้?
- **ผลลัพธ์**: validation report, errors, warnings, และ repair instructions for Pavel
- **เอกสาร**: [vincent.md](agents/npc/vincent.md)


---

## 📊 รูปแบบเอาต์พุต

รายงานจะถูกสร้างเป็น **ไฟล์ Markdown** โดยมีโครงสร้างดังนี้:

```markdown
# Weekly Report – [Week & Date Range]

## Executive Summary
[Overview of the week across all dimensions]

## Agent Analyses
- Michael's Financial Assessment
- Franklin's Progression Report
- Trevor's Risk & Entertainment Analysis
- Agent 14's Operational Review
- Lamar's Salvage Yard Report
- Tony's Nightclub & Warehouse Assessment
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

## 🚨 การจัดการข้อผิดพลาด

กรอบงานนี้มีการจัดการข้อผิดพลาดอย่างแข็งแกร่ง:

- **การล้มเหลวของเอเย่นต์แต่ละตัวไม่ทำให้ระบบล่ม**
- **ข้อผิดพลาดถูกแยกและบันทึก**
- **ยังดำเนินการต่อกับเอเย่นต์ที่เหลือได้**
- **มีโหมดออฟไลน์เป็นทางเลือกสำรอง**
- **บันทึกข้อผิดพลาดอย่างละเอียดเพื่อการดีบัก**

ดูเพิ่มเติมได้ที่ [Agent.md – Error Handling](agents/Agent.md#-error-handling)

---

## 🧪 สถานะ

ที่เก็บนี้ใช้ `schema v2` เป็นศูนย์กลางของ weekly planning workflow และมี runtime scripts สำหรับอ่าน payload, generate structured reports, และ aggregate ผลลัพธ์

ไฟล์ Markdown ต่าง ๆ อธิบายสถาปัตยกรรมกรอบงาน บทบาทเอเย่นต์ เวิร์กโฟลว์การวิเคราะห์ และแนวคิดการบูรณาการ

ดูสถาปัตยกรรมฉบับเต็มได้ที่ [Agent.md](agents/Agent.md)

---

## 💡 แนวคิดสำคัญ

### สภาพแวดล้อมแยกการทำงาน
แต่ละเอเย่นต์ทำงานแยกอย่างสมบูรณ์ รักษา prompt ระบบ/ผู้ใช้ของตัวเอง และสร้างการวิเคราะห์เป็นอิสระ นี่ช่วยให้ได้การวิเคราะห์หลายมุมมองที่เป็นของจริง

### ฉันทามติหลายมุมมอง
ฉันทามติที่แข็งแรง (เอเย่นต์ 5 ตัวขึ้นไปเห็นตรงกัน) เป็นสัญญาณความเชื่อมั่นสูง ความแตกต่างช่วยเปิดเผยด้านต่าง ๆ ของการตัดสินใจ

### การวิเคราะห์โดยบุคลิกภาพ
แต่ละเอเย่นต์ใส่น้ำหนักจากบุคลิก:
- Michael ให้ความสำคัญกับกำไร
- Franklin ให้ความสำคัญกับ vehicle opportunities และ limited unlocks
- Trevor ให้ความสำคัญกับ combat value, freebies, และของที่ใช้งานได้จริง
- ฯลฯ

สิ่งนี้สร้างมุมมองตัวละครที่ผู้ใช้สามารถเลือกถ่วงน้ำหนักตามความสำคัญของตนเอง

### การรวมและสังเคราะห์
Lester Crest สังเคราะห์มุมมองทั้งหมดเป็นคำแนะนำที่สมดุลและปฏิบัติได้จริง โดยเคารพทุกมุมมองของเอเย่นต์

---

## 📝 ใบอนุญาต

โครงการนี้เป็นส่วนหนึ่งของ GTA V Online Agency Plan initiative (Community Project)

---

## 🤝 การมีส่วนร่วม

สำหรับการมีส่วนร่วม กรุณา:
1. แก้ไขไฟล์เอกสาร `.md` ที่เกี่ยวข้อง
2. อัปเดตเอกสารถ้ามีการเปลี่ยนแปลงการออกแบบ  
3. รักษาความเป็นเอกลักษณ์ของบุคลิกเอเย่นต์
4. ปฏิบัติตามแนวทางโครงสร้างโครงการ

---

## 📚 อ่านเพิ่มเติม

- **[Agent.md](agents/Agent.md)** - สเปคกรอบงานฉบับสมบูรณ์
- **[Michael's Analysis](agents/npc/michael.md)** - กรอบงานการเงิน
- **[Franklin's Analysis](agents/npc/franklin.md)** - Vehicle opportunity analysis and weekly unlock prioritization
- **[Trevor's Analysis](agents/npc/trevor.md)** - Weapons, gear, and combat-value analysis
- **[Agent 14's Analysis](agents/npc/agent14.md)** - กรอบงานปฏิบัติการ
- **[Lamar's Analysis](agents/npc/lamar.md)** - Salvage Yard
- **[Tony's Analysis](agents/npc/tony.md)** - Nightclub & Warehouse
- **[Ron's Analysis](agents/npc/ron.md)** - กรอบงานเนื้อเรื่อง
- **[Lester's Analysis](agents/npc/lester.md)** - กรอบงานการสังเคราะห์

---

**Framework Version**: Multi-Agent Orchestration v2.0  
**Last Updated**: 2026-04-07  
**Status**: ✅ Schema v2 พร้อมใช้งานกับเอกสารและ runtime หลัก

---

## 🧪 การทดสอบ

---

## ⚙️ ตัวแปรแวดล้อม

runtime ปัจจุบันไม่ต้องใช้ environment variables เพื่อรันตัวอย่าง `schema v2` ในเครื่อง

---

## 📄 ตัวอย่างเอาต์พุต

รายงานจะถูกบันทึกเป็นไฟล์ Markdown และ structured JSON ใน `reports/` เช่น:

```
reports/report_michael_week_sample.md
reports/structured/michael_report.json
```

ประกอบด้วยการวิเคราะห์จากทุกเอเย่นต์ที่รัน โดยแต่ละส่วนมีสไตล์และมุมมองตามบุคลิก GTA V

---

## 🔧 ขยายกรอบงาน

หากต้องการขยายกรอบงาน:

1. สร้างหรืออัปเดตเอกสารเอเย่นต์ใน `agents/npc/`
2. กำหนดโปรไฟล์ เอเย่นต์ บทบาท บุคลิกภาพ และกรอบการวิเคราะห์
3. บันทึกโครงสร้างเอาต์พุตที่คาดหวังและตัวอย่างบทสนทนา
4. อธิบายจุดเชื่อมต่อการรวม ระบบตัวชี้วัด และกรณีใช้งาน
5. รักษาความสอดคล้องของการออกแบบกับสไตล์เอกสารปัจจุบัน
