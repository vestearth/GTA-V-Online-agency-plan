# Quickstart: วิธีใช้งานสัปดาห์ถัดไป

คู่มือสั้นสำหรับรัน workflow รายสัปดาห์ของโปรเจกต์นี้ให้ตรงกับโครงปัจจุบันของ repo

ก่อนเริ่มทุกครั้ง:
- อ่านกติกากลางใน `AGENTS.md`
- อัปเดต `data/player_profile.json` ให้ตรงกับบัญชีของคุณ
- ถ้ามี weekly payload ใหม่ ให้ใช้รูปแบบชื่อ `data/weekly_planning_<year>_w<week>.json`

ตัวอย่าง:
- `data/weekly_planning_2026_w22.json`
- `reports/weekly_master_plan_2026_w22.md`

---

## ทางลัดที่แนะนำ

ลำดับที่ใช้งานจริงใน repo นี้คือ:

1. scrape หรือเตรียม weekly payload
2. ให้ AI รัน `src/workflows/weekly_planning.yaml`
3. สร้างรายงานลง `reports/`
4. อัปเดต dashboard ด้วย `scripts/generate_dashboard.py`

---

## แบบที่ 1: มี URL ข่าวประจำสัปดาห์

ถ้ามี Rockstar Newswire หรือ Reddit thread แล้ว ให้เริ่มจาก scrape:

```bash
python3 scripts/scrape_weekly_update.py --url "https://www.rockstargames.com/newswire/article/..."
```

หรือ

```bash
python3 scripts/scrape_weekly_update.py --url "https://www.reddit.com/r/gtaonline/comments/..."
```

สิ่งที่ควรได้หลังจบขั้นนี้:
- weekly payload ใหม่ใน `data/`
- ข้อมูลตั้งต้นที่พร้อมส่งเข้า workflow

จากนั้นให้ใช้ prompt ลักษณะนี้กับผู้ช่วย AI:

> "นี่คือ weekly payload ใหม่ของ GTA Online ช่วยรันตาม `src/workflows/weekly_planning.yaml` โดยใช้อ้างอิง `AGENTS.md`, `.github/skills/gta-weekly-planning/SKILL.md`, `data/player_profile.json` และ `data/examples_bundle.json` ด้วย แล้วสรุปรายงานแบบ Lester ลง `reports/` ให้ครบ 3 ไฟล์ของสัปดาห์นี้ ได้แก่ `weekly_master_plan_<week_id>.md`, `weekly_master_plan_<week_id>_income_scenarios.md`, และ `event_master_plan_<week_id>.md`"

---

## แบบที่ 2: มี weekly payload JSON อยู่แล้ว

ถ้าคุณมีไฟล์อย่าง `data/weekly_planning_2026_w22.json` อยู่แล้ว ให้ข้ามขั้น scrape ได้เลย

ใช้ prompt นี้:

> "รัน `src/workflows/weekly_planning.yaml` โดยใช้ `data/weekly_planning_2026_w22.json` กับ `data/player_profile.json` แล้วสรุปผลเป็นรายงานของ Lester ลง `reports/` ให้ครบ 3 ไฟล์ พร้อม time buckets, action queue, และ discount snapshot ที่ไม่ตกหล่น"

สิ่งที่รายงานควรมี:
- `What to Play`
- `What to Buy`
- `What to Ignore`
- time buckets (`30m`, `1-2h`, `3h+`)
- ordered action queue
- weekly discounts ครบทุก tier ที่มีจริงใน payload

---

## แบบที่ 3: มีแค่ raw text

ถ้ายังไม่มี JSON และอยากให้ผู้ช่วยแปลงข้อมูลเองจากข้อความข่าว:

> "นี่คือข้อมูลอัปเดต GTA Online ประจำสัปดาห์: [วางข้อความดิบที่นี่] ช่วยแปลงเป็น weekly planning payload ตามโครงของโปรเจกต์นี้ แล้วรัน `src/workflows/weekly_planning.yaml` โดยใช้อ้างอิง `AGENTS.md`, `.github/skills/gta-weekly-planning/SKILL.md`, `data/player_profile.json` และ `data/examples_bundle.json` จากนั้นสร้างรายงานลง `reports/` ให้ครบ 3 ไฟล์"

หมายเหตุ:
- ถ้ามี discount data ต้องจัดลง `weekly_content.discounts`
- ถ้ามี showroom, test ride, prize ride, podium ให้แยกเป็น `vehicle_opportunities`
- อย่าเดาราคา, payout, หรือเงื่อนไข unlock ถ้า source ไม่ยืนยัน

