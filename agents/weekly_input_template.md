# Weekly Planning Input Template v2

ไฟล์นี้อธิบาย `schema v2` ซึ่งเป็น canonical input เดียวสำหรับทุก agent ในโปรเจกต์นี้ โดยออกแบบมาเพื่อ `pre-week planning` ของ GTA Online เป็นหลัก

## เป้าหมายของ schema v2

- ให้ทุก agent ใช้ section เดียวกันและหยุดพึ่ง field legacy ที่ไม่ตรงกัน
- แยก `weekly world state` ออกจาก `player/account state`
- ทำให้ recommendation เป็น personalized ได้จริง
- รองรับ missing data อย่างปลอดภัย โดย agent ต้องบอกว่า `insufficient_data` แทนการเดา

## Top-level shape

```json
{
  "schema_version": "2.0",
  "schema_mode": "weekly_planning",
  "week": {},
  "player_context": {},
  "planning_context": {},
  "weekly_content": {},
  "business_state": {},
  "crew_context": {},
  "analysis_hints": {},
  "data_quality": {}
}
```

## 1. `week`

metadata ของ payload สัปดาห์นั้น

- `id`: รหัสสัปดาห์ เช่น `2026-W14`
- `label`: ชื่อที่อ่านง่าย เช่น `April 2-9 2026`
- `start_date`, `end_date`: ISO date
- `source`: `rockstar_newswire` | `manual` | `mixed`
- `last_updated_at`: ISO datetime

## 2. `player_context`

ข้อมูลของ account ผู้เล่นเพื่อทำ recommendation แบบ personalized

- `player_name`: ชื่อผู้เล่น
- `platform`: `pc` | `ps5` | `xbox_series` | `unknown`
- `gta_plus`: `true` | `false` | `null`
- `rank`: ระดับตัวละคร
- `cash_on_hand`, `bank_balance`: เงินที่พร้อมใช้
- `play_style_tags`: แนวการเล่น เช่น `solo`, `grinder`, `combat`, `vehicle_collector`
- `goals_this_week`: เป้าหมายของสัปดาห์ เช่น `make_money`, `unlock_vehicle`, `passive_income`
- `owned_assets.properties`: ทรัพย์สิน/สิทธิ์เข้าถึง เช่น `agency`, `nightclub`, `ls_car_meet_membership`
- `owned_assets.businesses`: ธุรกิจที่มีจริง
- `owned_assets.key_vehicles`, `owned_assets.key_weapons`: ของสำคัญที่มีอยู่แล้ว
- `constraints.hours_available`: เวลาเล่นที่มีจริง
- `constraints.preferred_session_size`: `solo` | `1_2_friends` | `full_crew` | `any`
- `constraints.avoid_content_tags`: เนื้อหาที่ไม่อยากเล่น

## 3. `planning_context`

บริบทการตัดสินใจในสัปดาห์นี้

- `primary_objective`: `profit` | `vehicle_unlock` | `arsenal_upgrade` | `crew_fun` | `mixed`
- `budget_limit`: เพดานงบซื้อของ
- `risk_tolerance`: `low` | `medium` | `high`
- `session_plan`: ชุด block ของ session ที่วางไว้ล่วงหน้า
- `decision_policy.recommend_owned_only`: ถ้า `true` ให้แนะนำเฉพาะ content ที่ account เข้าถึงได้แล้ว
- `decision_policy.allow_new_purchases`: ถ้า `false` ห้ามเสนอแผนซื้อ
- `decision_policy.prioritize_limited_time_content`: ถ้า `true` ให้ content แบบ time-limited ได้ priority มากขึ้น

## 4. `weekly_content`

ส่วนนี้คือ Rockstar weekly event catalog ที่เป็นหัวใจของ `schema v2`

### 4.1 `featured_activities`

ใช้กับ Michael, Agent 14, Lamar, Ron, Lester

ฟิลด์หลัก:
- `id`, `name`
- `category`: `mission_bonus` | `weekly_challenge` | `race` | `time_trial` | `new_release` | `business_bonus` | `collectible`
- `content_type`: `active` | `passive` | `one_time` | `repeatable`
- `availability.start`, `availability.end`
- `bonus`: ตัวคูณที่ parse แล้ว เช่น `gta_cash_multiplier`, `rp_multiplier`, `gta_plus_cash_multiplier`
- `requirements`: สิ่งที่ต้องมี เช่น `agency`
- `recommended_party_size`: เช่น `solo`, `solo_or_duo`, `small_group`
- `timebox_minutes`
- `value_tags`: เช่น `money`, `crew_fun`, `limited_reward`, `new_content`
- `reward`: optional object
- `notes`: หมายเหตุที่ยังไม่ควรแปลงเป็น field แยก

### 4.2 `vehicle_opportunities`

ใช้กับ Franklin, Trevor, Lamar, Lester

รวม item ที่เดิมเคยกระจายอยู่ตาม `discounts`, `test rides`, `podium`, `prize ride`, `new vehicle`

