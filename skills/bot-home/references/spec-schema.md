# สเปคบอท — ช่องทั้งหมดและความหมาย

ไฟล์เหล่านี้คือ **แหล่งความจริงเดียว** ของบอท โค้ดทุกบรรทัดต้องถูกสร้างจากไฟล์พวกนี้
ถ้าผู้ใช้อยากเปลี่ยนพฤติกรรมบอท ให้แก้ที่นี่ ไม่ใช่แก้โค้ด

---

## bot/profile.yaml

```yaml
owner: "ไพรัตน์"
experience: beginner          # beginner | some | experienced
capital:
  amount: 50000
  currency: THB
  is_risk_capital: true       # true = เงินที่เสียทั้งหมดแล้วชีวิตไม่เปลี่ยน
pain_threshold:
  max_drawdown_pct: 15        # ขาดทุนสูงสุดจากจุดสูงสุดที่ยังนอนหลับได้
  max_losing_months: 4        # ขาดทุนติดกันกี่เดือนถึงจะทนไม่ไหว
attention:
  minutes_per_day: 15         # เวลาที่ดูบอทได้จริงต่อวัน
  can_wake_at_night: false
market: crypto                # crypto | thai_stock | tfex | forex | us_stock
goal: "ให้เงินก้อนนี้โตเร็วกว่าฝากธนาคาร โดยไม่ต้องนั่งเฝ้าจอ"
hard_no:                      # สิ่งที่ยอมไม่ได้เด็ดขาด
  - "ห้ามใช้ leverage เกิน 3 เท่า"
  - "ห้ามเทรดหุ้นรายตัวที่ปั่น"
```

## bot/strategy.yaml

```yaml
name: "btc-trend-h4"
archetype: trend_following    # ดูรายชื่อได้ใน skills/bot-strategy/references/catalog.md
universe:
  - BTCUSDT
timeframe: H4
direction: long_only          # long_only | short_only | both

entry:
  conditions:                 # ต้องเป็นจริง "ทุกข้อ" ถึงจะเข้า
    - "ema(50) > ema(200)"
    - "close > highest(high, 20)[1]"
  confirm:                    # ยืนยันเพิ่ม (ไม่บังคับ)
    - "volume > sma(volume, 20)"

exit:
  stop_loss:
    type: atr                 # atr | percent | structure | fixed
    atr_period: 14
    atr_multiple: 2.0
  take_profit:
    type: r_multiple          # r_multiple | percent | trailing | none
    r: 3.0
  trailing:
    type: chandelier
    atr_multiple: 3.0
    activate_after_r: 1.0
  time_stop_bars: 60          # ถือเกินกี่แท่งแล้วยังไม่ไปไหน ให้ออก

signal_ttl:
  valid_bars: 1               # สัญญาณหมดอายุใน 1 แท่ง — กันเข้าไม้ย้อนหลัง
  max_slippage_pct: 0.15      # ราคาวิ่งเกินนี้ = ยกเลิก ไม่ไล่ราคา

filters:                      # ห้ามเทรดเมื่อ...
  - "atr(14) / close < 0.005"       # ตลาดนิ่งเกินไป
  - "within_minutes_of_news(30)"    # ใกล้ข่าวใหญ่

llm_lanes: []                 # ว่างไว้ก่อน ใส่ทีหลังสุด ดู bot-scaffold
```

## bot/risk.yaml

```yaml
sizing:
  method: fixed_fractional    # fixed_fractional | atr_risk | fixed_notional
  risk_per_trade_pct: 0.5     # เสี่ยง 0.5% ของพอร์ตต่อไม้
  max_position_pct: 20        # ไม้เดียวห้ามเกิน 20% ของพอร์ต

limits:
  max_concurrent_positions: 3
  max_trades_per_day: 5
  max_daily_loss_pct: 2       # ถึงแล้วหยุดเทรดทั้งวัน
  max_weekly_loss_pct: 5
  max_drawdown_pct: 15        # ถึงแล้ว = KILL SWITCH รอมนุษย์ปลดล็อก
  max_leverage: 2
  max_correlated_exposure_pct: 30   # สินทรัพย์ที่วิ่งตามกันรวมกันห้ามเกินนี้

trading_window:
  timezone: Asia/Bangkok
  allowed_hours: "00:00-23:59"
  blackout:
    - "15 นาทีก่อนและหลังประกาศ FOMC"
    - "วันหยุดที่สภาพคล่องบาง"

requires_human_confirm:       # สิ่งที่บอทห้ามทำเองเด็ดขาด
  - increase_position_size
  - increase_leverage
  - withdraw_funds
  - disable_risk_engine
  - trade_outside_window
  - resume_after_kill_switch
```

## bot/connection.yaml

⚠️ **ช่อง `secrets` หน้าตาไม่เหมือนกันในแต่ละเอ็กซ์เชนจ์** ห้ามคัดลอกตัวอย่างของที่หนึ่ง
ไปใช้กับอีกที่หนึ่ง และห้ามเดาว่าผู้ใช้ใช้เอ็กซ์เชนจ์ไหน — ต้องรู้คำตอบก่อนเขียนไฟล์นี้
(ดูขั้นที่ 0 ใน `/bot:connect`)

