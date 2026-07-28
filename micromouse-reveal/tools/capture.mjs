/**
 * Deterministic frame capture.
 *
 * The page never animates on its own — main.js exposes __reveal.seek(t), and
 * this walks the timeline one frame at a time. Nothing depends on wall-clock
 * timing, so the same frames come out on every run.
 *
 *   node tools/capture.mjs            # resume (skips frames already on disk)
 *   node tools/capture.mjs --fresh    # delete out/frames first
 *
 * Capture runs in batches, relaunching the browser between them. A single
 * long-lived page accumulates enough renderer memory over a few hundred
 * 1080x1920 screenshots that it dies mid-run, and because every frame is
 * addressed by absolute time rather than by playback state, restarting costs
 * nothing and the output is identical.
 */
import { chromium } from 'playwright';
import { mkdir, rm, access } from 'node:fs/promises';
import path from 'node:path';

const URL = process.env.REVEAL_URL ?? 'http://localhost:5183/?render=1';
const OUT = path.resolve('out/frames');
const BATCH = Number(process.env.CAPTURE_BATCH ?? 250);
const FRESH = process.argv.includes('--fresh');

const framePath = (f) => path.join(OUT, `${String(f).padStart(5, '0')}.png`);
const exists = (p) =>
  access(p).then(
    () => true,
    () => false,
  );

async function openPage() {
  const browser = await chromium.launch({
    args: ['--force-device-scale-factor=1', '--hide-scrollbars', '--mute-audio'],
  });
  const page = await browser.newPage({
    viewport: { width: 1080, height: 1920 },
    deviceScaleFactor: 1,
  });
  page.on('pageerror', (e) => console.error('\n[page error]', e.message));
  page.on('crash', () => console.error('\n[page crashed]'));
  await page.goto(URL, { waitUntil: 'load' });
  await page.waitForFunction(() => window.__reveal?.ready === true, null, { timeout: 120000 });
  return { browser, page };
}

if (FRESH) await rm(OUT, { recursive: true, force: true });
await mkdir(OUT, { recursive: true });

let { browser, page } = await openPage();
const totalFrames = await page.evaluate(() => window.__reveal.TOTAL_FRAMES);
const fps = await page.evaluate(() => window.__reveal.FPS);
console.log(`capturing ${totalFrames} frames @ ${fps}fps (batches of ${BATCH})`);

const started = Date.now();
let sinceRestart = 0;
let captured = 0;
let skipped = 0;

for (let f = 0; f < totalFrames; f++) {
  if (await exists(framePath(f))) {
    skipped++;
    continue;
  }

  if (sinceRestart >= BATCH) {
    await browser.close();
    ({ browser, page } = await openPage());
    sinceRestart = 0;
  }

  // One retry: a dead renderer is recoverable because the frame is addressed
  // by absolute time, not by where playback happens to be.
  for (let attempt = 0; attempt < 2; attempt++) {
    try {
      // seek() is async: the video tail must present its frame before we shoot.
      await page.evaluate((frame) => window.__reveal.seek(frame / window.__reveal.FPS), f);
      await page.locator('#stage').screenshot({ path: framePath(f) });
      break;
    } catch (err) {
      if (attempt === 1) throw err;
      console.error(`\n[frame ${f}] ${err.message.split('\n')[0]} — restarting browser`);
      await browser.close().catch(() => {});
      ({ browser, page } = await openPage());
      sinceRestart = 0;
    }
  }

  sinceRestart++;
  captured++;

  if (f % 30 === 0 || f === totalFrames - 1) {
    const elapsed = (Date.now() - started) / 1000;
    const rate = captured / Math.max(elapsed, 0.001);
    const left = totalFrames - f - 1;
    console.log(
      `  ${(((f + 1) / totalFrames) * 100).toFixed(1)}%  ${f + 1}/${totalFrames}  ` +
        `${elapsed.toFixed(0)}s elapsed  ~${(left / Math.max(rate, 0.001)).toFixed(0)}s left`,
    );
  }
}

await browser.close();
console.log(`\ndone: ${captured} captured, ${skipped} already present → ${OUT}`);
