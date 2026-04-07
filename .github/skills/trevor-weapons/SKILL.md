# Trevor Weapons Skill

Summary
-------
This skill provides a concise, actionable reference of weapon categories, typical loadouts, and tactical recommendations tailored for Trevor (combat-focused persona) when analyzing or advising about in-game engagements in GTA V.

When to use
-----------
- Use this skill when a user asks Trevor-style advice about weapons, loadouts, or combat tactics.
- Use when converting a weapons list (e.g., wiki pages) to practical recommendations for missions, heists, or general combat.

Constraints
-----------
- Keep outputs concise and practical; avoid verbatim copying of large copyrighted texts.
- Prefer summary, comparisons, and actionable recommendations rather than raw dump of tables.
- Note source attribution: original reference is the GTA Fandom weapons listing.

Approach
--------
1. Map canonical weapon categories to short descriptions: melee, handguns, shotguns, SMGs, assault rifles, LMGs, sniper rifles, heavy weapons, explosives, and throwables.
2. For each category provide: short description, typical in-game roles, and 1–2 Trevor-recommended picks with a short rationale (e.g., "high DPS, close-quarters, silenced").
3. Offer 2–3 preset loadouts tailored to common Trevor scenarios: "Rampage / Chaos", "Heist Stealth", "Long-Range Support".
4. Include quick notes on ammo, vehicle usage, and sticky explosives when relevant.

Output Format
-------------
Return a JSON object with these keys:

- `agent`: "trevor-weapons"
- `summary`: one-paragraph Thai summary of weapon guidance
- `categories`: array of objects `{ "category": "shotgun", "desc": "...", "recommended": ["Weapon A","Weapon B"], "notes": "..." }`
- `loadouts`: array of named loadouts with weapon IDs and short reasons
- `references`: list of source URLs or short citations

Example use-cases
-----------------
- User: "Trevor, what should I bring for close-quarters heist?" → skill returns a close-quarters loadout and short reasoning in Trevor voice (Thai).
- User: "Summarize explosive options for vehicle ambushes" → skill returns explosives summary and tactical tips.

References
----------
- Primary source used for knowledge mapping: https://gta.fandom.com/wiki/Weapons_in_GTA_V (summarized and transformed)

Notes for maintainers
--------------------
- This skill intentionally summarizes and transforms the source wiki to avoid large verbatim excerpts.
- If you want verbatim tables or full specs, add a separate data file under `agents/data/` and reference it from prompt or agent workflows.

Detailed weapon recommendations (concise)
----------------------------------------
ด้านล่างเป็นสรุปแนะนำอาวุธที่ Trevor จะใช้ตามสถานการณ์ — แต่ละข้อเป็นสรุปเชิงปฏิบัติ (ไม่ใช่ตารางสเป็คถอดตรงจากแหล่ง):

- **ปืนสั้น (Handguns)**:
	- *Combat Pistol* — สมดุล, รีโหลดเร็ว, เหมาะต่อสู้ระยะประชิดทั่วไป.
	- *AP Pistol* — โหมดอัตโนมัติ (หรือเวอร์ชันที่ยิงเร็ว) ดีสำหรับการต่อสู้ภายในรถหรือการปะทะสั้น ๆ.
	- *Heavy Revolver / .50 Pistol* — ความเสียหายสูง เหมาะสำหรับเจาะเกราะหรือล้มศัตรูที่บึกบึน.

- **ปืนลูกซอง (Shotguns)**:
	- *Pump / Combat Shotgun* — ความเสียหายสูงระยะประชิด ดีในการจู่โจมห้องหรือรถติด.
	- *Assault Shotgun* — แม็กกาซีนใหญ่กว่า อัตราการยิงสูงขึ้น เหมาะโหมด Rampage.

- **SMG (Submachine Guns)**:
	- *SMG / Micro SMG* — พกพาสะดวก ในยานพาหนะหรือพื้นที่แคบ; สมดุลความเร็ว/ความแม่น.
	- *Combat PDW* — ความแม่นและอัตราการยิงดี เหมาะเล่น aggressor.

