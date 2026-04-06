# Weekly Activity Input Template

ใช้ไฟล์นี้เป็นแบบฟอร์มข้อมูลกิจกรรมแต่ละสัปดาห์สำหรับให้ agent วิเคราะห์แยกกัน

## ส่วนที่ 1: Metadata ของสัปดาห์

- `week`: รหัสสัปดาห์ เช่น `2026-W15`
- `date_range`: ช่วงวันที่ของสัปดาห์
- `player`: ชื่อผู้เล่นหลัก
- `crew`: ชื่อทีมหรือแก๊ง
- `playtime_hours`: ชั่วโมงเล่นทั้งหมดในสัปดาห์

## ส่วนที่ 2: ข้อมูลการเงิน

- `financials.earnings_total`: รายได้รวมทั้งหมด
- `financials.expenses_total`: ค่าใช้จ่ายทั้งหมด
- `financials.net_profit`: กำไรสุทธิ
- `financials.currency`: สกุลเงิน เช่น `GTA$`

## ส่วนที่ 3: ภารกิจ (missions)

รายการภารกิจสำคัญที่ทำในสัปดาห์ เช่น heist, mission, event

แต่ละรายการมี:
- `name`: ชื่อภารกิจ
- `type`: ประเภทภารกิจ เช่น `Heist`, `Mission`, `Event`
- `status`: `Completed`, `Failed`, `Abandoned`
- `duration_hours`: เวลาที่ใช้
- `revenue`: รายได้จากภารกิจ
- `expenses`: ค่าใช้จ่ายที่เกิดขึ้น
- `participants`: รายชื่อผู้เล่นหรือสมาชิกทีม
- `outcome`: ผลลัพธ์หลัก
- `notes`: หมายเหตุเพิ่มเติม

## ส่วนที่ 4: กิจกรรมทั่วไป (activities)

เก็บกิจกรรมด้านความสนุกหรือการเล่นเสริม

แต่ละกิจกรรมมี:
- `name`: ชื่อกิจกรรม
- `category`: หมวด เช่น `Entertainment`, `Social`, `Training`
- `duration_hours`: เวลาที่ใช้
- `fun_score`: คะแนนความสนุก 1-10
- `team_participation`: จำนวนคนร่วมกิจกรรม
- `notes`: หมายเหตุเพิ่มเติม

## ส่วนที่ 5: สรุปทีม

- `crew_summary.members_active`: จำนวนสมาชิกที่ active
- `crew_summary.mvp`: คนที่ทำได้เด่นสุด
- `crew_summary.team_cohesion`: คะแนนความร่วมมือทีม 1-10
- `crew_summary.conflicts`: ปัญหาหรือความขัดแย้งสำคัญ

## ส่วนที่ 6: ไฮไลท์และบทเรียน

- `highlights`: จุดเด่นของสัปดาห์
- `lessons_learned`: บทเรียนที่ได้จากสัปดาห์นี้

## ตัวอย่างการใช้งาน

ดูตัวอย่างโครงสร้างที่ `data/weekly_activity_template.json`