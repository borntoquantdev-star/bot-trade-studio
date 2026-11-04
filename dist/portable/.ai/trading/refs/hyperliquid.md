# Hyperliquid — ข้อเท็จจริงที่ต้องรู้ก่อนต่อ API

> ทุกข้อในไฟล์นี้มาจากเอกสาร API ของ Hyperliquid และ source ของ SDK
> https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api
> ถ้าต้องตอบเรื่องที่ไม่มีในไฟล์นี้ ให้ไปอ่าน doc จริง อย่าตอบจากความจำ

## ⚠️ เงื่อนไขที่ต้องบอกผู้ใช้ก่อน

**faucet ของ testnet จ่าย mock USDC ให้เฉพาะ wallet ที่เคยฝากเงินบน mainnet มาก่อน**

> "To use the testnet faucet, you need to have deposited on mainnet with the same address."
> ผ่านแล้วได้ 1,000 mock USDC ที่ https://app.hyperliquid-testnet.xyz/drip

ถ้าผู้ใช้ยังไม่เคยฝากเงินจริง **เขาจะไม่มีเงินเทรดบน testnet เลย** ให้ไปใช้
paper ในเครื่อง หรือ Binance Demo แทน (ดู `refs/choose-exchange.md`)

ถ้าล็อกอินด้วยอีเมล (Privy): address บน mainnet กับ testnet คนละอัน ต้อง export
wallet จาก mainnet แล้ว import เข้า Rabby/MetaMask ก่อน

## ทำไมเหมาะกับการเริ่มต้น

- ข้อมูลตลาด (ราคา, แท่งเทียน, metadata) เรียกได้**ฟรี ไม่ต้องมีคีย์**
  (ส่วนนี้ใช้ได้แม้ยังไม่มีบัญชี — ทดสอบโค้ดอ่านตลาดได้เลย)
- มี testnet แยกสมบูรณ์
- ขั้นต่ำต่อออเดอร์ **$10** (ต่ำกว่าเอ็กซ์เชนจ์ใหญ่หลายที่มาก เหมาะกับการทดลองด้วยทุนน้อย)
- perpetual futures 24/7 ไม่มี gap ข้ามคืน

## URL

```
mainnet   https://api.hyperliquid.xyz
testnet   https://api.hyperliquid-testnet.xyz
```

ปลายทางมีสองอัน: `/info` (อ่าน ไม่ต้องเซ็น) และ `/exchange` (เขียน ต้องเซ็น)

## กุญแจสองตัว — จุดที่คนพลาดบ่อยที่สุด

```
account_address   บัญชีแม่ (master) รูปแบบ 0x + 40 hex
                  ใช้ query ทุกอย่าง: ยอดเงิน, position
api_wallet_key    private key ของ API wallet (agent) ที่บัญชีแม่อนุมัติไว้
                  ใช้ "เซ็น" เท่านั้น ไม่เคยถูก query
```

สร้าง API wallet ที่ https://app.hyperliquid.xyz/API

**doc เตือนเองว่า:** ถ้าเอา address ของ agent ไป query แทน address บัญชีแม่
ตลาดจะตอบกลับเป็น**สถานะว่าง โดยไม่แจ้ง error** — บอทจะคิดว่าพอร์ตว่างเปล่าแล้วเทรดต่อ

เพราะงั้นเวลาตั้งค่า ให้:
1. ตรวจรูปแบบ `account_address` ว่าเป็น `0x` + 40 hex (ถ้าผู้ใช้วาง private key ลงช่องนี้ ให้ปฏิเสธทันที)
2. ถ้าดึงยอดเงินได้เป็นค่าว่าง ให้สงสัยข้อนี้ก่อนอย่างอื่น

ข้อดีของ API wallet: **มันถอนเงินไม่ได้** เซ็นได้แค่คำสั่งเทรด —
ตรงกับกฎข้อ 1 ใน SKILL เรื่องห้ามเปิดสิทธิ์ถอน

