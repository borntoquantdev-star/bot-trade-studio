#!/usr/bin/env python3
"""
สร้างตัวต่อ (adapter) สำหรับ host อื่นจาก skills/ ซึ่งเป็นแหล่งความจริงเดียว

    python tools/build-adapters.py

ผลลัพธ์อยู่ใน dist/ :
    dist/portable/.ai/trading/*.md          เนื้อหากลาง ใช้ได้กับทุกเครื่องมือ
    dist/portable/AGENTS.md                 Codex CLI, Cursor, Gemini CLI, Jules
    dist/portable/.github/copilot-instructions.md   GitHub Copilot (VS Code + CLI)
    dist/portable/.github/prompts/*.prompt.md       slash command ของ Copilot
    dist/codex-prompts/*.md                 คัดลอกไป ~/.codex/prompts/
"""
import json, os, re, shutil, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILLS = os.path.join(ROOT, "skills")
DIST = os.path.join(ROOT, "dist")

ORDER = [
    "bot-home", "bot-profile", "bot-strategy", "bot-risk", "bot-connect",
    "bot-backtest", "bot-paper", "bot-deploy", "bot-monitor",
    "bot-panic", "bot-tune", "bot-reality-check", "bot-explain", "bot-scaffold",
]
STAGE = {
    "bot-home": "0", "bot-profile": "1", "bot-strategy": "2", "bot-risk": "3",
    "bot-connect": "4", "bot-backtest": "5", "bot-paper": "6", "bot-deploy": "7",
    "bot-monitor": "8",
}
# เส้นทางอ้างอิงที่ต้องเขียนใหม่ให้แบนราบ
REF_FIX = [
    (r"\.\./bot-home/references/spec-schema\.md", "refs/spec-schema.md"),
    (r"\.\./bot-strategy/references/catalog\.md", "refs/catalog.md"),
    (r"\.\./bot-risk/references/sizing\.md", "refs/sizing.md"),
    (r"\.\./bot-explain/references/glossary\.md", "refs/glossary.md"),
    (r"references/spec-schema\.md", "refs/spec-schema.md"),
    (r"references/catalog\.md", "refs/catalog.md"),
    (r"references/sizing\.md", "refs/sizing.md"),
    (r"references/glossary\.md", "refs/glossary.md"),
]


def read_skill(name):
    path = os.path.join(SKILLS, name, "SKILL.md")
    text = open(path, encoding="utf-8").read()
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if not m:
        sys.exit(f"frontmatter หาย: {path}")
    fm, body = m.group(1), m.group(2).strip()
    desc = re.search(r"^description:\s*(.+)$", fm, re.M).group(1).strip()
    for pat, rep in REF_FIX:
        body = re.sub(pat, rep, body)
    return desc, body


def slash(name):
    """bot-home -> /bot:home ; bot-strategy -> /bot:strategy (Claude) / bot-strategy (อื่นๆ)"""
    return "/bot:home" if name == "bot-home" else "/bot:" + name[len("bot-"):]


def flat(name):
    return "bot" if name == "bot-home" else name


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w", encoding="utf-8", newline="\n").write(text)


