# GRVT — ข้อเท็จจริงที่ต้องรู้ก่อนต่อ API

> **นี่คือตลาดหลักของโปรเจคนี้** แม่แบบ `trade-bot` รองรับในตัว ตั้งค่าเดียวจบ
> ทุกข้อในไฟล์นี้มาจากเอกสาร API ของ GRVT และจาก source ของ `grvt-pysdk`
> https://api-docs.grvt.io/ · https://github.com/gravity-technologies/grvt-pysdk
> ถ้าต้องตอบเรื่องที่ไม่มีในไฟล์นี้ ให้ไปอ่าน doc จริง อย่าตอบจากความจำ

## ทำไมเหมาะกับนักเรียน

- **ไม่มีกำแพงแบบ faucet** — ต่างจาก Hyperliquid ที่ต้องเคย deposit บน mainnet ก่อน
  ถึงจะขอ mock USDC ได้ (ดู `refs/choose-exchange.md`)
- มี **testnet แยกสมบูรณ์** สลับด้วย `env: testnet`
- แม่แบบมี broker ของ GRVT มาให้แล้ว ไม่ต้องเขียนเพิ่ม
- perpetual futures เทรด 24/7 ไม่มี gap ข้ามคืน

## สภาพแวดล้อม

```
env: testnet   ซ้อมมือ ใช้คู่กับ --dry-run หรือ --live ก็ได้
env: prod      เงินจริง — บอทจะไม่ยอมรันถ้าไม่ใส่ --live
```

SDK รองรับ `prod` / `testnet` / `staging` / `dev` แต่โปรเจคนี้ใช้แค่สองตัวแรก

## กุญแจ — สามค่า

```
GRVT_API_KEY              คีย์จากหน้า API ของ GRVT
GRVT_PRIVATE_KEY          secret private key คู่กับคีย์นั้น
GRVT_TRADING_ACCOUNT_ID   เลขบัญชีเทรด
GRVT_SUB_ACCOUNT_ID       ถ้าไม่ได้ตั้งค่าไว้ใช้ "0"
```

ทั้งสามค่าอยู่ใน `bot/.env` เท่านั้น และ `.env` ต้องอยู่ใน `.gitignore` **ก่อน**สร้างไฟล์
เปิดสิทธิ์เทรดอย่างเดียว **ปิดสิทธิ์ถอนเงินเสมอ** และแยกคีย์ testnet กับ prod คนละอัน

ติดตั้ง SDK: `pip install grvt-pysdk` (ในแม่แบบคือ `pip install -e ".[grvt]"`)

## ชื่อสินค้า

ใช้ชื่อแบบ**คู่เทรด**: `BTC_USDT_Perp` `ETH_USDT_Perp`

ไม่ใช่ `BTCUSDT` (แบบ Binance) และไม่ใช่ `BTC` เปล่าๆ (แบบ Hyperliquid)
แม่แบบจะปฏิเสธถ้าเขียนผิดรูปแบบ พร้อมบอกว่าควรเขียนยังไง

## สเปคสินค้า — ตลาดบอกมาครบ ไม่ต้องเดา

`fetch_market(symbol)` คืนค่าเหล่านี้

| ฟิลด์ | ความหมาย | ใช้ทำอะไร |
|---|---|---|
| `tick_size` | ขนาดหนึ่งช่องราคา | ปัดราคา (tick ธรรมดา ไม่มีกฎ significant figures) |
| `min_size` | **ขนาดออเดอร์ขั้นต่ำ นับเป็นจำนวนสินค้า** | ด่าน `below_min_size` |
| `min_notional` | **มูลค่าออเดอร์ขั้นต่ำ หน่วย USD** | ด่าน `below_min_notional` |
| `base_decimals` | ทศนิยมของสินค้าอ้างอิง | lot step = `10^-base_decimals` |
| `quote_decimals` | ทศนิยมของสกุลเงินอ้างอิง | |
| `max_position_size` | เพดานขนาด position | |
| `instrument_hash` | asset id ใช้ตอนเซ็น | SDK จัดการให้ |

⚠️ **มีด่านขั้นต่ำสองชั้น ต้องผ่านทั้งคู่** — `min_size` เป็นจำนวนสินค้า
ส่วน `min_notional` เป็นมูลค่า ขั้นต่ำจริงคือ `max(min_notional, min_size x ราคา)`

### 🚨 ขั้นต่ำของ BTC สูงกว่าที่คนคาด — เช็คก่อนสัญญาอะไรกับผู้ใช้

ยืนยันจาก API จริงเมื่อ 2026-11-04 (190 สินค้า) ขั้นต่ำแบ่งเป็นสามชั้น

| ชั้น | `min_notional` | สินค้า |
|---|---|---|
| สูง | **$100** | **BTC_USDT_Perp เท่านั้น** |
| กลาง | **$20** | ETH, BCH, LTC, LINK |
| ต่ำ | **$5** | อีก 185 ตัว (SOL, XRP, DOGE, ADA, หุ้น, ทอง, น้ำมัน...) |