### แบบ GRVT — ค่าเริ่มต้นของโปรเจคนี้

```yaml
exchange: grvt

data:
  provider: grvt
  type: rest_poll            # websocket | rest_poll | csv
  history_source: grvt_ohlcv # fetch_ohlcv ของ SDK
  symbol: BTC_USDT_Perp      # ชื่อเป็นคู่เทรด ไม่ใช่ BTCUSDT หรือ BTC
  interval: 4h
  storage_timezone: UTC
  quality_checks:
    - no_gaps
    - timezone_normalized_utc
  use_closed_bars_only: true

broker:
  name: grvt
  env: testnet               # testnet | prod  (prod ต้องใส่ --live)
  mode: paper                # paper | live
  order_type: limit          # เข้าเป็น limit เสมอ ปิดด้วย market + reduce_only
  idempotency: client_order_id   # ⚠️ GRVT รับเป็น "ตัวเลข" (uint32)
  reconcile_every_seconds: 30

secrets:
  source: env                # อ่านจาก bot/.env เท่านั้น
  required_keys:
    - GRVT_API_KEY
    - GRVT_PRIVATE_KEY
    - GRVT_TRADING_ACCOUNT_ID
  key_permissions_required:
    - trade
  key_permissions_forbidden:
    - withdraw               # ห้ามเปิดสิทธิ์ถอนเงินเด็ดขาด
  notes:
    - "tick_size / min_size / base_decimals อ่านจาก fetch_market ไม่ต้องเดา"
    - "min_size เป็นจำนวนสินค้า ไม่ใช่มูลค่า จึงมีด่านขั้นต่ำสองชั้น"
```

### แบบ Hyperliquid — perp DEX ที่ใช้ API wallet (ทางเลือก)

```yaml
data:
  provider: hyperliquid
  type: rest_poll            # websocket | rest_poll | csv
  history_source: hyperliquid_candles   # /info candleSnapshot ฟรี ไม่ต้องมีกุญแจ
  timeframe: 5m
  quality_checks:
    - no_gaps
    - timezone_normalized_utc

broker:
  name: hyperliquid
  network: testnet           # testnet | mainnet
  mode: paper                # paper | live
  order_type: limit          # เข้าเป็น limit เสมอ ปิดด้วย ioc ที่ไล่ราคา
  idempotency: cloid         # 0x + 32 hex ตลาดบังคับกฎห้ามซ้ำให้อีกชั้น
  min_notional_usd: 10
  reconcile_every_seconds: 30

secrets:
  source: env                # อ่านจาก bot/.env เท่านั้น
  required_keys:
    - HYPERLIQUID_ACCOUNT_ADDRESS   # บัญชีแม่ ใช้ query (ไม่ใช่ความลับ แต่เก็บรวมไว้)
    - HYPERLIQUID_API_WALLET_KEY    # private key ของ agent ใช้เซ็นอย่างเดียว
  notes:
    - "API wallet ถอนเงินไม่ได้โดยธรรมชาติ จึงไม่มีช่องสิทธิ์ให้ตั้ง"
    - "ห้ามเอา address ของ agent ไป query ตลาดจะตอบสถานะว่างโดยไม่แจ้ง error"
```

### แบบ CEX ที่ใช้ API key + secret (Binance, Bybit, OKX... — ต้องเขียน broker เพิ่ม)

```yaml
data:
  provider: binance
  type: websocket
  history_source: binance_klines
  history_from: "2019-01-01"
  quality_checks:
    - no_gaps
    - no_zero_volume_bars
    - timezone_normalized_utc

broker:
  name: binance
  mode: testnet              # testnet | paper | live
  order_type: limit
  idempotency: client_order_id
  reconcile_every_seconds: 30

secrets:
  source: env
  required_keys:
    - BINANCE_API_KEY
    - BINANCE_API_SECRET
  key_permissions_required:
    - read
    - spot_trade
  key_permissions_forbidden:
    - withdraw               # ห้ามเปิดสิทธิ์ถอนเงินเด็ดขาด
```

---

## กติกาเวลาเขียนไฟล์พวกนี้

- ทุกค่าที่เดาเอา ต้องใส่คอมเมนต์ `# TODO: ยังไม่ได้ยืนยันกับผู้ใช้` กำกับ
- ห้ามใส่ค่าที่ผู้ใช้ยังไม่ได้ตอบ แล้วทำเหมือนเขาตอบแล้ว
- ตัวเลขเงินทุกช่อง ใช้ทศนิยมแบบตายตัว (decimal) ห้ามใช้ float ในโค้ดที่ gen ออกมา
- `bot/.env` ต้องถูกเพิ่มใน `.gitignore` ทันทีที่สร้าง และห้ามพิมพ์ค่าในนั้นออกหน้าจอ