def main():
    if os.path.isdir(DIST):
        shutil.rmtree(DIST)

    skills = {n: read_skill(n) for n in ORDER}
    portable = os.path.join(DIST, "portable")
    ai = os.path.join(portable, ".ai", "trading")

    # 1) เนื้อหากลาง
    for name in ORDER:
        desc, body = skills[name]
        stage = STAGE.get(name)
        head = f"# {flat(name)}" + (f"  ·  ขั้นที่ {stage}" if stage else "  ·  เรียกได้ตลอด")
        write(os.path.join(ai, flat(name) + ".md"),
              f"{head}\n\n> {desc}\n\n---\n\n{body}\n")

    # 2) เอกสารอ้างอิง
    os.makedirs(os.path.join(ai, "refs"), exist_ok=True)
    for src, dst in [
        ("bot-home/references/spec-schema.md", "spec-schema.md"),
        ("bot-strategy/references/catalog.md", "catalog.md"),
        ("bot-risk/references/sizing.md", "sizing.md"),
        ("bot-explain/references/glossary.md", "glossary.md"),
    ]:
        shutil.copyfile(os.path.join(SKILLS, src), os.path.join(ai, "refs", dst))

    # ตารางคำสั่งที่ใช้ซ้ำในทุก adapter
    rows = []
    for name in ORDER:
        desc = skills[name][0].split(" ใช้เมื่อ")[0].strip()
        rows.append(f"| `/{flat(name)}` | `.ai/trading/{flat(name)}.md` | {desc} |")
    table = ("| คำสั่ง | อ่านไฟล์นี้ | ทำอะไร |\n|---|---|---|\n" + "\n".join(rows))

    preamble = """# สตูดิโอสร้างบอทเทรด

โปรเจคนี้ใช้คู่มือชุดหนึ่งเพื่อพาผู้ใช้**ที่ไม่ได้เขียนโปรแกรม**สร้างบอทเทรด
คู่มืออยู่ใน `.ai/trading/` **อ่านไฟล์ที่เกี่ยวข้องก่อนลงมือทุกครั้ง** อย่าตอบจากความจำ

## หลักการที่ห้ามละเมิด

1. ผู้ใช้ไม่ต้องอ่านโค้ด — สเปคอยู่ในไฟล์ YAML ใต้ `bot/` ที่อ่านเป็นภาษาคนได้
2. AI เสนอ มนุษย์ตัดสิน เครื่องบังคับ — LLM ห้ามกดออเดอร์ ทุกสัญญาณต้องผ่าน risk engine ที่เป็นกฎตายตัว
3. ความเสี่ยงมาก่อนกำไร — ขั้นที่ 3 (`bot:risk`) ห้ามข้าม
4. ห้ามข้ามขั้นไปใช้เงินจริง — ไม่ผ่าน backtest และ paper ให้ปฏิเสธ
5. พูดตรง ไม่ขายฝัน

## ภาษา

ตอบเป็นภาษาไทย ใส่ศัพท์อังกฤษในวงเล็บครั้งแรกที่เจอ
"""

    # 3) AGENTS.md — Codex CLI, Cursor, Gemini CLI, Jules
    write(os.path.join(portable, "AGENTS.md"), f"""{preamble}
## คู่มือทั้งหมด

{table}

ถ้าผู้ใช้ไม่ได้ระบุคำสั่ง ให้เริ่มที่ `.ai/trading/bot.md` ซึ่งจะบอกว่าตอนนี้อยู่ขั้นไหน
""")

    # 4) GitHub Copilot — instructions + prompt files
    write(os.path.join(portable, ".github", "copilot-instructions.md"), f"""{preamble}
## คู่มือทั้งหมด

{table}

ใน VS Code และ Copilot CLI เรียกด้วย slash command ที่อยู่ใน `.github/prompts/`
""")
    for name in ORDER:
        desc, _ = skills[name]
        f = flat(name)
        write(os.path.join(portable, ".github", "prompts", f"{f}.prompt.md"),
              "---\n"
              "mode: agent\n"
              f"description: {desc.split(' ใช้เมื่อ')[0].strip()}\n"
              "---\n\n"
              f"อ่าน `.ai/trading/{f}.md` ให้ครบทั้งไฟล์ แล้วทำตามนั้นทุกขั้นตอน\n"
              "ถ้าไฟล์นั้นชี้ไปไฟล์อื่นใน `.ai/trading/refs/` ให้อ่านไฟล์นั้นด้วย\n\n"
              "สิ่งที่ผู้ใช้พิมพ์เพิ่มมา: ${input:args}\n")

    # 5) Codex CLI prompts — คัดลอกไป ~/.codex/prompts/
    for name in ORDER:
        f = flat(name)
        write(os.path.join(DIST, "codex-prompts", f"{f}.md"),
              f"อ่าน `.ai/trading/{f}.md` ในโปรเจคปัจจุบันให้ครบทั้งไฟล์ แล้วทำตามนั้นทุกขั้นตอน\n"
              "ถ้าไฟล์นั้นชี้ไปไฟล์อื่นใน `.ai/trading/refs/` ให้อ่านไฟล์นั้นด้วย\n\n"
              "สิ่งที่ผู้ใช้พิมพ์เพิ่มมา: $ARGUMENTS\n")

    n_files = sum(len(fs) for _, _, fs in os.walk(DIST))
    print(f"สร้างเสร็จ {n_files} ไฟล์ ใน dist/")
    for d in ("portable/.ai/trading", "portable/.github/prompts", "codex-prompts"):
        p = os.path.join(DIST, d.replace("/", os.sep))
        print(f"  {d:34s} {len(os.listdir(p))} รายการ")


if __name__ == "__main__":
    main()
