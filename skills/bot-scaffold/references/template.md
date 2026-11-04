# แม่แบบที่พิสูจน์แล้ว — hyperliquid-bot

> อ่านไฟล์นี้ก่อนจะ generate โค้ดใหม่เองทุกครั้ง
> ถ้าผู้ใช้เทรดคริปโตและยอมใช้ Python การ**เริ่มจากแม่แบบนี้** ให้ผลดีกว่าการเขียนขึ้นใหม่เสมอ

https://github.com/borntoquantdev-star/hyperliquid-bot

## ทำไมต้องเริ่มจากแม่แบบ ไม่ใช่เขียนใหม่

บอทเทรดที่ใช้ได้จริงมีรายละเอียดที่ "เขียนใหม่ทุกครั้ง" แล้วพลาดแน่ๆ เช่นกฎการปัดราคาของตลาด
การกันสั่งซ้ำ และการที่สถานะ halt ต้องอยู่ข้ามการรีสตาร์ต

แม่แบบนี้ผ่านแล้ว: **236 เทส offline** · `ruff` / `black` / `mypy` สะอาด · CI เขียวบน Python 3.10–3.12
ไม่ต้องมี API key ไม่ต้องต่อเน็ต ก็รันเทสและเทรดกระดาษได้

| สิ่งที่ยากและแม่แบบทำไว้แล้ว | ถ้าเขียนใหม่ |
|---|---|
| `risk_gate()` ปฏิเสธได้ 13 แบบ เรียงตามความร้ายแรง | มักได้ 3–4 แบบ และเรียงมั่ว |
| สูตรขนาดไม้ที่หักค่าธรรมเนียมสองขาแบบแก้สมการ | มักเผื่อเอาแบบมั่วๆ แล้วเสี่ยงเกินงบ |
| เทส invariant ว่าการปัดเศษไม่เคยทำให้เสี่ยงเกินงบ | ไม่มีใครคิดถึง |
| กฎราคาของตลาด (ดู `refs/hyperliquid.md`) | ออเดอร์ถูกปฏิเสธเงียบๆ |
| `client_order_id` คงที่ เขียนลงดิสก์ทันทีที่ส่งสำเร็จ | เน็ตหลุด = เปิดไม้ซ้อน |
| daily loss / drawdown halt ที่อยู่ข้ามการรีสตาร์ต | รีสตาร์ตแล้วเพดานรายวันรีเซ็ต |
| `--dry-run` ที่ offline จริง ไม่ต้องมีคีย์ | dry-run ที่ยัง auth กับตลาดจริงก่อน |

## วิธีเริ่ม

```bash
gh repo create my-bot --template borntoquantdev-star/hyperliquid-bot --private --clone
cd my-bot
python -m venv .venv
.venv/Scripts/python.exe -m pip install -e ".[dev]"     # mac/linux: .venv/bin/python
.venv/Scripts/python.exe -m pytest                      # ต้องได้ 236 passed ก่อนทำอะไรต่อ
```

ถ้าไม่มี `gh` ให้ `git clone` แล้วลบ `.git` ออกและ `git init` ใหม่

**รันเทสให้ผ่านก่อนแก้อะไรทั้งสิ้น** ถ้าเทสตกตั้งแต่ต้น ปัญหาอยู่ที่สภาพแวดล้อม ไม่ใช่โค้ด

## โครงที่ได้มา

```
hyperbot/
  money.py        Decimal ล้วน + floor_to_step / significant_figure_step
  types.py        Side, InstrumentSpec, RiskLimits, Signal, SizedOrder, Reject, Candle
  risk.py         risk_gate() ← หัวใจ pure sync ไม่มี I/O ไม่มี LLM
  strategies/     base.py (Strategy, MarketView) + random + ma_cross + ทะเบียน
  brokers/        base.py (Broker protocol) + paper.py (offline) + hyperliquid.py
  core/           config.py (YAML + env + validate) + engine.py (ลูป ไม่มีกฎเทรด)
  cli/main.py     --dry-run --live --doctor --resume --close --iterations
tests/            เทส offline + integration ที่ต้องสั่ง --run-integration
dashboard/        หน้าดูบอททำงาน realtime (Node ล้วน ไม่มี dependency)
config/config.example.yaml
```

ทิศทางการ import ชี้เข้าทางเดียว: `cli → core → {strategies, brokers} → {risk, types, money}`
ชั้นในห้าม import ชั้นนอก

## สัญญาของ `risk_gate` — ห้ามแก้โดยไม่คุยกับผู้ใช้

```python
def risk_gate(signal, state, limits, spec, mark_price, now) -> SizedOrder | Reject
```

1. **pure** ไม่ต่อเน็ต ไม่อ่านไฟล์ ไม่มีนาฬิกาของตัวเอง (`now` ส่งเข้ามา) ไม่มี random ไม่มี LLM
2. **sync** ห้าม `async` เด็ดขาด
3. **ขนาดไม้มาจากงบเสี่ยงกับระยะ stop เท่านั้น** กลยุทธ์ส่ง `confidence` มาก็ไม่มีผล — และไม่มีฟิลด์นั้นด้วย
4. **ทุก Signal ต้องมี stop** ไม่มี code path ไหนเปิดไม้ได้โดยไม่มี stop
5. **รายงานเหตุผลที่ร้ายแรงที่สุดก่อน** ลำดับใน `RejectCode` คือลำดับการตรวจ

