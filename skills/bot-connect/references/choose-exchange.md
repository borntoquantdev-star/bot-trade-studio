# เลือกสนามซ้อมให้ถูก — GRVT, Hyperliquid หรือ Binance

> อ่านไฟล์นี้ใน **ขั้นที่ 0** ของ `/bot:connect` ก่อนพูดเรื่องกุญแจ
> ผู้ใช้ส่วนใหญ่เป็นนักเรียนที่ยังไม่มีบัญชีอะไรเลย การเลือกผิดแปลว่าเขาไปสมัคร
> แล้วติดกำแพงที่ข้ามไม่ได้ เสียเวลาเป็นวัน

## กำแพงที่ต้องบอกก่อน ไม่ใช่ให้ไปเจอเอง

**Hyperliquid testnet ขอ mock USDC ได้เฉพาะคนที่เคยฝากเงินบน mainnet มาก่อน**

> "To use the testnet faucet, you need to have deposited on mainnet with the same address."
> — https://hyperliquid.gitbook.io/hyperliquid-docs/onboarding/testnet-faucet

ผ่านเงื่อนไขแล้วจะได้ **1,000 mock USDC** ที่ https://app.hyperliquid-testnet.xyz/drip

แปลว่า **ถ้านักเรียนยังไม่เคยฝากเงินจริงเข้า Hyperliquid เขาเทรด testnet ไม่ได้เลย**
ไม่มีเงินในบัญชีให้เปิดไม้ นี่ไม่ใช่เรื่องตั้งค่าผิด แต่เป็นกติกาของตลาด

⚠️ อีกกับดักของ Hyperliquid: ถ้าล็อกอินด้วย**อีเมล** (Privy) address บน mainnet
กับ testnet จะ**คนละอัน** ต้อง export wallet จาก mainnet แล้ว import เข้า Rabby
หรือ MetaMask ก่อน ถึงจะใช้ address เดียวกันได้

## ตารางตัดสินใจ

ถามผู้ใช้แค่สองข้อ แล้วชี้ทางได้เลย

| สถานการณ์ของผู้ใช้ | แนะนำ | เพราะ |
|---|---|---|
| ยังไม่มีบัญชีอะไรเลย อยากลองก่อน | **paper ในเครื่อง** (`--dry-run`) | ไม่ต้องสมัคร ไม่ต้องมีเงิน ไม่ต้องต่อเน็ต เริ่มได้ใน 1 นาที |
| อยากต่อตลาดจริงโดยไม่มีเงื่อนไขกั้น | **GRVT testnet** | แม่แบบรองรับในตัว · ไม่มีเงื่อนไขต้องเคยฝากเงินก่อน |
| มีบัญชี Binance อยู่แล้ว | **Binance Demo Trading** | ใช้บัญชีเดิมล็อกอิน กดรีเซ็ตยอดเงินเองได้ · แต่ต้องเขียน broker เพิ่ม |
| **ยังไม่เคยฝากเงินเข้า Hyperliquid** | **อย่าเพิ่งไป Hyperliquid testnet** | faucet จะไม่จ่าย mock USDC ให้ → เทรดไม่ได้ |
| เคยฝากเงินเข้า Hyperliquid mainnet แล้ว | **Hyperliquid testnet** | แม่แบบรองรับในตัว ขั้นต่ำ $10 ต่อไม้ |

**ทางที่ราบรื่นที่สุดสำหรับนักเรียนส่วนใหญ่คือ GRVT** เพราะแม่แบบรองรับอยู่แล้ว
และไม่มีกำแพงแบบ faucet ของ Hyperliquid

---

## ฝั่ง GRVT — testnet

```
env         testnet | prod          (ตั้งที่ grvt.env)
กุญแจ        api_key + private_key + trading_account_id  ออกที่หน้า API ของ GRVT
สินค้า       BTC_USDT_Perp (ชื่อเป็นคู่เทรด)
ขั้นต่ำ       มีทั้งมูลค่าขั้นต่ำ และ min_size (จำนวนสินค้า) ที่ตลาดประกาศมา
```

เปิดสิทธิ์เทรดอย่างเดียว **ปิดสิทธิ์ถอนเงิน** และ `grvt.env: prod` ต้องใส่ `--live` ด้วย
เอกสาร: https://api-docs.grvt.io/

ตั้งค่าในแม่แบบ:

```yaml
exchange: grvt
grvt:
  env: testnet
  api_key: "${GRVT_API_KEY}"
  private_key: "${GRVT_PRIVATE_KEY}"
  trading_account_id: "${GRVT_TRADING_ACCOUNT_ID}"
```

