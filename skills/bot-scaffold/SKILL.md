---
name: bot-scaffold
description: สร้างโปรเจคโค้ดจริงจากไฟล์สเปคที่ผู้ใช้ตอบคำถามไว้ โดยเริ่มจากแม่แบบที่เทสผ่านแล้วถ้าทำได้ หรือวางโครงใหม่ตามกฎสถาปัตยกรรมถ้าตลาดไม่รองรับ ให้ risk engine และ executor เป็นฟังก์ชันตายตัวที่ไม่มี LLM และใช้โค้ดชุดเดียวกันได้ทั้ง backtest paper และ live ใช้เมื่อผู้ใช้พิมพ์ /bot:scaffold หรือขอให้สร้างโค้ด เขียนโปรแกรมบอท generate project
---

# สร้างโปรเจคจากสเปค

## ด่านก่อนเริ่ม

ต้องมี `bot/strategy.yaml` และ `bot/risk.yaml` ครบก่อน ถ้ายังไม่มี ให้กลับไป `/bot:strategy` และ `/bot:risk`
ห้าม gen โค้ดจากค่าที่เดาเอง

## ตัดสินใจก่อนลงมือ — เริ่มจากแม่แบบ หรือเขียนใหม่

**อ่าน `references/template.md` ก่อนทุกครั้ง** แล้วเลือกทางตามนี้

```
ผู้ใช้เทรดคริปโต perpetual + รับ Python ได้
    → เริ่มจากแม่แบบ hyperliquid-bot (236 เทสผ่าน, CI เขียว)
      งานที่เหลือคือแมปสเปคลง config + เขียนไฟล์กลยุทธ์ + เทสของมัน

ผู้ใช้เทรดหุ้น / TFEX / ฟอเร็กซ์ หรือยืนยันว่าอยาก Rust
    → วางโครงใหม่ตามกฎ 5 ข้อข้างล่าง
      แต่ยังลอก "สัญญาของ risk_gate" กับ "สูตรขนาดไม้" จาก references/template.md มาทั้งหมด
```

บอกผู้ใช้ตรงๆ ว่าเลือกทางไหนและเพราะอะไร การเริ่มจากแม่แบบไม่ใช่การขี้เกียจ —
มันคือการไม่เขียนบั๊กเดิมซ้ำ (ดู `references/pitfalls.md` ว่าเคยพลาดอะไรมาแล้ว)

---

## กฎสถาปัตยกรรม 5 ข้อ — ห้ามละเมิดไม่ว่าจะใช้ภาษาอะไรหรือทางไหน

1. **risk engine และ executor ต้องไม่มี LLM และไม่เป็น async**
   เป็นฟังก์ชันบริสุทธิ์ที่รับสถานะเข้า คืนผลออก เทสต์ได้ 100% ไม่มีผลข้างเคียง
   เวลาปัจจุบันต้องส่งเข้าไปเป็นพารามิเตอร์ ไม่ใช่ให้มันอ่านนาฬิกาเอง
2. **โค้ดชุดเดียวใช้ได้ทั้ง backtest / paper / live**
   ต่างกันแค่ตัวป้อนข้อมูลกับตัวส่งคำสั่ง (เปลี่ยนที่ขอบ ไม่ใช่เปลี่ยนแกน)
   ถ้าต้องเขียน logic ซ้ำสองที่ แปลว่าออกแบบผิด
3. **ห้ามใช้ float กับเงินและราคา** ใช้ decimal เสมอ (`rust_decimal` / `decimal.Decimal`)
   จุดเดียวที่ยอมให้มี `float` คือตอนเรียก SDK ของตลาดที่บังคับ และต้องมีคอมเมนต์กำกับ
4. **สเปคคือแหล่งความจริง** โค้ดอ่าน YAML ตอนรัน ไม่ใช่ฝังค่าไว้ในโค้ด
   ผู้ใช้แก้พฤติกรรมบอทได้โดยแก้ YAML ไม่ต้องแตะโค้ด
5. **บันทึกทุกการตัดสินใจ** ทุกสัญญาณ ทุกคำสั่ง ทุกการปฏิเสธจาก risk engine ต้องลงไฟล์พร้อมเหตุผล
   แนะนำ JSONL หนึ่งบรรทัดต่อหนึ่งการตัดสินใจ อ่านย้อนหลังได้

---

## ทางที่ 1 — เริ่มจากแม่แบบ (คริปโต + Python)

