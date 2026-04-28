## คู่มือสั้น ๆ: ลดค่าใช้จ่ายเมื่อใช้ระบบแบบ Usage-Based Billing

สรุปสั้นๆ เป็นข้อปฏิบัติที่ทำได้ทันทีเพื่อให้การใช้ LLM/API ประหยัดและคาดการณ์ได้สำหรับโปรเจกต์เกมนี้

1) ตรวจสอบและเก็บข้อมูลการเรียก (Instrumentation)
- เปิด logging กลางสำหรับทุกการเรียก LLM/HTTP: model, endpoint, prompt size (tokens), user, timestamp, duration, response size.
- เก็บเป็นไฟล์ CSV/JSON หรือส่งไปยังระบบมอนิเตอร์ (Prometheus/Datadog) เพื่อวิเคราะห์แนวโน้มค่าใช้จ่าย.

2) ใช้ caching สำหรับคำตอบที่คาดว่าจะซ้ำ
- แคชผลลัพธ์แบบ deterministic (key = hash(prompt + model + version + context_id)).
- เก็บบนดิสก์/SQLite/Redis แล้วให้โค้ดตรวจก่อนเรียก LLM.

3) แยกงานตามความสำคัญ — เลือกโมเดลถูก-แพงให้เหมาะสม
- งาน exploratory / ร่าง / bulk analysis → ใช้โมเดลราคาถูกกว่า (หรือ local model).
- งาน final synthesis / user-facing → ใช้โมเดลสูงกว่าหรือที่แม่นยำกว่า.

4) ลดขนาด context และผลรวม token
- สรุปข้อมูลยาว (summarize) ก่อนส่ง ถ้าไม่จำเป็นต้องมีรายละเอียดทั้งหมด.
- กำหนด `max_tokens` ที่เหมาะสมและใช้ temperature ต่ำถ้าไม่ต้องการความหลากหลาย.

5) Batching และ Debouncing
- รวมคำถามเล็ก ๆ หลายคำถามเป็นคำขอเดียว (batch) เมื่อเป็นไปได้.
- สำหรับเหตุการณ์ที่เกิดถี่ ให้ใช้ debounce/queue แล้วเรียกเป็นช่วงเวลา (e.g., ทุก 5 นาที).

6) กฎเชิงธุรกิจก่อนเรียก LLM
- ใส่ logic ในโค้ดเพื่อตัดสินใจ (if/then) ก่อนเรียก เช่น: ถ้ามีแคชหรือข้อมูลไม่เปลี่ยน → ไม่เรียก.

7) ตั้ง quota, alerts และ circuit-breaker
- ตั้งเพดานรายวัน/รายสัปดาห์ต่อ environment และส่งแจ้งเตือนเมื่อใกล้ถึงเพดาน.
- ใช้ circuit-breaker เพื่อหยุดการเรียกอัตโนมัติเมื่อเกิด spike.

8) Prompt templates และรีไซเคิล context
- เก็บ prompt templates ไว้ใน `docs/` หรือ `src/prompts/` และเวอร์ชันไว้เพื่อรีวิว.
- ส่งเฉพาะส่วนที่จำเป็นของ context (context ids + short summary) แทนส่งข้อมูลทั้งหมดทุกครั้ง.

9) พิจารณา local/cheap alternatives
- สำหรับงานที่ deterministic หรือ utility (tokenize, regex, transforms) ให้ใช้สคริปต์ท้องถิ่น.
- สำรวจ LLM เล็กที่รันในเครื่องหรือบนโฮสต์ราคาถูกสำหรับงาน background.

10) ตัวอย่างโค้ด wrapper (Python) — logging + cache + model selection
```python
import hashlib
import json
from pathlib import Path

CACHE_DIR = Path(".cache/llm")
CACHE_DIR.mkdir(parents=True, exist_ok=True)

def _cache_key(model: str, prompt: str) -> str:
    h = hashlib.sha256((model + "\0" + prompt).encode()).hexdigest()
    return h

def get_cached(model: str, prompt: str):
    key = _cache_key(model, prompt)
    p = CACHE_DIR / key
    if p.exists():
        return json.loads(p.read_text(encoding='utf-8'))
    return None

def set_cached(model: str, prompt: str, resp: dict):
    key = _cache_key(model, prompt)
    p = CACHE_DIR / key
    p.write_text(json.dumps(resp, ensure_ascii=False), encoding='utf-8')

def llm_call(model: str, prompt: str, call_fn, use_cache=True):
    # call_fn is a function that executes the real API call
    if use_cache:
        cached = get_cached(model, prompt)
        if cached is not None:
            return cached
    resp = call_fn(model=model, prompt=prompt)
    set_cached(model, prompt, resp)
    return resp
```

11) เอกสาร prompt templates (ตัวอย่าง)
- `weekly_summary_template`: ให้ส่งเฉพาะรายการเหตุการณ์ใหม่ + สถานะสำคัญ ไม่ต้องส่ง payload ดิบทั้งหมด.

12) การวางแนวปฏิบัติทีม (policy)
- ให้ทีมทำ A/B tests กับ prompt/params ใน sandbox ก่อนเปิดใช้งานสู่ production.
- บันทึกเวอร์ชัน prompt ทุกครั้งที่แก้ไข.

13) ขั้นตอนต่อไปที่ผมช่วยทำได้ทันที
- เพิ่ม lightweight instrumentation ที่จับการเรียก HTTP/LLM ในโปรเจกต์ (ไฟล์ `src/instrumentation.py`).
- สร้าง `src/llm_client.py` scaffold ที่รวม caching, logging, model selection.
- หรือ: แค่อยู่ใน `docs/` ฉบับย่อแบบนี้ (ไฟล์นี้) — ถ้าพอแล้ว ให้ผมปิด TODO.

---
บอกผมว่าต้องการให้ผมสร้าง `src/llm_client.py` scaffold ด้วยโค้ดตัวอย่าง หรือแค่เก็บเอกสารนี้ไว้เป็นนโยบาย (ผมได้สร้างไฟล์นี้แล้ว).
