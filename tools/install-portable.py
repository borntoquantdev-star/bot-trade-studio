#!/usr/bin/env python3
"""
ติดตั้งคู่มือลงโปรเจคใดก็ได้ เพื่อใช้กับ Codex CLI / Copilot CLI / VS Code / Cursor

    python tools/install-portable.py "C:/path/to/my-project"
    python tools/install-portable.py "C:/path/to/my-project" --codex-global

สิ่งที่คัดลอกไป:
    .ai/trading/                      คู่มือกลาง (ทุกเครื่องมืออ่านจากที่นี่)
    AGENTS.md                         Codex CLI, Cursor, Gemini CLI
    .github/copilot-instructions.md   GitHub Copilot
    .github/prompts/*.prompt.md       slash command ของ Copilot

--codex-global จะคัดลอก slash command ไป ~/.codex/prompts/ ด้วย
ไฟล์ที่มีอยู่แล้วจะไม่ถูกเขียนทับ เว้นแต่ใส่ --force
"""
import argparse, os, shutil, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "dist", "portable")
CODEX_SRC = os.path.join(ROOT, "dist", "codex-prompts")


def copy_tree(src, dst, force, log):
    for base, _, files in os.walk(src):
        rel = os.path.relpath(base, src)
        out = os.path.join(dst, rel) if rel != "." else dst
        os.makedirs(out, exist_ok=True)
        for f in files:
            target = os.path.join(out, f)
            shown = os.path.relpath(target, dst)
            if os.path.exists(target) and not force:
                log.append(("ข้าม (มีอยู่แล้ว)", shown))
                continue
            shutil.copyfile(os.path.join(base, f), target)
            log.append(("คัดลอก", shown))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("target", help="โฟลเดอร์โปรเจคปลายทาง")
    ap.add_argument("--force", action="store_true", help="เขียนทับไฟล์เดิม")
    ap.add_argument("--codex-global", action="store_true",
                    help="คัดลอก slash command ไป ~/.codex/prompts/ ด้วย")
    a = ap.parse_args()

    if not os.path.isdir(SRC):
        sys.exit("ยังไม่ได้ build — รัน  python tools/build-adapters.py  ก่อน")
    if not os.path.isdir(a.target):
        sys.exit(f"ไม่พบโฟลเดอร์ปลายทาง: {a.target}")

    log = []
    copy_tree(SRC, a.target, a.force, log)

    if a.codex_global:
        home = os.path.join(os.path.expanduser("~"), ".codex", "prompts")
        os.makedirs(home, exist_ok=True)
        copy_tree(CODEX_SRC, home, a.force, log)

    copied = sum(1 for k, _ in log if k == "คัดลอก")
    skipped = sum(1 for k, _ in log if k != "คัดลอก")
    for k, f in log:
        print(f"  {k:18s} {f}")
    print(f"\nคัดลอก {copied} ไฟล์ · ข้าม {skipped} ไฟล์")
    print(f"ปลายทาง: {a.target}")
    print("\nลองใช้: เปิด CLI ในโฟลเดอร์นั้นแล้วพิมพ์  /bot  (หรือสั่งว่า 'อ่าน AGENTS.md แล้วเริ่มสร้างบอทเทรด')")


if __name__ == "__main__":
    main()