**นี่ทำให้สเปคของนักเรียนทุนน้อยพังเงียบๆ** ทุน 5,000 บาท เสี่ยง 0.25% stop 2.5%
→ ไม้ละ ~$14 ซึ่งผ่านชั้น $5 สบาย แต่**ไม่ผ่าน BTC ที่ $100**

ถ้าปล่อยไว้ บอทจะปฏิเสธทุกสัญญาณด้วย `below_min_notional` ตลอดไป
**รันได้ ไม่ error แต่ไม่เทรด** ซึ่งอันตรายกว่า error เพราะดูเหมือนทำงานปกติ

และถ้าฝืนเปิดไม้ $100 ให้ผ่านขั้นต่ำ: stop ต้องแคบเหลือ 0.39% จึงจะเสี่ยงตามงบ
แต่ ATR x2 บน H4 ของ BTC กว้าง 2.5-4% → ความเสี่ยงจริงเกินสเปค 6-10 เท่า

**ดังนั้นในขั้นที่ 4 ต้องเช็คขั้นต่ำเทียบกับ `risk.yaml` ก่อน** ไม่ใช่รอให้บอทไปเจอเอง
ถ้าไม่ผ่าน ให้เสนอทางเลือกตรงๆ: เปลี่ยนสินค้าไปชั้น $5 · ไปตลาดอื่น · หรือเพิ่มทุน
ห้ามแก้ `risk.yaml` ให้เสี่ยงมากขึ้นเพื่อให้ผ่านขั้นต่ำ นั่นคือเปลี่ยนสเปคความปลอดภัยให้เข้ากับตลาด

## ดึงข้อมูล

| ต้องการ | เรียกอะไร |
|---|---|
| สเปคสินค้า | `fetch_market(symbol)` · ทั้งหมด `fetch_all_markets()` |
| ราคา | `fetch_ticker(symbol)` → `mark_price` / `index_price` / `last_price` |
| แท่งเทียน | `fetch_ohlcv(symbol, timeframe, since, limit)` — **ใช้ warm-up ได้** |
| order book | `fetch_order_book(symbol, limit)` |
| ยอดเงิน | `fetch_balance(type="sub-account")` |
| position | `fetch_positions(symbols)` → `size` **ติดลบ = short** · `entry_price` |
| ออเดอร์ที่ค้าง | `fetch_open_orders(symbol)` |

⚠️ แถวที่ `size` เป็น 0 ต้อง**ทิ้ง** ตลาดยังรายงานสินค้าที่ปิดไปแล้วด้วยขนาดศูนย์
ถ้านับเป็น position ที่เปิดอยู่ risk gate จะปฏิเสธการเทรดตัวนั้นตลอดไป

## ดึงสเปคและราคาได้ "โดยไม่ต้องมีกุญแจ" — ใช้ประโยชน์ข้อนี้

market data ของ GRVT เป็น public ใช้ตรวจได้ก่อนผู้ใช้สมัครบัญชีเลย

```
POST https://market-data.grvt.io/full/v1/instruments          (prod)
POST https://market-data.testnet.grvt.io/full/v1/instruments   (testnet)
     body: {"kind": ["PERPETUAL"], "is_active": true}

POST .../full/v1/ticker    body: {"instrument": "BTC_USDT_Perp"}  -> mark_price
```

**เช็คขั้นต่ำเทียบสเปคผู้ใช้ตั้งแต่ก่อนมีกุญแจ** แล้วค่อยให้เขาไปสมัคร
ดีกว่าให้เขาเสียเวลาสมัคร ตั้งคีย์ แล้วมาเจอว่าเทรดสินค้านั้นไม่ได้

### ⚠️ กับดัก: endpoint ไม่สนใจตัวกรอง `instrument`

ส่ง `{"instrument": ["BTC_USDT_Perp"]}` ไปที่ `/instruments` แล้ว**มันคืนทั้งลิสต์**
ถ้าหยิบ `result[0]` มาใช้เลยจะได้สเปคของสินค้าตัวแรกตามตัวอักษร (AAOI) มาแทน BTC
**โดยไม่มีอะไรฟ้อง** — tick, min_size, min_notional ผิดหมด ขนาดไม้พังทั้งระบบ

ต้องกรองชื่อเองฝั่งเรา และยืนยันว่า `instrument` ที่ได้ตรงกับที่ขอจริงก่อนใช้ค่า

### กับดักเรื่องสเกลราคา

GRVT มี API สองแบบ

| แบบ | ราคาเป็นอะไร |
|---|---|
| `full` (ที่ใช้ข้างบน) | สตริงทศนิยมปกติ เช่น `"78672.9692"` |
| `lite` | **จำนวนเต็มที่สเกลตามทศนิยมของสินค้า** |

**ให้ใช้ `GrvtCcxt` หรือ endpoint `full` เท่านั้น** ถ้าเผลอใช้ `lite` แล้วไม่หารกลับ
ราคาจะใหญ่กว่าความจริงมหาศาลและขนาดไม้จะพังหมด — แม่แบบดักไว้แล้วด้วยการ raise
ถ้าราคาเกินค่าที่เป็นไปได้ พร้อมบอกให้เปลี่ยนไปใช้ ccxt client

