# bot-trade-studio

ชุด skills สำหรับ Claude Code ที่พา **คนที่ไม่ได้เขียนโปรแกรม** สร้างบอทเทรดจนใช้ได้จริง
ผู้ใช้ตอบคำถาม → AI แปลงเป็นสเปค YAML ที่อ่านเป็นภาษาคนได้ → ค่อย generate โค้ดจากสเปคนั้น

## ติดตั้ง

### ใช้ได้ทุกเครื่องมือ — คำสั่งเดียว

```bash
npx github:borntoquantdev-star/bot-trade-studio
```

คัดลอกคู่มือลงโปรเจคที่อยู่ปัจจุบัน แล้วใช้ได้ทันทีกับ Claude Code, Codex, Copilot, Cursor
ไม่ต้อง clone ไม่ต้องมีบัญชี npm ไม่ต้องลงอะไรค้างในเครื่อง

```bash
npx github:borntoquantdev-star/bot-trade-studio --help          # ดูตัวเลือกทั้งหมด
npx github:borntoquantdev-star/bot-trade-studio ./my-bot        # ระบุโฟลเดอร์
npx github:borntoquantdev-star/bot-trade-studio --codex-global  # ใส่ slash command ให้ Codex ทั่วเครื่อง
npx github:borntoquantdev-star/bot-trade-studio --only core     # เอาแค่คู่มือกลาง
```

ไฟล์ที่มีอยู่แล้วจะถูกข้าม เว้นแต่ใส่ `--force` รันซ้ำได้ไม่เสียหาย

### ลงเป็น plugin ของ Claude Code (ได้ `/bot:home` และโหลด skill อัตโนมัติ)

พิมพ์ใน Claude Code บรรทัดเดียว (ต้องเป็นเวอร์ชัน 2.1.275 ขึ้นไป):

```
/plugin install bot --marketplace borntoquantdev-star/bot-trade-studio
```

เวอร์ชันเก่ากว่านั้นแยกเป็นสองบรรทัด:

```
/plugin marketplace add borntoquantdev-star/bot-trade-studio
/plugin install bot
```

ติดตั้งจากโฟลเดอร์ในเครื่อง หรือทดลองโดยไม่ติดตั้ง:

```bash
/plugin marketplace add /path/to/bot-trade-studio
claude --plugin-dir /path/to/bot-trade-studio
```

## เริ่มใช้

```
/bot:home
```

แล้ว AI จะถามว่าคุณเป็นใคร รับความเสี่ยงได้แค่ไหน แล้วแนะนำกลยุทธ์ที่เหมาะ

## คำสั่งทั้งหมด

**เส้นทางหลัก — ทำเรียงลำดับ**

| คำสั่ง | ทำอะไร | ได้ไฟล์ |
|---|---|---|
| `/bot:home` | ดูว่าอยู่ขั้นไหน ควรทำอะไรต่อ | `bot/STATUS.md` |
| `/bot:profile` | สัมภาษณ์ทุน ความเสี่ยงที่รับไหว เวลา ตลาด | `bot/profile.yaml` |
| `/bot:strategy` | เลือกกลยุทธ์จาก 10 แบบ แล้วแปลงเป็นกฎ | `bot/strategy.yaml` |
| `/bot:risk` | ขนาดไม้ เพดานขาดทุน kill switch | `bot/risk.yaml` |
| `/bot:connect` | ข้อมูลตลาด + โบรกเกอร์ + ความปลอดภัยของ key | `bot/connection.yaml` |
| `/bot:backtest` | ทดสอบย้อนหลัง + ตรวจ overfitting | `bot/reports/` |
| `/bot:paper` | เทรดกระดาษ + เกณฑ์จบการศึกษา 10 ข้อ | `bot/reports/` |
| `/bot:deploy` | ตรวจ 14 ข้อก่อนขึ้นเงินจริง | `bot/journal/` |
| `/bot:monitor` | เฝ้าระบบ 4 ชั้น + สมุดบันทึก | `bot/journal/` |

**เรียกได้ตลอด ไม่ต้องเรียงขั้น**

| คำสั่ง | ทำอะไร |
|---|---|
| `/bot:panic` | หยุดฉุกเฉิน — PAUSE / FLATTEN / KILL |
| `/bot:reality-check` | ค้านแผนคุณแบบตรงไปตรงมา |
| `/bot:tune` | ปรับพารามิเตอร์อย่างมีวินัย |
| `/bot:explain` | อธิบายศัพท์เป็นภาษาคน |
| `/bot:scaffold` | สร้างโค้ดจริงจากสเปค (Rust / Python) |

## ตัวอย่างที่เดินครบเส้นแล้ว

