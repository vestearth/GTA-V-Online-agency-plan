# การรับข้อมูลและกู้คืน automation

ใช้กับ Issues [#16](https://github.com/vestearth/GTA-V-Online-agency-plan/issues/16), [#17](https://github.com/vestearth/GTA-V-Online-agency-plan/issues/17), [#18](https://github.com/vestearth/GTA-V-Online-agency-plan/issues/18), [#19](https://github.com/vestearth/GTA-V-Online-agency-plan/issues/19), [#20](https://github.com/vestearth/GTA-V-Online-agency-plan/issues/20), [#21](https://github.com/vestearth/GTA-V-Online-agency-plan/issues/21)

## Weekly: curated-first

| สถานะ | ความหมาย | ผลต่อข้อมูลเผยแพร่ |
|---|---|---|
| `acquiring` | กำลังรับ source | ยังไม่เปลี่ยนคำแนะนำ |
| `needs_review` | บันทึก candidate แล้ว หรือ source/coverage ไม่พอ | เก็บข้อมูลยืนยันเดิมและแสดงคำเตือน |
| `confirmed` | curator ตรวจเนื้อหาและ coverage กับ source แล้ว | ยังต้องมี approval ของรายงาน |
| `generating` | ผ่าน publication gate กำลังสร้าง HTML ชั่วคราว | คง HTML คู่เดิมจนสร้างครบ |
| `published` | สร้างและเปลี่ยน Dashboard ทั้งสองแล้วใน workspace ของ run | Actions ยังต้อง commit/push สำเร็จจึงขึ้น Pages |
| `failed` | รับข้อมูล/สร้าง artifacts ไม่สำเร็จ | เก็บ status + คำเตือน; health monitor เปิด Issue |
| `pre_live` | simulation/ข้อมูลก่อนยืนยันจริง | ไม่ผ่าน publication gate |
| `stale` | หมด reset window | คำเตือนทั้งสอง Dashboard; ไม่ใช้เป็นคำแนะนำปัจจุบัน |

`data/refresh_status.json` เป็นหลักฐานสถานะ ไม่ใช่การรับรองว่าข้อมูลขึ้น Pages สำเร็จ
ตรวจผล commit/push ของ Actions เพิ่มด้วย หาก push ถูกปฏิเสธเพราะ remote เปลี่ยน ให้รันใหม่

### 1. รับ source ที่ตรง reset

Weekly Content Refresh รัน Thursday **13:00 UTC / 20:00 Bangkok** วันอ้างอิงคำนวณใน Asia/Bangkok
การเลือกเวลานี้เป็นระยะรอสำหรับเนื้อหาหลัง reset; ต้องตรวจ source date เสมอ ไม่ถือว่า cron สำเร็จเท่ากับ source ถูกสัปดาห์

กำหนด `--url` หรือ Actions input `newswire_url` ได้ และมี `WEEKLY_UPDATE_URL` เป็น fallback
URL ต้องเป็น HTTPS Rockstar Newswire article เท่านั้น แม้เป็น manual override ก็ยังผ่าน date/title/body validation

แหล่งสำรองคือ registry ที่แก้ไขและรีวิวใน `data/weekly_source_index.json`:

```json
{
  "articles": [{
    "week_id": "YYYY-WXX",
    "kind": "weekly",
    "state": "confirmed",
    "reviewer": "REVIEWER",
    "published_date": "YYYY-MM-DD",
    "url": "https://www.rockstargames.com/newswire/article/ARTICLE_ID/ARTICLE_SLUG"
  }]
}
```

ตัวอย่างเป็นรูปแบบ ไม่ใช่ source จริง ต้องใส่ค่าที่ตรวจแล้ว registry ถูกเก็บไว้ใน repo จึงอ่านได้โดยไม่พึ่ง listing HTML
หากไม่มี record ที่ตรงหรือมีมากกว่าหนึ่ง record จะหยุดพร้อม diagnostic
การค้นหา Newswire listing แบบเดิมยังอยู่สำหรับ fixture compatibility แต่ไม่อยู่ใน live resolver
ไม่มี undocumented API หรือการเดา URL จากคะแนน keyword

รองรับ JSON-LD `Article`/`NewsArticle`/`BlogPosting` ที่มี `datePublished`, `headline`, `articleBody`
หรือ visible `<article>` ที่มี `og:title` และ `article:published_time` ตัด script/navigation ออกก่อน regex
JS-only, title ของ GTA+ monthly, ไม่มี publication date, body ไม่พอ และ source เก่าจะหยุด
หาก Rockstar ไม่ส่ง article body ให้ client นี้ ต้องทำ curated intake จากแหล่งที่อ่านได้และตรวจอ้างอิงเอง
อย่าตีความ error เป็น weekly update ว่าง และอย่า mark `confirmed` เพียงเพราะพบ bonus หนึ่งรายการ

```bash
python scripts/run_weekly_content_refresh.py --url CURRENT_NEWSWIRE_ARTICLE_URL
```

candidate อยู่ใน `data/candidates/weekly_planning_<week_id>.json`
`provenance` เก็บ URL/title/publication date/fetch time/raw article SHA-256
`intake_issues` แจ้ง coverage ที่ขาด; parser ไม่รับรองว่ารายการที่พบครบทุกส่วนของบทความ
critical coverage ขั้นต่ำคือ bonuses, discounts, vehicle_opportunities และต้องผ่าน canonical schema
หากบทความไม่มีบางกลุ่มจริง ให้ curator บันทึกและตรวจข้อมูลก่อนแก้กติกา ไม่ใส่รายการปลอมเพื่อผ่าน gate

### 2. ตรวจและสร้างรายงาน

ตรวจ candidate กับบทความจริง โดยเฉพาะส่วนลดทั้งหมด, platform/edition, claim eligibility และแยก display/test ride ออกจาก purchase
ใช้ `src/workflows/weekly_planning.yaml` ตามลำดับเดิม: schema precheck → normalize activities → normalize vehicles → readiness gate → specialists → Lester
ขั้นตอนนี้ทำโดย assistant/curator และต้องผ่าน `validate_report_completeness` ไม่ใช่ regex scraper

สร้างรายงาน exactly 3 ไฟล์พร้อม week ID ใน heading แรก:

- `reports/weekly_master_plan_<week_id>.md`
- `reports/weekly_master_plan_<week_id>_income_scenarios.md`
- `reports/event_master_plan_<week_id>.md`

ไม่มี dummy Master Plan หรือ `weekly_report` เพิ่มใน weekly run
จากนั้น review handoff:

```bash
python scripts/review_weekly_candidate.py data/candidates/weekly_planning_YYYY_wXX.json --reviewer REVIEWER
```

คำสั่งนี้หมายถึง reviewer ตรวจข้อเท็จจริงและ canonical QA แล้ว ไม่ใช่คำสั่งรีวิวด้วย AI อัตโนมัติ
ตรวจ schema/window/coverage/report headings และบันทึก hash ของ payload และรายงานก่อน promote ไป `data/`
รายงานหลักต้องมี What to Play / What to Buy / What to Ignore / Action Queue
ควร commit approved payload และรายงานทั้งสามด้วย `git add -f` เพราะ `reports/` ถูก ignore
payload หรือ report เปลี่ยนหลัง review ต้อง review อีกครั้ง

### 3. เผยแพร่ชุดที่รีวิวแล้ว

```bash
python scripts/run_weekly_content_refresh.py --publish-reviewed
```

หรือ Actions `workflow_dispatch` ตั้ง `publish_reviewed: true`
หาก source ถูกแก้หลังอนุมัติ การ intake ซ้ำจะหยุดที่ `needs_review`; explicit publish ใช้ชุดที่ reviewer อนุมัติ
canonical data ที่ผิดสัปดาห์/ไม่ approved/รายงานไม่ครบหรือ hash เปลี่ยนไม่ผ่าน gate
ทั้งสอง generator ตรวจ gate ด้วยตนเอง จึงไม่เปลี่ยน header ใหม่โดยทิ้งคำแนะนำเก่าไว้
ส่วนที่ parse รายงานใหม่ไม่ได้จะเป็นข้อความรอข้อมูล ไม่คงคำแนะนำสัปดาห์ก่อน

การตรวจ hash เป็นหลักฐานชุด artifact ที่อนุมัติ ไม่ได้แทนการตรวจข้อเท็จจริงโดย curator

## Vehicle price recovery

ค่าเริ่มต้นใช้เฉพาะรถใน weekly payload ล่าสุดที่ยัง `base_price: null`
ต้องการสัปดาห์เฉพาะหรือ retry:

```bash
python scripts/update_vehicle_prices.py --weekly data/weekly_planning_YYYY_wXX.json
python scripts/fetch_gtacar_prices.py --weekly data/weekly_planning_YYYY_wXX.json --summary data/price_refresh_status.json
```

`--dry-run` ไม่ HTTP หรือเขียนไฟล์; `--refresh-all` ใช้กับการตรวจ historical catalog โดยตั้งใจ
กรอง property/decor เช่น Wonderama Arcade ออก การไม่มี Price ไม่ใช่หลักฐานว่า layout ทั้งเว็บเสีย
ข้อความ `Cannot be acquired` จัดเป็น non-purchasable และไม่ดึงตัวเลขจาก handling/sell value
ราคามีใน catalog ไม่ใช่การยืนยันว่ามี purchase path ในเกมสัปดาห์นี้; availability ยังจำกัด/ไม่ทราบได้
HTTP 503, slug ขาด, parser ไม่พบราคา และ non-purchasable มีเหตุผลแยกใน summary
ไม่ทราบราคาคง `null`; safe partial enrichment ไม่บล็อก valid weekly report
`--fail-on-skipped` ยังใช้สำหรับ diagnostic แบบ strict ได้ แต่ไม่ใช้ใน producer ประจำสัปดาห์

## GTA+ monthly intake

ตรวจตาม `membership_period.start_date/end_date` ไม่ใช้เดือนของ weekly reset แทน
`content-health.yml` ตรวจ rollover ทุกวันโดยอิสระจาก weekly refresh และเปิด Issue เมื่อไม่มี current reviewed period
รับ payload จากการวิจัย source ด้วยรูปแบบเดิมและเพิ่ม evidence ดังนี้:

```json
{
  "schema_mode": "gta_plus_monthly",
  "review_state": "confirmed",
  "review": {"reviewer": "REVIEWER"},
  "membership_period": {"start_date": "YYYY-MM-DD", "end_date": "YYYY-MM-DD", "source_urls": ["HTTPS_SOURCE"]},
  "monthly_benefits": {
    "claimable_vehicles": [{
      "vehicle": "VERIFIED_VEHICLE",
      "claim_method": "vinewood_car_club",
      "location": "VERIFIED_LOCATION",
      "review_state": "confirmed",
      "source_urls": ["HTTPS_SOURCE"],
      "eligibility": {"platform": "unknown", "edition": "unknown", "claim_scope": "unknown"}
    }]
  }
}
```

ทุก key benefit (vehicles/bonuses/discounts/freebies/standing perks) ต้องมี review/source/eligibility
review handoff บันทึก `review.payload_sha256` อัตโนมัติ; แก้ monthly payload หลังรีวิวต้อง review ใหม่ก่อนแสดง current perks
ยอด `gta_dollar_deposit` ต้องมี `deposit_evidence.review_state/source_urls`
`claim_method`: `login`, `vinewood_car_club`, `in_game_purchase`, `unknown` — อย่าเดาจาก item type
`pre_live`/`unknown` ไม่เป็น current confirmed perks และ unknown eligibility ไม่ใช่ universally available

```bash
python scripts/gta_plus_intake.py MONTHLY_CANDIDATE.json
python scripts/gta_plus_intake.py MONTHLY_CANDIDATE.json --reviewer REVIEWER
python scripts/refresh_dashboard_status.py
```

ทั้งสอง Dashboard ใช้ period selection เดียวกัน overlap/conflict จะไม่เลือกฝ่ายหนึ่งโดยเดาจากชื่อไฟล์
ไม่มี payload ปัจจุบันจะลบ perks เก่าออกจาก monthly block และแสดงรอข้อมูล รายงาน weekly ระบุ member/non-member แยก
`combine_weekly_bonuses` รับ effective multiplier เฉพาะ `weekly_overlay` ที่มี review/source/week/activity/reward/multiplier ตรงกัน
period ต้องครอบคลุม weekly window ทั้งหมด มิฉะนั้นให้แยกช่วงเวลาในการรีวิว ไม่สร้างตัวคูณทั้งสัปดาห์

## Profile v2

ใช้ `account` สำหรับยอดธนาคาร/entitlements/shared observations และ `characters` สำหรับคลัง/progress/prize claims/เงินตัวละคร
เลือก `active_character` หรือระบุตัวละครให้ชัดก่อน readiness/purchase; legacy profile ยังอ่านผ่าน `normalize_profile`
inventory เดิมย้ายไป main พร้อม `legacy_recorded`; secondary เป็น `partial_user_observation` เฉพาะ Mk II
ไม่ตีความ properties list ว่างของ secondary ว่าไม่เป็นเจ้าของแน่นอน และไม่โยกเงินเก่าไป account bank balance
top-level `owned_assets`/`bankroll` เป็น compatibility alias ของ main; ต้องให้ตรงกับ active view

Orange Shade Camo: `observed_available` บน main/secondary ตาม user in-game observation ใน Issue #21
เดือนที่สังเกตคือ October 2026; edition ไม่ทราบ ไม่มีหลักฐาน causal unlock, expiry หรือหลังยกเลิก GTA+
`confirmed_unlock_method` กับ `claim_scope` ยัง unknown การมี entitlement ไม่เท่ากับมีรถ/เคย claim บนทั้งสองตัวละคร
`cosmetic_available` ไม่แนะนำซื้อรถซ้ำเพื่อปลดล็อกลายที่ตรวจว่า secondary ใช้ได้แล้ว

## Monitoring และข้อจำกัดการทำงานจริง

ตรวจวันที่ 2026-10-14 ผ่าน GitHub Actions API พบ Weekly Content Refresh และ Auto Update Vehicle Prices เป็น `disabled_inactivity`
จึงยืนยันสาเหตุที่ไม่เห็น scheduled runs ใหม่ได้จาก state ไม่ใช่การเดาจาก error เก่า
หลังนำไฟล์ขึ้น main ให้ Enable Weekly Content Refresh และ Content Health ใน Actions
Auto Update Vehicle Prices เหลือ manual retry เท่านั้น

Health Issue มีชื่อคงที่ เปิดใหม่หรือ reopen เมื่อ failed/missing/disabled/current data pending review และปิดเมื่อฟื้นตัว
run absence ใช้ Thursday 16:00 UTC เป็น deadline (3 ชั่วโมงหลัง collection) และตรวจ event schedule
ทุก writer ใช้ concurrency เดียว ไม่มี rebase ที่ replay generated content ลง remote ใหม่กว่า
GitHub notification ขึ้นอยู่กับการ subscribe/watch; monitor นี้พึ่ง GitHub scheduler หากทุก scheduled workflow ถูกปิดก็ตรวจตัวเองไม่ได้
เบราว์เซอร์ยังตรวจวันหมดอายุของ weekly/GTA+ ให้โดยไม่ต้องรอ Actions และ daily status job ไม่เปลี่ยนคำแนะนำ

การทดสอบ offline ใช้ synthetic Newswire layouts ที่ระบุชัดว่าไม่ใช่ข้อมูลเกมจริง และ acquisition fragments จาก GTACars ที่เก็บวันที่ 2026-10-14
ยังต้องยืนยัน live current source และ monthly period ก่อนเผยแพร่คำแนะนำใหม่ ไม่สร้าง October benefits หรือ weekly payouts ขึ้นเอง