## ส่งออเดอร์

```python
from pysdk.grvt_ccxt import GrvtCcxt
from pysdk.grvt_ccxt_env import GrvtEnv

client = GrvtCcxt(GrvtEnv("testnet"), logger, parameters={
    "api_key": api_key,
    "trading_account_id": trading_account_id,
    "private_key": private_key,
})

client.create_order(
    symbol="BTC_USDT_Perp",
    order_type="limit",          # เข้าเป็น limit เสมอ
    side="buy",
    amount=0.01,
    price=100000.0,
    params={
        "client_order_id": 2311191495,   # ⚠️ ต้องเป็นตัวเลข
        "time_in_force": "GOOD_TILL_TIME",
        "reduce_only": False,
        "sub_account_id": "0",
    },
)
```

- `time_in_force`: `GOOD_TILL_TIME` (ค่าเริ่มต้น) · `IMMEDIATE_OR_CANCEL` · `ALL_OR_NONE` ฯลฯ
- `order_duration_secs`: อายุออเดอร์ ค่าเริ่มต้น 24 ชั่วโมง
- ปิด position: `order_type="market"` + `reduce_only=True`
- ยกเลิก: `cancel_order(id=...)` หรือ `cancel_order(params={"client_order_id": ...})`

### ⚠️ client_order_id ต้องเป็น "ตัวเลข"

SDK ทำ `int(params["client_order_id"])` และถ้าไม่ส่งมาจะสุ่ม uint32 ให้
ต่างจาก Hyperliquid ที่ต้องเป็น `0x` + hex 32 ตัว

แม่แบบแก้ด้วยการให้ `risk_gate` ผลิต id เดียวที่คงที่ (sha256 ของตัวสัญญาณ)
แล้ว **broker ของ GRVT พับเป็น uint32** ด้วย 8 ตัวแรกของ hash
สัญญาณเดิมจึงได้ id เดิมเสมอ = กันสั่งซ้ำได้ โดยที่ risk gate ไม่ต้องรู้เรื่องตลาด

## การอ่านคำตอบของออเดอร์

มองหา `order_id` (อาจซ้อนใน `result`) ถ้าไม่เจอให้ถือว่า **error**
ห้ามนับเป็นสำเร็จ และต้องบอกผู้ใช้ให้ reconcile ก่อนลองใหม่
(ดู `refs/pitfalls.md` ข้อ 5 — บอทตัวหนึ่งเคยพลาดข้อนี้จนคิดว่าถือ position ที่เรียกชื่อไม่ได้)

เงื่อนไขที่ถือว่าล้มเหลว เข้าข้อใดข้อหนึ่งก็พอ: `code` ไม่ใช่ 0/200 · มี `error` · `status` ≥ 400

## leverage

SDK ตัวนี้**ตั้ง leverage ไม่ได้** ต้องไปตั้งบนเว็บ GRVT เอง
บอททำได้แค่จำกัด exposure ที่ ทุน × `risk.max_leverage` ซึ่งเป็นคนละเรื่องกัน

อย่าสร้างพารามิเตอร์ `leverage=` ที่รับแล้วไม่ใช้ — บอทรุ่นเก่าเคยทำแบบนั้นและมันโกหกคนอ่านโค้ด

## ตั้งค่าในแม่แบบ

```yaml
exchange: grvt

grvt:
  env: testnet
  api_key: "${GRVT_API_KEY}"
  private_key: "${GRVT_PRIVATE_KEY}"
  trading_account_id: "${GRVT_TRADING_ACCOUNT_ID}"
  sub_account_id: "0"

trading:
  symbol: ""          # เว้นว่าง = BTC_USDT_Perp
  timeframe: "4h"
```

## เช็คลิสต์ทดสอบการเชื่อมต่อ

ใช้แทน 4 ข้อท้าย `/bot:connect` ได้เลย

```
[ ] fetch_market คืน tick_size / min_size / base_decimals ของสินค้าที่จะเทรด
[ ] fetch_ticker คืนราคาเป็นบวก และอยู่ในช่วงที่สมเหตุสมผล (ไม่ใช่ค่าสเกล 1e9)
[ ] fetch_ohlcv คืนแท่งเทียนเรียงตามเวลา
[ ] fetch_balance คืนยอดเงินของ sub-account
[ ] fetch_positions ทำงาน และแถวขนาดศูนย์ถูกกรองทิ้ง
[ ] วาง limit order ห่างตลาด 30% แล้ว cancel ด้วย client_order_id ได้
[ ] ลองส่งออเดอร์ต่ำกว่า min_size แล้วจับ error ได้ ไม่ใช่เงียบ
```

ในแม่แบบสั่งได้ด้วยคำสั่งเดียว

```bash
tradebot --doctor                  # ตรวจ config + เชื่อมต่อ + ราคา + สเปค + ยอดเงิน + แท่งเทียน
pytest --run-integration           # ยิงออเดอร์จริงหนึ่งไม้แล้วยกเลิก (testnet เท่านั้น)
```