---

## อัปเดต Dashboard

หลังได้ weekly payload และ reports แล้ว ให้ regenerate dashboard:

```bash
python scripts/generate_dashboard.py --check-markers
python scripts/generate_dashboard.py --dry-run
python scripts/generate_dashboard.py
```

ถ้าจะบังคับใช้ไฟล์สัปดาห์ใดสัปดาห์หนึ่ง:

```bash
python scripts/generate_dashboard.py --weekly data/weekly_planning_2026_w22.json
```

เปิด dashboard:

```bash
open dashboard.html
```

Dashboard ปัจจุบันจะอัปเดตได้อย่างน้อย:
- header metadata
- summary cards
- weekly deals snapshot
- weekly vehicle spotlight
- current focus
- next claim / buy
- weekly action plan
- what to buy / ignore
- asset overview

ยังคงเป็น manual:
- ROI notes บางส่วน
- decision log

---

## คำสั่งที่มีประโยชน์

อัปเดตราคาอ้างอิงรถ:

```bash
python3 scripts/update_vehicle_prices.py
```

dry run:

```bash
python3 scripts/update_vehicle_prices.py --dry-run
```

ล็อก weekly file:

```bash
python3 scripts/update_vehicle_prices.py --weekly data/weekly_planning_2026_w22.json
```

---

## ตัวอย่าง prompt แบบเจาะเฉพาะเรื่อง

### Franklin: รถประจำสัปดาห์

> "ให้ Franklin ช่วยวิเคราะห์รถลดราคา, Test Track, Prize Ride, Podium, และ showroom vehicles ประจำสัปดาห์นี้จาก payload ที่ให้มา โดยอ้างอิง `src/agents/franklin.yaml` แล้วสรุปว่าคันไหนควรซื้อ คันไหนควรข้าม และคันไหนเป็นแค่ availability signal"

### Tony: ธุรกิจ passive

> "ให้ Tony Prince วิเคราะห์โบนัสและส่วนลดของธุรกิจ passive ประจำสัปดาห์นี้ โดยอ้างอิง `src/agents/tony.yaml` แล้วสรุปว่าควรโฟกัสธุรกิจไหนก่อน"

### Michael: ความคุ้มค่า

> "ให้ Michael ประเมิน ROI ของกิจกรรมและธุรกิจประจำสัปดาห์นี้ โดยอ้างอิง `src/skills/calculate_business_roi.yaml` แล้วจัดอันดับกิจกรรมที่คุ้มที่สุดตามเวลาเล่น"

---

## Checklist ของ weekly payload

ก่อนรัน workflow ควรเช็กว่าข้อมูลมีอย่างน้อย:

- `week.id` และ `week.label`
- `weekly_content.discounts`
- `weekly_content.vehicle_opportunities`
- `weekly_content.headline`
- `weekly_content.summary`

ถ้ามี discount data:
- ต้องเก็บครบทุก tier ที่มีจริง
- อย่าตัดรายการทิ้งเพียงเพราะไม่คิดว่าจะสำคัญ
- Gun Van ควรแยกเป็นกลุ่มของมันเอง

ถ้ามี vehicle opportunities:
- showroom/test ride/prize ride/podium เป็นคนละ signal กัน
- อย่าตีความว่าโชว์ใน showroom เท่ากับลดราคา
- อย่าตีความว่า Salvage Yard robbery vehicle จะ claim ได้ ถ้า source ไม่ยืนยัน

---

## Output ที่คาดหวัง

ต่อ 1 สัปดาห์ ควรมีรายงานหลักครบ 3 ไฟล์:

1. `reports/weekly_master_plan_<week_id>.md`
2. `reports/weekly_master_plan_<week_id>_income_scenarios.md`
3. `reports/event_master_plan_<week_id>.md`

และถ้ารัน dashboard generator ต่อ:

- `dashboard.html` ควรสะท้อน weekly payload ล่าสุด
- ถ้ามี unresolved prices หรือ ambiguous values ให้ generator รายงานเตือน ไม่เดาข้อมูล

---

## Tip

ถ้าคุณใช้ผู้ช่วย AI:
- ระบุ `src/workflows/weekly_planning.yaml`
- ระบุ `.github/skills/gta-weekly-planning/SKILL.md`
- ระบุ `AGENTS.md`
- ระบุ `data/player_profile.json`

จะช่วยให้ผลลัพธ์สม่ำเสมอและตรง guardrails ของโปรเจกต์มากขึ้น