```bash
gh repo create my-bot --template borntoquantdev-star/hyperliquid-bot --private --clone
cd my-bot
python -m venv .venv
.venv/Scripts/python.exe -m pip install -e ".[dev]"
.venv/Scripts/python.exe -m pytest        # ต้องผ่านก่อนแก้อะไรทั้งสิ้น
```

ถ้าเทสตกตั้งแต่ยังไม่แก้อะไร ปัญหาอยู่ที่สภาพแวดล้อม ไม่ใช่โค้ด — แก้ให้ผ่านก่อน

แล้วทำ 4 อย่างนี้ตามลำดับ

1. **แมปสเปคลง `config/config.yaml`** ตามตารางใน `references/template.md`
2. **เขียนไฟล์กลยุทธ์** ใน `hyperbot/strategies/` ตามแบบ `ma_cross.py` แล้วลงทะเบียนใน `__init__.py`
3. **เขียนเทสของกลยุทธ์** อย่างน้อย 5 เคส: ยัง warm-up ไม่ครบ / เงื่อนไขติด / เงื่อนไขไม่ติดหนึ่งก้าวก่อน /
   stop อยู่ฝั่งที่ถูกทั้ง long และ short / เงียบเมื่อมีไม้เปิดอยู่
4. **รัน `pytest` แล้ว `hyperbot --dry-run --iterations 20`** แล้วอ่าน `logs/audit.jsonl` กับผู้ใช้

**ห้ามแก้ `hyperbot/risk.py` เพื่อให้กลยุทธ์ผ่านด่าน** ถ้ากลยุทธ์ชนด่าน ให้แก้กลยุทธ์หรือสเปค
ถ้าผู้ใช้ยืนยันว่าต้องแก้กฎ ให้เตือนว่าแก้อะไรและทำไมมันถูกใส่ไว้ตอนแรก

---

## ทางที่ 2 — วางโครงใหม่

### ลำดับการสร้าง — ห้ามสลับ

```
1  ชนิดข้อมูลหลัก + risk_gate + เทสต์      ← ทำให้เสร็จและเทสต์ผ่านก่อน
2  store (SQLite) + ตัวอ่านข้อมูลย้อนหลัง
3  backtest runner ที่เรียก risk_gate ตัวเดียวกับที่จะใช้จริง
4  executor + paper adapter + reconcile
5  live adapter (เปิดใช้หลังผ่าน /bot:paper)
6  UI / dashboard
7  LLM analyst lanes                        ← ทำทีหลังสุดเสมอ
```

> ทำ UI หรือ LLM ก่อน = ได้บอทที่สวยแต่เชื่อถือไม่ได้

### แบบ Rust (ถ้าผู้ใช้อยากได้ไฟล์เดียวจบและเร็ว)

```
bot/                      ← สเปค YAML (ไม่ใช่โค้ด)
crates/
  core/        ชนิดข้อมูล: Price, Qty, Signal, Order, Position  (decimal ล้วน)
  risk/        risk_gate() — ฟังก์ชัน sync ล้วน ไม่มี I/O
  strategy/    อ่าน strategy.yaml แล้วผลิต Signal จากแท่งเทียน
  data/        market data: csv / websocket / rest
  exec/        executor + adapter: backtest | paper | live
  store/       sqlx + SQLite: candles, signals, orders, decisions
  app/         ตัวรันหลัก + CLI
ui/            (ขั้นที่ 6) Tauri
```

```toml
tokio        = { version = "1", features = ["full"] }
rust_decimal = "1"          # ห้าม f64 กับเงิน
serde        = { version = "1", features = ["derive"] }
serde_yaml   = "0.9"
sqlx         = { version = "0.8", features = ["sqlite", "runtime-tokio"] }
tracing      = "0.1"
reqwest      = { version = "0.12", features = ["json"] }
tokio-tungstenite = "0.24"
thiserror    = "2"
```

```rust
// 1 strategy = 1 task มี mailbox และสถานะที่ UI subscribe ได้
struct Lane { tx: mpsc::Sender<Command>, status: watch::Receiver<LaneStatus> }

enum LaneStatus { Scanning, InPosition { since: Instant }, NeedsApproval, Halted, Error }

// ตัวจุดชนวน: แท่งปิด / เหตุการณ์ / ตารางเวลา
select! {
    _     = interval.tick()  => run(),
    Ok(c) = candle_rx.recv() => run(),
    Ok(e) = event_rx.recv()  => run(),
}

// หัวใจ — sync ล้วน ไม่มี LLM ไม่มี I/O เทสต์ได้เต็มร้อย
fn risk_gate(state: &PortfolioState, sig: &Signal, cfg: &RiskConfig, now: DateTime<Utc>)
    -> Result<SizedOrder, Reject>;
```