เรื่อง nonce ที่ต้องรู้: nonce นับแยกตามคีย์ที่เซ็น และ sub-account ทั้งหมดที่เซ็นด้วย
API wallet เดียวกันจะใช้ตัวนับร่วมกัน → **ถ้ามีหลาย sub-account ให้สร้าง API wallet แยกแต่ละอัน**
และ **ห้ามเอา agent address เก่ากลับมาใช้ซ้ำ** ให้สร้างใหม่

## กฎราคา — ไม่ใช่ tick size ธรรมดา

perpetual ของ Hyperliquid บังคับสองข้อ**พร้อมกัน**

1. ไม่เกิน **5 significant figures** — `1234.5` ผ่าน `1234.56` ไม่ผ่าน
2. ไม่เกิน **6 − szDecimals** ตำแหน่งทศนิยม
3. **ยกเว้นจำนวนเต็ม ผ่านตลอด** ไม่ว่าจะกี่หลัก — `123456` ผ่าน แต่ `12345.6` ไม่ผ่าน

ข้อ 3 สำคัญกว่าที่คิด: BTC ที่ราคาระดับแสน แปลว่า**ราคาต้องเป็นจำนวนเต็ม**
เพราะ `100100.5` มี 7 significant figures

วิธีคิดที่ถูก: หา step ที่หยาบกว่าระหว่างสองกฎ แล้วปัดไปทางที่ปลอดภัย (ซื้อปัดลง ขายปัดขึ้น)

```
ราคาใกล้ 100,000  →  step = 1       (จำนวนเต็มเท่านั้น)
ราคาใกล้ 1,000    →  step = 0.1
ราคาใกล้ 1        →  step ตาม 6 − szDecimals
```

## กฎขนาดไม้

```
lot_step = 10 ^ -szDecimals
```

`szDecimals` อ่านจาก `meta()` ของแต่ละเหรียญ ตัวอย่างจริง:

| เหรียญ | szDecimals | lot step | ทศนิยมราคาสูงสุด |
|---|---|---|---|
| BTC | 5 | 0.00001 | 1 |
| ETH | 4 | 0.0001 | 2 |
| SOL | 2 | 0.01 | 4 |

ปัด**ลง**เสมอ แล้วปฏิเสธถ้าได้ศูนย์

## ชื่อสินค้า

ใช้**ชื่อเหรียญเปล่าๆ**: `BTC` `ETH` `SOL` — ไม่ใช่ `BTCUSDT` หรือ `BTC_USDT_Perp`
asset id ที่ `/exchange` ต้องการคือ **ลำดับใน `universe`** ที่ `meta()` คืนมา

## ข้อมูลที่ดึงได้ (ไม่ต้องมีคีย์)

| ต้องการ | เรียกอะไร |
|---|---|
| metadata ทุกเหรียญ (szDecimals, maxLeverage) | `meta()` |
| ราคา mark ของทุกเหรียญ | `meta_and_asset_ctxs()` → `ctxs[i].markPx` |
| ราคากลางทุกเหรียญ | `all_mids()` |
| แท่งเทียน OHLCV | `candles_snapshot(coin, interval, startMs, endMs)` |
| order book | `l2_snapshot(coin)` |

interval ที่รับ: `1m 3m 5m 15m 30m 1h 2h 4h 8h 12h 1d 3d 1w 1M`

แท่งเทียนมีคีย์ `t` (เวลาเปิด ms) `o h l c v` — **ใช้ warm-up อินดิเคเตอร์ตอนบอทเริ่มได้**
ไม่ต้องรอสังเกตราคาทีละรอบ

## ข้อมูลบัญชี (ต้องมี address บัญชีแม่)

`user_state(account_address)` คืน:

```
marginSummary.accountValue          ยอดพอร์ตรวม (สตริง)
assetPositions[].position.coin      เหรียญ
assetPositions[].position.szi       ขนาด "มีเครื่องหมาย" บวก=long ลบ=short
assetPositions[].position.entryPx   ราคาเข้า
```

⚠️ แถวที่ `szi` เป็น 0 ต้อง**ทิ้ง** ตลาดยังรายงานเหรียญที่ปิดไปแล้วด้วยขนาดศูนย์
ถ้านับเป็น position ที่เปิดอยู่ risk gate จะปฏิเสธการเทรดเหรียญนั้นตลอดไป

## ส่งออเดอร์

