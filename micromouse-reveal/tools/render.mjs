/**
 * Renders the film straight to MP4.
 *
 *   node tools/render.mjs
 *
 * Frames are piped directly into ffmpeg's stdin and never touch the disk.
 * Writing 1350 lossless 1080x1920 PNGs first costs ~1.8GB of scratch space,
 * which is what broke the earlier frame-based pipeline; this needs only the
 * ~20MB of the finished file.
 *
 * The browser is relaunched every CAPTURE_BATCH frames. ffmpeg's stdin stays
 * open across restarts, so the stream is unbroken.
 */
// paths.mjs must be imported before playwright: it sets
// PLAYWRIGHT_BROWSERS_PATH, which playwright reads when it is first loaded.
import { OUT_DIR } from './paths.mjs';
const { chromium } = await import('playwright');

import { serve } from './static-server.mjs';
import { spawn } from 'node:child_process';
import { mkdir, access } from 'node:fs/promises';
import path from 'node:path';

const OUT_FILE = path.join(OUT_DIR, 'micromouse-26-reveal.mp4');
const BATCH = Number(process.env.CAPTURE_BATCH ?? 250);
const DIST = path.resolve('dist');

// Serve the built bundle from an in-process static server rather than the Vite
// dev server, which died mid-render more than once and took the run with it.
// REVEAL_URL still overrides, for rendering against a live dev server.
let baseUrl = process.env.REVEAL_URL;
let staticServer = null;
if (!baseUrl) {
  await access(path.join(DIST, 'index.html')).catch(() => {
    console.error('No dist/ build found. Run `npm run build` first.');
    process.exit(1);
  });
  staticServer = await serve(DIST);
  baseUrl = `http://127.0.0.1:${staticServer.port}/?render=1`;
  console.log(`serving ${DIST} on port ${staticServer.port}`);
}
const URL = baseUrl;

async function resolveFfmpeg() {
  if (process.env.FFMPEG_PATH) return process.env.FFMPEG_PATH;
  try {
    const mod = await import('ffmpeg-static');
    if (mod.default) return mod.default;
  } catch {
    /* fall through to PATH */
  }
  return 'ffmpeg';
}

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

/** Writes to a stream, respecting backpressure. */
const write = (stream, buf) =>
  new Promise((resolve, reject) => {
    if (stream.write(buf)) return resolve();
    stream.once('drain', resolve);
    stream.once('error', reject);
  });

await mkdir(OUT_DIR, { recursive: true });

let { browser, page } = await openPage();
const { fps, totalFrames } = await page.evaluate(() => ({
  fps: window.__reveal.FPS,
  totalFrames: window.__reveal.TOTAL_FRAMES,
}));

const ffmpeg = await resolveFfmpeg();
const proc = spawn(
  ffmpeg,
  [
    '-y',
    '-f', 'image2pipe',
    '-framerate', String(fps),
    '-i', '-',
    '-c:v', 'libx264',
    '-preset', 'slow',
    '-crf', '17',
    '-pix_fmt', 'yuv420p',
    '-g', String(fps * 2),
    '-movflags', '+faststart',
    '-colorspace', 'bt709',
    '-color_primaries', 'bt709',
    '-color_trc', 'bt709',
    OUT_FILE,
  ],
  { stdio: ['pipe', 'ignore', 'pipe'] },
);

let ffmpegErr = '';
proc.stderr.on('data', (d) => (ffmpegErr += d.toString()));

const finished = new Promise((resolve, reject) => {
  proc.on('close', (code) =>
    code === 0 ? resolve() : reject(new Error(`ffmpeg exited ${code}\n${ffmpegErr.slice(-2000)}`)),
  );
});

console.log(`rendering ${totalFrames} frames @ ${fps}fps → ${OUT_FILE}`);
const started = Date.now();

try {
  for (let f = 0; f < totalFrames; f++) {
    if (f > 0 && f % BATCH === 0) {
      await browser.close();
      ({ browser, page } = await openPage());
    }

    let shot;
    for (let attempt = 0; attempt < 2; attempt++) {
      try {
        await page.evaluate((frame) => window.__reveal.seek(frame / window.__reveal.FPS), f);
        shot = await page.locator('#stage').screenshot();
        break;
      } catch (err) {
        if (attempt === 1) throw err;
        console.error(`\n[frame ${f}] ${err.message.split('\n')[0]} — restarting browser`);
        await browser.close().catch(() => {});
        ({ browser, page } = await openPage());
      }
    }

    await write(proc.stdin, shot);

    if (f % 60 === 0 || f === totalFrames - 1) {
      const elapsed = (Date.now() - started) / 1000;
      const rate = (f + 1) / Math.max(elapsed, 0.001);
      console.log(
        `  ${(((f + 1) / totalFrames) * 100).toFixed(1)}%  ${f + 1}/${totalFrames}  ` +
          `${elapsed.toFixed(0)}s elapsed  ~${((totalFrames - f - 1) / rate).toFixed(0)}s left`,
      );
    }
  }
} finally {
  proc.stdin.end();
  await browser.close().catch(() => {});
  await staticServer?.close();
}

await finished;
console.log(`\ndone: ${OUT_FILE}`);