ฟิลด์หลัก:
- `id`
- `vehicle_name`
- `opportunity_type`: `discount` | `prize_ride` | `podium` | `test_ride` | `premium_test_ride` | `new_release`
- `source`: `ls_car_meet` | `casino` | `warstock` | `legendary_motorsport` | `san_andreas_super_autos` | `salvage_yard` | `unknown`
- `availability`
- `discount_percent`, `price`, `trade_price`
- `class`
- `limited`
- `removed_vehicle`
- `gta_plus_only`
- `acquisition`: วิธีได้รถคันนั้น เช่น challenge หรือ claim path
- `evaluation_inputs.performance_score`
- `evaluation_inputs.test_metrics`: optional test ride metrics เช่น premium stability, lap time
- `evaluation_inputs.utility_tags`
- `evaluation_inputs.weaponized`
- `evaluation_inputs.service_vehicle`

### 4.3 `weapon_and_gear_opportunities`

ใช้กับ Trevor และ Lester

- `id`, `name`
- `opportunity_type`: `gun_van_free` | `gun_van_discount` | `armor_discount`
- `discount_percent`
- `gta_plus_only`
- `combat_role_tags`
- `urgency`: `must_claim` | `good_pick` | `optional` | `skip`
- `notes`

### 4.4 `business_opportunities`

ใช้กับ Michael, Agent 14, Tony

- `id`, `name`
- `business_type`: `nightclub` | `bunker` | `salvage_yard` | `agency` | `hangar` | `mc_business`
- `bonus`
- `requires_owned_business`
- `requirements`
- `estimated_value_tags`: เช่น `passive_income`, `active_grind`, `setup_required`
- `notes`

### 4.5 `time_trials_and_races`

ใช้กับ Franklin และ Michael

- `id`, `name`, `type`
- `vehicle_restrictions`
- `recommended_vehicle_classes`
- `reward`
- `notes`

### 4.6 `salvage_yard_targets`

ใช้กับ Lamar, Franklin, Lester

- `id`
- `robbery_name`
- `vehicle_name`
- `claimable`
- `salvage_value`
- `sell_value`
- `notes`

## 5. `business_state`

สถานะธุรกิจจริงของ account เพื่อให้ Tony และ Michael แนะนำได้ถูก

### 5.1 `nightclub`

- `owned`
- `safe_cash`
- `popularity_percent`
- `technicians_total`
- `technician_assignments`
- `goods_stock`
- `upgrade_flags`

### 5.2 `feeder_businesses`

array ของธุรกิจที่ feed เข้าระบบ passive income

- `business_type`
- `owned`
- `operational`
- `supply_level_percent`
- `stock_level_percent`
- `upgrade_flags`

## 6. `crew_context`

ข้อมูลทีมที่ใช้กับ Lamar, Agent 14, Ron และ Lester

- `crew_name`
- `active_members`
- `usual_party_size`
- `coordination_level`
- `notes`

ตัวอย่าง member entry:

```json
{
  "name": "PlayerA",
  "role_tags": ["pilot", "support"],
  "reliability": "medium"
}
```

## 7. `analysis_hints`

guardrails สำหรับทุก agent

- `missing_data_policy`: แนะนำใช้ `state_unknown_explicitly`
- `recommendation_style`: เช่น `ranked_list`
- `language`: เช่น `th`
- `max_recommendations`
- `must_cite_ids`

## 8. `data_quality`

meta ให้ agent รู้ว่าข้อมูลครบแค่ไหน

- `coverage.player_context_complete`
- `coverage.business_state_complete`
- `coverage.crew_context_complete`
- `known_gaps`
- `confidence_level`: `low` | `medium` | `high`

## Missing-data rules

- ถ้าไม่มี field ที่จำเป็น ห้ามเดาตัวเลข
- ถ้าไม่รู้ราคาหรือ payout ให้ใช้คำอธิบายเชิงคุณภาพแทน
- ถ้า recommendation ต้องอิง owned assets แต่ข้อมูลไม่ครบ ให้ตอบว่า `account_specific_check_required`
- ถ้าไม่มี `crew_context.active_members` ให้ Lamar/Ron/Agent 14 เปลี่ยนเป็นการวิเคราะห์สำหรับ solo/public lobby

## Agent mapping แบบย่อ

- `Michael`: `player_context`, `planning_context`, `featured_activities`, `business_opportunities`, `data_quality`
- `Franklin`: `vehicle_opportunities`, `time_trials_and_races`, `player_context.owned_assets`
- `Trevor`: `weapon_and_gear_opportunities`, `vehicle_opportunities`, `player_context.gta_plus`
- `Agent 14`: `featured_activities`, `business_opportunities`, `crew_context`, `planning_context.session_plan`
- `Lamar`: `crew_context`, `salvage_yard_targets`, `vehicle_opportunities`, `featured_activities`
- `Tony`: `business_state`, `business_opportunities`, `player_context.owned_assets`
- `Ron`: `week`, `planning_context`, `featured_activities`, `crew_context`
- `Lester`: ทั้ง payload และ structured outputs จาก agent อื่น

## Structured output contract

ทุก agent ควรตอบอย่างน้อยในรูปแบบนี้ก่อน prose/markdown:

```json
{
  "agent": "franklin",
  "summary": "...",
  "top_recommendations": [
    {
      "target_id": "ocelot_swinger_prize_ride",
      "action": "prioritize",
      "reason": "limited weekly unlock",
      "confidence": "medium"
    }
  ],
  "warnings": [],
  "insufficient_data": []
}
```

## ตัวอย่าง payload

ดู payload ตัวอย่างเต็มได้ที่ `data/schema_v2_example.json`