13 เหตุผลที่ปฏิเสธ เรียงจากร้ายแรงสุด:

```
halted → max_drawdown → daily_loss_limit → expired → short_not_allowed
→ invalid_stop → slippage_exceeded → already_in_position → too_many_positions
→ qty_rounds_to_zero → below_min_notional → exceeds_exposure → bad_instrument
```

## สูตรขนาดไม้ที่ใช้จริง

ถ้าโดน stop จะเสีย = ระยะ stop **บวก** ค่าธรรมเนียมทั้งขาเข้าและขาออก
ซึ่งค่าธรรมเนียมขึ้นกับ qty ที่ยังหาคำตอบไม่ได้ จึงแก้ด้วยการจัดสมการ ไม่ใช่เผื่อเอา

```
qty = งบเสี่ยง / (ระยะstop + (ราคาเข้า + ราคาstop) × feeRate)
```

แล้วปัด qty **ลง** ตาม lot step เสมอ การปัดจึงทำให้เสี่ยง**น้อยกว่า**งบได้เท่านั้น ไม่มีทางเกิน
มีเทส `test_risk_amount_never_exceeds_the_budget` ไล่หลายระยะ stop ยืนยันไว้

## กัน slippage สองชั้น

1. **ก่อนส่ง** ถ้าราคาวิ่งสวนสัญญาณเกิน `max_slippage` → ปฏิเสธ
2. **ในตัวออเดอร์** limit price = `ราคาเข้า × (1 ± max_slippage)` ปัดไปทางที่ปลอดภัย
   ราคาจะวิ่งแค่ไหนระหว่างออเดอร์เดินทาง ตลาดก็ fill แย่กว่านี้ไม่ได้

เพราะงั้น**ออเดอร์เข้าเป็น limit เสมอ** ส่วนออเดอร์ปิดเป็น market/IOC ที่ไล่ราคา —
เวลาอยากออก ราคาสวยที่ไม่มีใครรับคือผลลัพธ์ที่แย่ที่สุด

## สิ่งที่ต้องปรับตามสเปคของผู้ใช้

อ่าน `bot/profile.yaml` `bot/strategy.yaml` `bot/risk.yaml` แล้วแมปลง `config/config.yaml`:

| จาก bot/*.yaml | ไป config.yaml |
|---|---|
| ตลาด/สินค้า | `trading.symbol` (Hyperliquid ใช้ชื่อเหรียญ: `BTC` `ETH` `SOL`) |
| timeframe | `trading.timeframe` + `trading.warmup_candles` |
| ความเสี่ยงต่อไม้ | `risk.risk_per_trade_pct` |
| เพดานขาดทุนรายวัน | `risk.max_daily_loss_pct` |
| kill switch | `risk.max_drawdown_pct` |
| จำนวนไม้พร้อมกัน | `risk.max_positions` |
| long only? | `risk.allow_short: false` |

แล้วเขียนกลยุทธ์ของผู้ใช้เป็นไฟล์ใหม่ใน `hyperbot/strategies/` ตามแบบ `ma_cross.py`
**อย่าแก้ `risk.py` เพื่อให้กลยุทธ์ผ่าน** — ถ้ากลยุทธ์ชนด่าน ให้แก้กลยุทธ์หรือสเปค

## ขั้นต่ำที่ต้องส่งมอบ

1. โปรเจคที่ `pytest` ผ่าน **รันให้ดูและรายงานผลจริง** ถ้าตกให้บอกตรงๆ
2. ไฟล์กลยุทธ์ของผู้ใช้ + เทสของมัน (อย่างน้อย 5 เคสตามแบบใน `docs/strategies.md`)
3. `config/config.yaml` ที่แมปจากสเปคแล้ว
4. รัน `hyperbot --dry-run --paper-walk --iterations 20` ให้ดู แล้วอ่าน `logs/audit.jsonl` ด้วยกัน
5. เปิด `node dashboard/server.js --open` ให้เขาเห็นห้าขั้นของบอททำงานสดๆ
   (รายละเอียดใน `refs/dashboard.md`)
5. อธิบายว่าอยากเปลี่ยนพฤติกรรมบอทต้องแก้ตรงไหน (คำตอบคือ YAML เกือบทุกกรณี)
6. อัปเดต `bot/STATUS.md`

## เมื่อไหร่ที่ไม่ควรใช้แม่แบบนี้

- ผู้ใช้เทรด**หุ้น / TFEX / ฟอเร็กซ์** → แม่แบบผูกกับ Hyperliquid ให้เขียนใหม่ตามกฎ 5 ข้อใน SKILL
  แต่ยัง**ลอกสถาปัตยกรรมและสัญญาของ `risk_gate` มาได้ทั้งหมด**
- ผู้ใช้ยืนยันว่าอยาก Rust → ใช้โครง Rust ใน SKILL แต่พอร์ต 13 reject code กับสูตรขนาดไม้มา
- ผู้ใช้อยากเรียนรู้จากการเขียนเองทุกบรรทัด → เคารพความต้องการนั้น แต่บอกให้รู้ว่าแลกกับอะไร
