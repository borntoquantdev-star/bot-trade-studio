#!/usr/bin/env node
/**
 * ติดตั้งคู่มือสร้างบอทเทรดลงโปรเจคใดก็ได้ ด้วยคำสั่งเดียว
 *
 *   npx github:borntoquantdev-star/bot-trade-studio
 *
 * ไม่มี dependency ใช้แค่ไลบรารีมาตรฐานของ Node (>=18)
 * ตัวนี้ทำงานเหมือน tools/install-portable.py ทุกอย่าง มีไว้สองทางเพราะ
 * บางคนมี node แต่ไม่มี python และบางคนกลับกัน
 */

"use strict";

const fs = require("node:fs");
const path = require("node:path");
const os = require("node:os");

const ROOT = path.resolve(__dirname, "..");
const PORTABLE = path.join(ROOT, "dist", "portable");
const CODEX = path.join(ROOT, "dist", "codex-prompts");

const HELP = `
สตูดิโอสร้างบอทเทรด — ตัวติดตั้งคู่มือ

  npx github:borntoquantdev-star/bot-trade-studio [โฟลเดอร์] [ตัวเลือก]

โฟลเดอร์      ปลายทาง ถ้าไม่ใส่จะใช้โฟลเดอร์ปัจจุบัน

ตัวเลือก
  --force           เขียนทับไฟล์ที่มีอยู่แล้ว (ค่าตั้งต้นคือข้าม)
  --codex-global    คัดลอก slash command ไป ~/.codex/prompts/ ด้วย
  --only <ชื่อ>     ติดตั้งเฉพาะบางส่วน: core | claude | copilot | agents
                    ใส่ซ้ำได้ เช่น --only core --only claude
  --dry-run         บอกว่าจะทำอะไร แต่ยังไม่เขียนไฟล์
  --help            แสดงข้อความนี้

สิ่งที่คัดลอกไป
  .ai/trading/                      คู่มือกลาง ทุกเครื่องมืออ่านจากที่นี่   (core)
  .claude/commands/*.md             slash command ของ Claude Code         (claude)
  .github/copilot-instructions.md   GitHub Copilot                        (copilot)
  .github/prompts/*.prompt.md       slash command ของ Copilot             (copilot)
  AGENTS.md                         Codex CLI, Cursor, Gemini CLI         (agents)

ถ้าใช้ Claude Code อยู่แล้ว การลงเป็น plugin สะดวกกว่า
  /plugin install bot --marketplace borntoquantdev-star/bot-trade-studio
`;

const GROUPS = {
  core: [".ai"],
  claude: [".claude"],
  copilot: [".github"],
  agents: ["AGENTS.md"],
};

function parseArgs(argv) {
  const opts = {
    target: null,
    force: false,
    codexGlobal: false,
    only: [],
    dryRun: false,
    help: false,
  };
  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    if (arg === "--help" || arg === "-h") opts.help = true;
    else if (arg === "--force") opts.force = true;
    else if (arg === "--codex-global") opts.codexGlobal = true;
    else if (arg === "--dry-run") opts.dryRun = true;
    else if (arg === "--only") {
      const name = argv[i + 1];
      if (!name || !(name in GROUPS)) {
        fail(`--only รับได้แค่: ${Object.keys(GROUPS).join(" | ")}`);
      }
      opts.only.push(name);
      i += 1;
    } else if (arg.startsWith("-")) {
      fail(`ไม่รู้จักตัวเลือก ${arg}  (ลอง --help)`);
    } else if (opts.target === null) {
      opts.target = arg;
    } else {
      fail("ใส่โฟลเดอร์ปลายทางได้แค่หนึ่งที่");
    }
  }
  return opts;
}

function fail(message) {
  console.error(`\nหยุด: ${message}\n`);
  process.exit(2);
}

/** รายชื่อไฟล์ทั้งหมดใต้ dir คืนเป็น path ที่สัมพันธ์กับ dir */
function walk(dir, base = dir, out = []) {
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) walk(full, base, out);
    else if (entry.isFile()) out.push(path.relative(base, full));
  }
  return out;
}