### แบบ Python (ถ้าตลาดไม่ใช่คริปโต)

```
bot/              ← สเปค YAML
src/
  core/      types.py (Decimal), signal.py, order.py
  risk/      gate.py        ← ฟังก์ชันบริสุทธิ์ + test_gate.py
  strategy/  loader.py, indicators.py
  data/      ccxt_source.py, csv_source.py, quality.py
  exec/      backtest.py, paper.py, live.py  (อินเทอร์เฟซเดียวกัน)
  store/     db.py (SQLite)
  app/       main.py, cli.py
tests/
```

ไลบรารี: `ccxt`, `pandas` หรือ `polars`, `pandas-ta`, `pydantic` (ตรวจ YAML),
`vectorbt` หรือ `backtesting.py`, `python-dotenv`, `structlog`

### สิ่งที่ต้อง generate ให้ครบ ไม่ใช่แค่โครงว่าง

1. **`risk_gate` ที่ทำงานได้จริง** อ่านค่าจาก `risk.yaml` ครบทุกช่อง
   ใช้ 13 เหตุผลปฏิเสธใน `references/template.md` เป็นรายการตั้งต้น เรียงตามความร้ายแรง
   และต้องมีเทสหนึ่งตัวต่อหนึ่งเหตุผล บวกเทส invariant ว่าขนาดไม้ไม่เคยเสี่ยงเกินงบ
2. **ตัวตรวจสเปค** — โปรแกรมต้อง refuse to start ถ้า YAML ขัดกันเอง
   (ใช้กติกาตรวจความสอดคล้อง 5 ข้อจาก `/bot:risk`)
3. **`.gitignore`** ที่มี `bot/.env` อยู่แล้ว **ก่อน**ที่จะสร้างไฟล์ `.env`
4. **README สั้น** บอกวิธีรัน backtest / paper / live และวิธีหยุด
5. **สคริปต์หยุดฉุกเฉิน** ที่ `/bot:panic` เรียกใช้ได้
6. **สถานะที่อยู่ข้ามการรีสตาร์ต** — ทุนต้นวัน จุดสูงสุดของพอร์ต สถานะ halt และ order id ที่ส่งแล้ว

---

## สิ่งที่ห้าม generate ไม่ว่าทางไหน

- โค้ดที่ส่งคำสั่งด้วยการพิมพ์ลง terminal หรือ UI automation — ต้องใช้ API เท่านั้น
- โค้ดที่ให้ LLM เรียก broker API ตรงๆ
- โค้ดที่ไม่มี stop loss
- โค้ดที่ default เป็น `live` — ค่าตั้งต้นต้องเป็น `backtest` หรือ `paper` เสมอ
- ค่า API key ฝังในโค้ด ไม่ว่าจะเป็นค่าตัวอย่างก็ตาม
- `dry-run` ที่ยังต้อง authenticate กับตลาดจริงก่อน (ดู `references/pitfalls.md` ข้อ 8)
- พารามิเตอร์ที่รับแล้วไม่ใช้ เช่น `leverage=` ที่ไม่มีผลอะไร (ข้อ 6)

## ก่อนบอกว่าเสร็จ — ไล่เช็คลิสต์ท้าย `references/pitfalls.md`

สิบข้อนั้นมาจากบอทจริงที่เคยพังมาแล้ว ข้อที่พลาดกันมากที่สุดสองข้อคือ
**clone รีโปเปล่าแล้วเทสไม่ผ่าน** และ **`pytest` เปล่าๆ ยิงออเดอร์จริง**

## ผลลัพธ์ที่ต้องส่งมอบ

1. โครงโปรเจคที่ **คอมไพล์ผ่านและเทสต์ผ่าน** ไม่ใช่โครงที่ยังรันไม่ได้
2. รันเทสต์ของ `risk_gate` ให้ดูและรายงานผลจริง ถ้าเทสต์ตก ให้บอกตรงๆ
3. รันโหมด dry-run / paper ให้ดูอย่างน้อยหนึ่งรอบ แล้วอ่าน log การตัดสินใจด้วยกัน
4. อธิบายให้ผู้ใช้ว่า **เขาต้องแก้ตรงไหนเวลาอยากเปลี่ยนพฤติกรรมบอท**
   (คำตอบควรเป็น "แก้ YAML" เกือบทุกกรณี)
5. อัปเดต `bot/STATUS.md`