Python SDK: `pip install hyperliquid-python-sdk`

```python
from hyperliquid.info import Info
from hyperliquid.exchange import Exchange
from hyperliquid.utils import constants
from hyperliquid.utils.types import Cloid
from eth_account import Account

info = Info(constants.TESTNET_API_URL, skip_ws=True)
wallet = Account.from_key(api_wallet_key)           # คีย์ของ agent
exchange = Exchange(wallet, constants.TESTNET_API_URL,
                    account_address=master_address)  # address ของบัญชีแม่

result = exchange.order(
    "BTC", True, 0.001, 100000.0,                   # coin, is_buy, size, limit price
    {"limit": {"tif": "Gtc"}},                      # Gtc | Ioc | Alo
    reduce_only=False,
    cloid=Cloid.from_str("0x" + hex32),             # ต้อง 0x + 32 hex พอดี
)
```

- `tif` : `Gtc` ค้างในกระดาน · `Ioc` ไม่ fill ก็ยกเลิกทันที · `Alo` ยกเลิกถ้าจะ match ทันที
- ปิด position: `reduce_only=True` + `Ioc` ที่ราคาไล่ข้ามกระดาน (เช่น ±5% จาก mark)
- ยกเลิกด้วย cloid ของเราเอง: `exchange.cancel_by_cloid(coin, cloid)`
- ตั้ง leverage ได้จริง: `exchange.update_leverage(n, coin, is_cross)` — แต่**บอทไม่ควรเรียกเอง**
  ลูปเทรดไม่ควรไปแก้ setting บัญชีเงียบๆ ให้คุม exposure ด้วยกฎของบอทแทน

### cloid — กุญแจกันสั่งซ้ำที่ตลาดบังคับให้

ต้องเป็น `0x` + **32 ตัวอักษร hex พอดี** (128 bit)

ทางที่ดีคือทำให้มันเป็นค่าที่คำนวณได้จากตัวสัญญาณเอง เช่น
`sha256(เหรียญ|ฝั่ง|ราคาเข้า|ราคา stop|เวลาหมดอายุ)` ตัด 32 ตัวแรก
→ สัญญาณเดิมได้ cloid เดิมเสมอ → ส่งซ้ำตลาดปฏิเสธเอง

## การอ่านคำตอบของออเดอร์

```
{"status": "ok", "response": {"type": "order", "data": {"statuses": [...]}}}
```

`statuses[0]` เป็นอย่างใดอย่างหนึ่ง:

| รูปแบบ | ความหมาย |
|---|---|
| `{"resting": {"oid": 123}}` | ค้างในกระดาน |
| `{"filled": {"totalSz": "...", "avgPx": "...", "oid": 123}}` | fill แล้ว |
| `{"error": "..."}` | **ปฏิเสธ** เช่น `"Order must have minimum value of $10."` |

ไม่เจอ `oid` = ถือว่า **error** ห้ามนับเป็นสำเร็จ (ดู `refs/pitfalls.md` ข้อ 5)

## เช็คลิสต์ทดสอบการเชื่อมต่อสำหรับ Hyperliquid

ใช้แทน 4 ข้อใน SKILL ได้เลย

```
[ ] meta() คืน universe ที่มีเหรียญที่จะเทรด                    (ไม่ต้องมีคีย์)
[ ] markPx ของเหรียญนั้นเป็นค่าบวก                              (ไม่ต้องมีคีย์)
[ ] candles_snapshot คืนแท่งเทียนเรียงตามเวลา                   (ไม่ต้องมีคีย์)
[ ] user_state(บัญชีแม่) คืน accountValue  ← ถ้าว่าง = ใส่ address ผิดตัว
[ ] วาง limit order ห่างตลาด 30% แล้ว cancel_by_cloid ได้
[ ] ลองส่งออเดอร์มูลค่าต่ำกว่า $10 แล้วจับ error ได้ ไม่ใช่เงียบ
```

ข้อ 1–3 ทำได้ก่อนที่ผู้ใช้จะมีบัญชีด้วยซ้ำ — ใช้พิสูจน์ว่าโค้ดอ่านตลาดถูกตั้งแต่ยังไม่สมัคร