`example/bot/` คือสเปคจริงที่ได้จากการเดินขั้น 1–4 ของผู้ใช้สมมติ (ทุน 50,000 บาท มือใหม่ ดูจอได้ 15 นาที/วัน ห้าม leverage) เปิดอ่านได้เลยเพื่อดูว่าผลลัพธ์หน้าตาเป็นยังไง

จุดที่น่าดูที่สุดคือข้อขัดแย้งที่ `/bot:profile` จับได้: ผู้ใช้รับ drawdown ได้ 15% แต่กลยุทธ์ตามเทรนด์เจอ 25–40% เป็นปกติ ทางออกที่เลือกคือลงเงินแค่ครึ่งเดียว (`deployed_capital: 25000`) แล้ว `/bot:risk` ผูกตัวเลขนั้นกลับเป็น kill switch ที่ 30% ของทุนที่ลง = 15% ของทุนทั้งหมด ตรงกับที่ตอบไว้ตั้งแต่ขั้น 1

`example/bot/reports/backtest-EXAMPLE.md` เป็น**ตัวอย่างรูปแบบรายงาน ไม่ใช่ผลทดสอบจริง** ตัวเลขข้างในเป็นภาพประกอบ

## ใช้บนเครื่องมืออื่น (Codex CLI / Copilot CLI / VS Code / Cursor)

เนื้อหาทั้งหมดอยู่ใน `skills/` ซึ่งเป็น**แหล่งความจริงเดียว** ตัวต่อ (adapter) สำหรับ host อื่นถูก generate ออกมา ไม่ได้เขียนซ้ำ

ติดตั้งด้วย `npx` ตามหัวข้อข้างบน หรือถ้ามี python แต่ไม่มี node:

```bash
python tools/build-adapters.py                      # สร้าง dist/ (ตอน dev)
python tools/install-portable.py "C:/my-project"    # ติดตั้งลงโปรเจคใดก็ได้
python tools/install-portable.py "C:/my-project" --codex-global
```

ได้ไฟล์แบบนี้ในโปรเจคปลายทาง:

```
.ai/trading/            คู่มือ 14 ไฟล์ + refs/ 7 ไฟล์ — ทุกเครื่องมืออ่านจากที่นี่
.claude/commands/*.md               slash command ของ Claude Code (ระดับโปรเจค)
AGENTS.md               Codex CLI · Cursor · Gemini CLI · Jules
.github/copilot-instructions.md     GitHub Copilot (VS Code + CLI)
.github/prompts/*.prompt.md         slash command ของ Copilot
~/.codex/prompts/*.md               slash command ของ Codex (ใส่ --codex-global)
```

| เครื่องมือ | โมเดล | เรียกยังไง |
|---|---|---|
| Claude Code | Claude | `/bot:home` ถ้าลงเป็น plugin · `/bot` ถ้าลงด้วย npx |
| Codex CLI | ChatGPT | `/bot`, `/bot-strategy` (อ่าน `AGENTS.md` อัตโนมัติ) |
| Copilot CLI | Claude / ChatGPT | `/bot`, `/bot-strategy` |
| VS Code + Copilot Chat | Claude / ChatGPT | `/bot` ในช่องแชต (โหมด Agent) |
| Cursor | Claude / ChatGPT | อ่าน `AGENTS.md` เอง — สั่งเป็นภาษาพูดได้ |
| เครื่องมืออื่น | อะไรก็ได้ | สั่งว่า "อ่าน `.ai/trading/bot.md` แล้วทำตาม" |

**แก้เนื้อหาที่ `skills/` เสมอ แล้ว build ใหม่** อย่าแก้ที่ `dist/` เพราะจะถูกลบทิ้งทุกครั้งที่ build

### ข้อแตกต่างที่ควรรู้

- ชื่อคำสั่ง: Claude Code ใช้ `:` (`/bot:strategy`) host อื่นใช้ `-` (`/bot-strategy`) เพราะ `:` ใช้ในชื่อไฟล์ไม่ได้
- Claude Code โหลด skill ให้อัตโนมัติเมื่อบทสนทนาเข้าเรื่องที่ตรงกับ `description` — host อื่นต้องพิมพ์ slash command หรืออ้างไฟล์เอง
- `AskUserQuestion` (ปุ่มกดเลือก) มีเฉพาะ Claude Code — host อื่นจะถามเป็นข้อความธรรมดาแทน เนื้อหาคู่มือยังใช้ได้เหมือนกัน

## แม่แบบที่พิสูจน์แล้ว

