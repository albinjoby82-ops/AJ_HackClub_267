/**
 * Inventories the supplied media, identifies the clean animation vs the
 * watermarked pacing reference *by content* rather than by filename, and
 * produces the assets the Remotion composition consumes.
 *
 * Only the primary animation is ever written into public/. The pacing
 * reference is deliberately never copied, scaled or composited.
 */
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {probe, run} from './ffmpeg.mjs';
import {HEIGHT, WIDTH} from '../src/timeline.mjs';

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, '..');
const publicDir = path.join(root, 'public');

const SEARCH_DIRS = [
  path.join(root, 'source'),
  root,
  'D:/Downloads',
  path.join(process.env.USERPROFILE ?? '', 'Downloads'),
];

const LOGO_CANDIDATES = [
  path.resolve(root, '../micromouse-reveal/public/assets/logos/elesoc_logo.png'),
  path.join(root, 'source/elecsoc-logo.png'),
];

const FONT_CANDIDATES = [
  'C:/Windows/Fonts/bahnschrift.ttf',
  'C:/Windows/Fonts/ARIALNB.TTF',
  'C:/Windows/Fonts/segoeuib.ttf',
];

/**
 * The clean animation is 478x850 @ 30 fps / ~20.3 s; the TikTok pacing
 * reference is 576x1090 @ 30 fps / ~21.1 s. Resolution alone is not enough —
 * unrelated phone clips in the same folder share the 478x850 frame size — so
 * frame rate and duration are part of the fingerprint.
 */
const near = (value, target, tolerance) =>
  value !== null && Math.abs(value - target) <= tolerance;

const isPrimary = (info) =>
  info.width === 478 &&
  info.height === 850 &&
  near(info.fps, 30, 1) &&
  near(info.durationInSeconds, 20.3, 1.5);

const isReference = (info) =>
  info.width === 576 &&
  info.height === 1090 &&
  near(info.fps, 30, 1) &&
  near(info.durationInSeconds, 21.1, 1.5);

const findSources = () => {
  const seen = new Set();
  const found = {primary: null, reference: null, inventory: []};

  for (const dir of SEARCH_DIRS) {
    if (!dir || !fs.existsSync(dir)) continue;
    for (const name of fs.readdirSync(dir)) {
      if (!name.toLowerCase().endsWith('.mp4')) continue;
      const full = path.join(dir, name);
      if (seen.has(full)) continue;
      seen.add(full);

      const info = probe(full);
      if (!info.exists) continue;

      if (isPrimary(info) && !found.primary) {
        found.primary = full;
        found.inventory.push({role: 'primary', file: full, ...info, raw: undefined});
      } else if (isReference(info) && !found.reference) {
        found.reference = full;
        found.inventory.push({
          role: 'pacing-reference (never rendered)',
          file: full,
          ...info,
          raw: undefined,
        });
      }
    }
    if (found.primary && found.reference) break;
  }

  return found;
};

const copyFirst = (candidates, dest, label) => {
  const hit = candidates.find((p) => fs.existsSync(p));
  if (!hit) throw new Error(`Could not locate ${label}. Tried:\n${candidates.join('\n')}`);
  fs.mkdirSync(path.dirname(dest), {recursive: true});
  fs.copyFileSync(hit, dest);
  console.log(`  ${label}: ${hit}`);
  return hit;
};

const main = async () => {
  fs.mkdirSync(publicDir, {recursive: true});

  console.log('Inventory');
  const {primary, reference, inventory} = findSources();
  for (const item of inventory) {
    console.log(
      `  [${item.role}] ${path.basename(item.file)} — ${item.width}x${item.height}, ` +
        `${item.fps} fps, ${item.durationInSeconds?.toFixed(2)} s, ${item.codec}/${item.audioCodec}`,
    );
  }
  if (!primary) throw new Error('Primary animation (478x850) not found.');
  if (!reference) console.log('  [note] pacing reference not found — not required for the render');

  console.log('\nAssets');
  copyFirst(LOGO_CANDIDATES, path.join(publicDir, 'elecsoc-logo.png'), 'ElecSoc logo');
  copyFirst(
    FONT_CANDIDATES,
    path.join(publicDir, 'fonts/bahnschrift.ttf'),
    'Condensed font',
  );

  // 478x850 and 1080x1920 differ in aspect by 0.03%, so a straight Lanczos
  // resize fills the frame with no crop, no padding and no visible distortion.
  const out = path.join(publicDir, 'primary-1080.mp4');
  console.log('\nUpscaling primary footage (Lanczos + mild sharpen)…');
  await run([
    '-y',
    '-i', primary,
    '-an',
    '-vf', `scale=${WIDTH}:${HEIGHT}:flags=lanczos,unsharp=5:5:0.45:5:5:0.0,format=yuv420p`,
    '-r', '30',
    '-c:v', 'libx264',
    '-preset', 'medium',
    '-crf', '12',
    '-pix_fmt', 'yuv420p',
    out,
  ]);

  const result = probe(out);
  console.log(
    `  → ${path.relative(root, out)} — ${result.width}x${result.height}, ` +
      `${result.fps} fps, ${result.durationInSeconds?.toFixed(2)} s`,
  );

  fs.writeFileSync(
    path.join(root, 'output', 'source-inventory.json'),
    JSON.stringify({inventory, upscaled: {file: 'public/primary-1080.mp4', ...result, raw: undefined}}, null, 2),
  );
};

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