**ลำดับที่แนะนำสำหรับนักเรียน:** `paper ในเครื่อง → Binance Demo หรือ Hyperliquid testnet → เงินจริงน้อยๆ`
ข้ามขั้นแรกไม่ได้ช่วยอะไรเลย เพราะ paper ใช้โค้ดชุดเดียวกับของจริงอยู่แล้ว

## สิ่งที่ต้องบอกให้ชัด: แม่แบบรองรับอะไร

แม่แบบ `trade-bot` ที่ `/bot:scaffold` ใช้ มี broker มาให้ **สองตัว** คือ
**GRVT** กับ **Hyperliquid** (เลือกด้วย `exchange:` บรรทัดเดียว) บวก paper broker ที่ออฟไลน์

ถ้าผู้ใช้เลือก Binance ต้องบอกตรงๆ ว่าต้องเขียน broker เพิ่มเอง — ซึ่งไม่ยาก
เพราะสถาปัตยกรรมกันไว้แล้ว (เขียนคลาสเดียวตาม `Broker` protocol ใน
`hyperbot/brokers/base.py` แล้วแยกตัวอ่านคำตอบเป็นฟังก์ชัน pure เหมือน
`brokers/hyperliquid.py`) แต่ **`risk_gate` เอนจินและเทสทั้งหมดไม่ต้องแตะเลย**

อย่าบอกว่า "ใช้ได้เลย" ถ้ามันยังไม่มีโค้ด

---

## ฝั่ง Binance — Demo Trading

Binance มีสองสภาพแวดล้อมที่**ไม่ใช่อันเดียวกัน** อย่าสลับ

| | Demo Mode | Spot Testnet (ของเดิม) |
|---|---|---|
| รีเซ็ตยอดเงิน | กดเองได้ตลอดจาก UI | รีเซ็ตเองทุกเดือน |
| ล็อกอิน | บัญชี Binance ปกติ | บัญชีแยก |

**Spot — Demo Mode**
```
REST        https://demo-api.binance.com/api
WS API      wss://demo-ws-api.binance.com/ws-api/v3
WS streams  wss://demo-stream.binance.com/ws
กุญแจ        ล็อกอิน Binance → Demo Trading → API Key Management ที่ demo.binance.com
```

**USDS-M Futures**
```
REST (demo)       https://demo-fapi.binance.com
WS (demo)         wss://demo-fstream.binance.com
REST (ของจริง)     https://fapi.binance.com
```

เอกสาร:
- https://developers.binance.com/en/docs/products/spot/demo-mode/general-info
- https://developers.binance.com/en/docs/products/derivatives-trading-usds-futures/general-info

⚠️ ข้อมูลใน Demo Mode เป็น "realistic market data" แต่**ไม่ใช่ตลาดจริง** —
กลยุทธ์ที่ได้ผลใน demo ไม่รับประกันว่าได้ผลจริง ต้องบอกผู้ใช้ข้อนี้

กุญแจเป็นแบบ API key + secret → ใช้กฎสิทธิ์ตามปกติ: เปิดแค่ read + trade
**ปิด withdraw** และทำ IP whitelist

## ฝั่ง Hyperliquid — testnet

```
REST        https://api.hyperliquid-testnet.xyz
faucet      https://app.hyperliquid-testnet.xyz/drip   (ต้องเคย deposit mainnet)
กุญแจ        สร้าง API wallet ที่ https://app.hyperliquid.xyz/API
```

เก็บสองค่าคนละหน้าที่ — รายละเอียดใน `refs/hyperliquid.md`

- `account_address` บัญชีแม่ ใช้ query
- `api_wallet_key` private key ของ agent ใช้เซ็นอย่างเดียว ถอนเงินไม่ได้

## สคริปต์ที่ต้องเขียนให้ผู้ใช้

ไม่ว่าเลือกทางไหน ให้สร้าง `bot/.env.example` ที่มี**เฉพาะชื่อตัวแปรของทางที่เลือก**
ห้ามใส่ของทั้งสองค่ายปนกันในไฟล์เดียว เพราะผู้ใช้จะงงว่าต้องกรอกช่องไหน

```bash
# ถ้าเลือก GRVT
GRVT_API_KEY=
GRVT_PRIVATE_KEY=
GRVT_TRADING_ACCOUNT_ID=

# ถ้าเลือก Hyperliquid
HYPERLIQUID_ACCOUNT_ADDRESS=
HYPERLIQUID_API_WALLET_KEY=

# ถ้าเลือก Binance Demo (ต้องเขียน broker เพิ่มเอง)
BINANCE_DEMO_API_KEY=
BINANCE_DEMO_API_SECRET=
```

และต้องใส่ base URL ของ demo/testnet ลง `bot/connection.yaml` ให้ถูกตั้งแต่แรก
ไม่ใช่ค่าของ production — นี่คือจุดที่คนพลาดแล้วยิงออเดอร์ผิดที่