- **ปืนจู่โจม (Assault Rifles)**:
	- *Special Carbine / Carbine Rifle* — ตัวเลือกมาตรฐาน: แม่น, รีคอยล์จัดการได้, เหมาะสลับระยะกลาง/ไกล.
	- *Assault Rifle* — มักเป็นตัวเลือกสำรองเมื่อต้องการแม็กกาซีนใหญ่.

- **ปืนกลเบา (LMG)**:
	- *Combat MG / MG* — ไฟร์ยาวต่อเนื่อง เหมาะวางป้อมไฟหรือฝ่าวงล้อม; ระวัง mobility ลดลง.

- **ปืนซุ่ม (Sniper / Marksman)**:
	- *Marksman Rifle* — เซมิออโต้ เหมาะสำหรับการสนับสนุนระยะไกลและถ่ายเป้าหมายต่อเนื่อง.
	- *Heavy Sniper* — ความเสียหายสูง เหมาะเจาะยานพาหนะหรือศัตรูเกราะ.

- **อาวุธหนัก & ระเบิด**:
	- *RPG* — ทำลายยานพาหนะ/เฮลิคอปเตอร์ได้ดี
	- *Grenade Launcher* — ประสิทธิภาพพื้นที่ เหมาะกับการเคลียร์ฝูง
	- *Sticky Bomb* — ยืดหยุ่นสำหรับกับดัก/ดักรถ

- **ขว้าง / ระเบิดมือ**:
	- *Grenade* — ระเบิดพื้นที่มาตรฐาน
	- *Molotov* — ดีสำหรับการบล็อกเส้นทาง/สร้างความโกลาหล

- **ระยะประชิด / มีด / ไม้**:
	- *Knife, Baseball Bat, Crowbar* — ทักษะระยะประชิด หรือสถานการณ์ที่ต้องการความเงียบ (มีด)

Quick tactical notes:

- สำหรับการปะทะในรถ: พก *SMG* หรือ *AP Pistol* (ความคล่องตัวสูง)
- สำหรับดวลระยะกลาง/ไกล: ใช้ *Carbine/Special Carbine* + *Marksman/Heavy Sniper* เป็นคู่
- เข้าห้อง/บุก: พก *Shotgun* + *SMG* หรือรองด้วย *Sticky Bomb* สำหรับดักการหลบ
- ป้องกันตัวบนยานพาหนะ: *RPG* หรือ *Grenade Launcher* สำหรับภัยจากยาน

Preset Trevor loadouts (ชื่อไทย + อธิบายสั้น ๆ)

- "Rampage / Chaos": `Assault Shotgun` + `Combat MG`/`Minigun` + `Sticky Bombs` — ทำความเสียหายสูงระยะประชิดและพื้นที่
- "Heist Stealth": `Suppressor SMG`/`AP Pistol (มีซัพเพรสเซอร์)` + `Marksman Rifle` + `Knife` — เงียบและมีระยะสำรอง
- "Long-Range Support": `Heavy Sniper` + `Carbine Rifle` + `Grenade Launcher` — เจาะเป้า/สนับสนุนจากระยะปลอดภัย

Ammo & utility:

- แนะนำสำรองกระสุนสำหรับปืนหลัก และมี *Sticky Bomb* / *Grenade* ไว้ 2–4 ชิ้นสำหรับกับดักหรือทำลายยาน
- ถ้ามีตัวเลือกซัพเพรสเซอร์ ให้ใช้ตอนต้องการ stealth; ถ้าเน้นพังยานพาหนะ ให้แลกเป็น rounds ที่แรงขึ้น

References
----------
- แยกย่อและสังเคราะห์จากรายการอาวุธทั่วไป (สรุปจากแหล่งสาธารณะเช่น GTA Fandom) — https://gta.fandom.com/wiki/Weapons_in_GTA_V
