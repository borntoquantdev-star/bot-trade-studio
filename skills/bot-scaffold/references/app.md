# ติดตั้งโปรเจคบอท + แอพ TradeBot.exe

> อ่านไฟล์นี้เมื่อผู้ใช้ยังไม่มีโฟลเดอร์บอท (ไม่มี `tradebot/` กับ `config/`)
> หรือมีโฟลเดอร์แล้วแต่ยังไม่มี `TradeBot.exe` อยู่ข้างใน

เป้าหมายคือให้ผู้ใช้**ดับเบิลคลิกครั้งเดียวแล้วเห็นโปรแกรม** ไม่ต้องเปิด venv ไม่ต้อง cd ไม่ต้องจำ flag
**คุณ (AI) เป็นคนรันคำสั่งข้างล่างทั้งหมด** ผู้ใช้ไม่ต้องพิมพ์เอง

## 1. โค้ดบอท

เลือกทางแรกที่ใช้ได้ในเครื่องผู้ใช้ (ลองตามลำดับ):

```powershell
# มี gh และล็อกอินแล้ว: ได้รีโปของตัวเองบน GitHub เก็บประวัติทุกรอบที่แก้กลยุทธ์
gh repo create my-bot --template borntoquantdev-star/trade-bot --private --clone

# มีแค่ git
git clone https://github.com/borntoquantdev-star/trade-bot my-bot

# ไม่มีทั้งสองอย่าง
Invoke-WebRequest -UseBasicParsing https://github.com/borntoquantdev-star/trade-bot/archive/refs/heads/main.zip -OutFile trade-bot.zip
Expand-Archive trade-bot.zip . ; Rename-Item trade-bot-main my-bot ; Remove-Item trade-bot.zip
```

## 2. แอพ (TradeBot.exe + หน้าบอร์ด + ตัวติดตั้ง Python)

แอพ build ไว้แล้วอยู่ที่หน้า Releases ของแม่แบบ ไม่ต้องลง Rust ไม่ต้อง build เอง

```powershell
cd my-bot
Invoke-WebRequest -UseBasicParsing https://github.com/borntoquantdev-star/trade-bot/releases/latest/download/board-pack.zip -OutFile board-pack.zip
Expand-Archive board-pack.zip board-pack -Force
Copy-Item board-pack\TradeBot.exe . -Force
Remove-Item board-pack.zip
```

- `board-pack\` กับ `TradeBot.exe` อยู่ใน `.gitignore` ของแม่แบบแล้ว ไม่หลุดขึ้น GitHub
- โหลดไม่ได้ (404) แปลว่ายังไม่มี release บอกผู้ใช้ตรงๆ แล้วใช้ทาง CLI ใน `/bot:demo` ไปก่อน ห้ามพยายาม build เอง

## 3. ให้ผู้ใช้เปิด

บอกผู้ใช้ประมาณนี้:

> ดับเบิลคลิก `TradeBot.exe` ในโฟลเดอร์ `my-bot` ครั้งแรกโปรแกรมจะลง Python ให้เอง ใช้เวลาประมาณ 1-2 นาทีและต้องมีเน็ต
> ถ้า Windows ขึ้นจอฟ้า ให้กด "More info" แล้วกด "Run anyway" (โปรแกรมไม่มีลายเซ็น ไม่ใช่ไวรัส)
> เบราว์เซอร์จะเปิดการ์ด "ควบคุม" ขึ้นมาเอง

**ห้ามปิดหน้าต่างสีดำ** ตราบที่ยังใช้งานอยู่ เพราะปิดแล้วบอทจะหยุดตามทันที

## สิ่งที่ผู้ใช้ทำในแอพได้

| ปุ่ม | ทำอะไร |
|---|---|
| รายการกลยุทธ์ | กรณีศึกษา 1 `ping_pong` (เครื่องทดสอบ) · กรณีศึกษา 2 `ma_cross` (ตามเทรนด์) · และทุกกลยุทธ์ที่เขาเขียนเอง |
| กระดาษ / testnet | กระดาษไม่ต้องมีกุญแจ · testnet ต้องใส่กุญแจในการ์ดก่อน · **ไม่มีเงินจริงในแอพ** |
| ดึงข้อมูล + ตรวจกลยุทธ์ | `--check` ของกลยุทธ์ที่เลือก ต้องผ่านก่อนรัน testnet |
| เริ่มบอท / หยุดบอท | หยุดแล้วบอทปิดไม้ก่อนออก |
| ปลดล็อก | ล้าง halt (ล็อกขาดทุนรายวันปลดเองตอนเที่ยงคืนไทยอยู่แล้ว) |

## หลังติดตั้ง AI ใช้บอทตัวไหน

แอพสร้าง `.venv` ไว้ในโฟลเดอร์บอท ให้ใช้ตัวนั้นเสมอ: `.venv\Scripts\tradebot.exe`
ถ้าผู้ใช้ยังไม่เคยเปิดแอพ `.venv` จะยังไม่มี ให้เขาเปิดแอพหนึ่งครั้งก่อน
หรือสร้างเองด้วย `python -m venv .venv` แล้ว `.venv\Scripts\python.exe -m pip install -e ".[dev,grvt]"`

**ห้ามสั่ง `tradebot` รันบอทจากแชทขณะที่บอทในแอพกำลังรัน** บอทสองตัวจะเขียนไฟล์ state เดียวกัน
คำสั่งที่อ่านอย่างเดียว (`--check`, `--backtest`, `--list-strategies`) รันได้
