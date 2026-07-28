/**
 * Renders a contact sheet of the whole film so pacing and framing can be
 * reviewed at a glance. Not part of the delivery pipeline — this is a
 * review aid.
 *
 *   node tools/contact-sheet.mjs [count] [from] [to] [cols] [thumbWidth]
 */
import { chromium } from 'playwright';
import { mkdir, writeFile } from 'node:fs/promises';
import path from 'node:path';

const URL = process.env.REVEAL_URL ?? 'http://localhost:5183/?render=1';
const COUNT = Number(process.argv[2] ?? 24);
const FROM = process.argv[3] != null ? Number(process.argv[3]) : null;
const TO = process.argv[4] != null ? Number(process.argv[4]) : null;
const COLS = Number(process.argv[5] ?? 6);
const THUMB_W = Number(process.argv[6] ?? 240);
const OUT = path.resolve('out/contact');

const browser = await chromium.launch();
const page = await browser.newPage({
  viewport: { width: 1080, height: 1920 },
  deviceScaleFactor: 1,
});

await page.goto(URL, { waitUntil: 'load' });
await page.waitForFunction(() => window.__reveal?.ready === true, null, { timeout: 60000 });

const total = await page.evaluate(() => window.__reveal.TOTAL_DURATION);
const from = FROM ?? 0;
const to = TO ?? total;
await mkdir(OUT, { recursive: true });

const shots = [];
for (let i = 0; i < COUNT; i++) {
  const t = from + (i / (COUNT - 1)) * (to - from);
  await page.evaluate((time) => window.__reveal.seek(time), t);
  const buf = await page.locator('#stage').screenshot();
  shots.push({ t, data: buf.toString('base64') });
  process.stdout.write(`\rframe ${i + 1}/${COUNT}`);
}

const rows = Math.ceil(COUNT / COLS);
const html = `<!doctype html><meta charset="utf-8"><title>contact sheet</title>
<style>
 body{margin:0;background:#111;color:#ccc;font:12px system-ui;padding:8px}
 .grid{display:grid;grid-template-columns:repeat(${COLS},${THUMB_W}px);gap:6px}
 figure{margin:0}
 img{width:${THUMB_W}px;display:block;background:#000}
 figcaption{padding:2px}
</style>
<div class="grid">
${shots.map((s) => `<figure><img src="data:image/png;base64,${s.data}"><figcaption>${s.t.toFixed(2)}s</figcaption></figure>`).join('\n')}
</div>`;

await writeFile(path.join(OUT, 'index.html'), html);
await browser.close();
console.log(`\ncontact sheet: ${path.join(OUT, 'index.html')} (${rows} rows)`);