`/bot:scaffold` ไม่ได้เขียนบอทขึ้นใหม่ทุกครั้งอีกแล้ว ถ้าผู้ใช้เทรดคริปโตและรับ Python ได้
มันจะเริ่มจาก [trade-bot](https://github.com/borntoquantdev-star/trade-bot)
ซึ่งผ่าน **297 เทส offline** และ CI เขียวบน Python 3.10–3.12

```bash
gh repo create my-bot --template borntoquantdev-star/trade-bot --private --clone
```

แล้วงานที่เหลือคือแมปสเปคจาก `bot/*.yaml` ลง config เขียนไฟล์กลยุทธ์ และเทสของมัน
ไม่ใช่การเขียน risk engine ขึ้นใหม่แล้วหวังว่าจะถูก

แม่แบบมี **dashboard** มาด้วย — `node dashboard/server.js --open` แล้วเห็นห้าขั้นของบอท
(ข้อมูลตลาด → กลยุทธ์ → ด่านความเสี่ยง → ส่งคำสั่ง → ไม้ที่ถืออยู่) เปลี่ยนสถานะสดๆ
พร้อมกราฟราคาและเหตุผลที่ถูกปฏิเสธ · มันอ่าน `logs/` ฝ่ายเดียว สั่งอะไรบอทไม่ได้

เอกสารอ้างอิง 3 ไฟล์ที่ skill อ่านก่อนลงมือ:

| ไฟล์ | เนื้อหา |
|---|---|
| `refs/template.md` | แม่แบบมีอะไร สัญญาของ `risk_gate` 13 เหตุผลปฏิเสธ สูตรขนาดไม้ สิ่งที่ต้องปรับตามสเปค |
| `refs/grvt.md` | **ตลาดหลัก** — สเปคสินค้าจาก fetch_market · min_size เป็นจำนวนสินค้า · client_order_id ต้องเป็นตัวเลข · กับดักสเกลราคา 1e9 · เช็คลิสต์ทดสอบ |
| `refs/hyperliquid.md` | กฎราคา 5 sig figs + 6−szDecimals · lot step · cloid 128 bit · กุญแจสองตัวที่คนสับสน · เช็คลิสต์ทดสอบ |
| `refs/choose-exchange.md` | เลือกสนามซ้อม: Binance Demo หรือ Hyperliquid testnet · **faucet ของ Hyperliquid ต้องเคย deposit mainnet ก่อน** · base URL ของทั้งสองฝั่ง |
| `refs/pitfalls.md` | กับดัก 11 ข้อจากการรีวิวบอทจริง — credential รั่วเพราะ shallow copy, ปัดเศษได้ศูนย์, ออเดอร์ล้มเหลวถูกนับเป็นสำเร็จ |
| `refs/dashboard.md` | หน้าดูบอททำงาน realtime — ห้า node ต่อกัน, อ่าน audit trail ฝ่ายเดียว, วิธีเอาไปใช้กับบอทที่ไม่ได้สร้างจากแม่แบบ |

## หลักการที่ฝังอยู่ในทุก skill

1. **ผู้ใช้ไม่ต้องอ่านโค้ด** — แก้พฤติกรรมบอทที่ YAML ไม่ใช่ที่โค้ด
2. **AI เสนอ มนุษย์ตัดสิน เครื่องบังคับ** — LLM ห้ามกดออเดอร์ ทุกสัญญาณต้องผ่าน risk engine ที่เป็นกฎตายตัว
3. **ความเสี่ยงมาก่อนกำไร** — ขั้น `/bot:risk` ห้ามข้าม
4. **ห้ามข้ามขั้นไปใช้เงินจริง** — ไม่ผ่าน backtest และ paper จะถูกปฏิเสธ
5. **พูดตรง** — ไม่ขายฝัน ไม่มีคำว่าชนะ 90%

## โครงไฟล์ที่ plugin สร้างในโปรเจคผู้ใช้

```
bot/
  STATUS.md        อยู่ขั้นไหน ติดอะไร ปรับจูนไปกี่รอบ
  profile.yaml     ทุน เพดานความเจ็บ เวลาที่ดูได้
  strategy.yaml    universe timeframe entry exit ttl filters
  risk.yaml        sizing limits trading_window requires_human_confirm
  connection.yaml  data broker secrets (ไม่มีค่า key)
  .env             key จริง — อยู่ใน .gitignore เสมอ
  reports/         ผล backtest / paper / สรุปรายเดือน
  journal/         บันทึกการตัดสินใจและการแทรกแซงทุกครั้ง
```

## คำเตือน

plugin นี้ช่วย **จัดกระบวนการ** ให้รัดกุม ไม่ได้รับประกันว่าบอทจะทำกำไร
การเทรดมีความเสี่ยงที่จะสูญเสียเงินต้นทั้งหมด ใช้เฉพาะเงินที่เสียได้