function wanted(rel, only) {
  if (only.length === 0) return true;
  const head = rel.split(path.sep)[0];
  return only.some((name) => GROUPS[name].includes(head));
}

function copyInto(srcDir, destDir, { force, dryRun, only }) {
  const result = { copied: [], skipped: [] };
  for (const rel of walk(srcDir).sort()) {
    if (!wanted(rel, only)) continue;
    const target = path.join(destDir, rel);
    if (fs.existsSync(target) && !force) {
      result.skipped.push(rel);
      continue;
    }
    if (!dryRun) {
      fs.mkdirSync(path.dirname(target), { recursive: true });
      fs.copyFileSync(path.join(srcDir, rel), target);
    }
    result.copied.push(rel);
  }
  return result;
}

function main() {
  const opts = parseArgs(process.argv.slice(2));
  if (opts.help) {
    console.log(HELP);
    return 0;
  }

  if (!fs.existsSync(PORTABLE)) {
    fail(
      `ไม่พบ ${path.relative(ROOT, PORTABLE)} — ถ้ารันจากซอร์ส ให้สั่ง ` +
        "`python tools/build-adapters.py` ก่อน"
    );
  }

  const target = path.resolve(opts.target || process.cwd());
  if (!fs.existsSync(target)) {
    if (opts.dryRun) fail(`ไม่มีโฟลเดอร์ ${target}`);
    fs.mkdirSync(target, { recursive: true });
  }
  if (!fs.statSync(target).isDirectory()) fail(`${target} ไม่ใช่โฟลเดอร์`);

  console.log(`\nปลายทาง: ${target}`);
  if (opts.dryRun) console.log("(โหมด --dry-run ยังไม่เขียนไฟล์จริง)");

  const { copied, skipped } = copyInto(PORTABLE, target, opts);

  for (const rel of copied) console.log(`  + ${rel}`);
  if (skipped.length) {
    console.log(`\n  ข้าม ${skipped.length} ไฟล์ที่มีอยู่แล้ว (ใส่ --force ถ้าจะเขียนทับ)`);
    for (const rel of skipped.slice(0, 5)) console.log(`    · ${rel}`);
    if (skipped.length > 5) console.log(`    · ... และอีก ${skipped.length - 5} ไฟล์`);
  }

  if (opts.codexGlobal) {
    const dest = path.join(os.homedir(), ".codex", "prompts");
    console.log(`\nslash command ของ Codex -> ${dest}`);
    const res = copyInto(CODEX, dest, { ...opts, only: [] });
    console.log(`  คัดลอก ${res.copied.length} ไฟล์ ข้าม ${res.skipped.length} ไฟล์`);
  }

  if (copied.length === 0 && skipped.length > 0) {
    console.log("\nมีคู่มืออยู่ครบแล้ว ไม่มีอะไรต้องทำ");
  }

  console.log(`
ติดตั้งแล้ว ${copied.length} ไฟล์

เริ่มใช้งาน — เปิดโปรเจคนี้ในเครื่องมือที่ถนัดแล้วพิมพ์
  Claude Code   /bot                 (หรือลงเป็น plugin เพื่อได้ /bot:home)
  Copilot Chat  /bot
  Codex         "อ่าน .ai/trading/bot.md แล้วพาผมสร้างบอทเทรด"

ไม่รู้จะเริ่มตรงไหน ให้บอกว่า "อยากสร้างบอทเทรด" แล้วมันจะถามทีละขั้นเอง
คู่มือทั้งหมดอยู่ใน .ai/trading/ แก้ไขได้ตามใจ มันเป็นไฟล์ข้อความธรรมดา
`);
  return 0;
}

try {
  process.exit(main());
} catch (err) {
  console.error(`\nผิดพลาด: ${err && err.message ? err.message : err}\n`);
  process.exit(1);
}
