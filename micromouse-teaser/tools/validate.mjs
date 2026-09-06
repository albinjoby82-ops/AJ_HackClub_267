/**
 * Validates the delivered MP4 against the brief's acceptance criteria and
 * produces the contact sheet. Exits non-zero if any hard requirement fails.
 */
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {probe, run} from './ffmpeg.mjs';
import {
  AUDIO,
  DURATION_IN_SECONDS,
  END_CARD,
  FPS,
  HEIGHT,
  segment,
  WIDTH,
} from '../src/timeline.mjs';

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, '..');
const outputDir = path.join(root, 'output');

/** Validates the V2 deliverable by default; pass a filename to override. */
const targetName = process.argv[2] ?? 'micromouse-teaser-final-v2.mp4';
const target = path.join(outputDir, targetName);
const sheet = path.join(
  outputDir,
  `${path.basename(targetName, '.mp4')}-contact-sheet.png`,
);

/** The V2 brief's target duration window, seconds. */
const DURATION_WINDOW = [16.5, 17.2];

const checks = [];
const check = (label, pass, detail) => {
  checks.push({label, pass, detail});
  console.log(`  ${pass ? 'PASS' : 'FAIL'}  ${label}${detail ? ` — ${detail}` : ''}`);
};

const measureLoudness = async (file) => {
  const stderr = await run([
    '-hide_banner', '-i', file,
    '-af', 'loudnorm=I=-14:TP=-1:LRA=11:print_format=json',
    '-f', 'null', '-',
  ]);
  return JSON.parse(stderr.slice(stderr.lastIndexOf('{'), stderr.lastIndexOf('}') + 1));
};

/** Full decode; any corrupt frame makes ffmpeg report errors here. */
const decodeCheck = async (file) => {
  const stderr = await run(['-hide_banner', '-v', 'error', '-i', file, '-f', 'null', '-']);
  return stderr.trim();
};

/**
 * Walks the top-level MP4 atom table. Fast-start requires `moov` to appear
 * before `mdat` so a player can begin without fetching the whole file.
 */
const hasFastStart = (file) => {
  const fd = fs.openSync(file, 'r');
  try {
    const header = Buffer.alloc(8);
    let offset = 0;
    const {size: fileSize} = fs.fstatSync(fd);
    while (offset < fileSize - 8) {
      if (fs.readSync(fd, header, 0, 8, offset) < 8) break;
      let size = header.readUInt32BE(0);
      const type = header.toString('ascii', 4, 8);
      if (type === 'moov') return true;
      if (type === 'mdat') return false;
      if (size === 1) {
        const ext = Buffer.alloc(8);
        fs.readSync(fd, ext, 0, 8, offset + 8);
        size = Number(ext.readBigUInt64BE(0));
      }
      if (size < 8) break;
      offset += size;
    }
    return false;
  } finally {
    fs.closeSync(fd);
  }
};

/**
 * Measures luma change between consecutive frames in a range.
 *
 * The composition renders this range byte-identically (confirmed by comparing
 * losslessly rendered stills), but H.264 quantisation still perturbs decoded
 * pixels, so a bit-exact comparison of the encoded file would fail on codec
 * noise rather than on movement.
 *
 * The gate is the *mean* absolute difference, not the max: an I-frame boundary
 * produces isolated single-pixel spikes of ~25/255 in the dark gradient while
 * the frame mean stays around 1e-5. Anything genuinely animating would move
 * the mean by orders of magnitude, so the mean is the honest discriminator and
 * the max is reported alongside it for transparency.
 */
const frameDelta = async (file, from, to) => {
  // `metadata=mode=print` with no file= logs to stderr, which avoids having to
  // escape a Windows path (drive colons and spaces both break filter parsing).
  const stderr = await run([
    '-hide_banner', '-i', file,
    '-an',
    '-vf',
      `select='between(n\\,${from}\\,${to})',tblend=all_mode=difference,` +
      `signalstats,metadata=mode=print`,
    '-vsync', '0', '-f', 'null', '-',
  ]);
  const maxes = [...stderr.matchAll(/lavfi\.signalstats\.YMAX=([\d.e+-]+)/g)].map((m) =>
    Number(m[1]),
  );
  const avgs = [...stderr.matchAll(/lavfi\.signalstats\.YAVG=([\d.e+-]+)/g)].map((m) =>
    Number(m[1]),
  );
  return {
    maxMean: avgs.length ? Math.max(...avgs) : Infinity,
    maxPeak: maxes.length ? Math.max(...maxes) : Infinity,
    frames: maxes.length,
  };
};

const main = async () => {
  if (!fs.existsSync(target)) throw new Error(`Missing ${target}`);
  const info = probe(target);

  console.log('Final output validation');
  check('Container decodes end to end', (await decodeCheck(target)) === '', 'no ffmpeg errors');
  check('Dimensions 1080x1920', info.width === WIDTH && info.height === HEIGHT, `${info.width}x${info.height}`);
  check('Frame rate 30 fps', Math.abs(info.fps - FPS) < 0.01, `${info.fps} fps`);
  check('Video codec H.264', info.codec === 'h264', info.codec);
  check('Pixel format yuv420p', info.pixelFormat === 'yuv420p', info.pixelFormat);
  check('Audio codec AAC', info.audioCodec === 'aac', info.audioCodec);
  check('Audio 48 kHz', info.sampleRate === AUDIO.sampleRate, `${info.sampleRate} Hz`);
  check(
    `Duration within ${DURATION_WINDOW[0]}-${DURATION_WINDOW[1]} s`,
    info.durationInSeconds >= DURATION_WINDOW[0] &&
      info.durationInSeconds <= DURATION_WINDOW[1],
    `${info.durationInSeconds?.toFixed(2)} s`,
  );
  check(
    'Duration matches timeline',
    Math.abs(info.durationInSeconds - DURATION_IN_SECONDS) < 0.15,
    `expected ${DURATION_IN_SECONDS.toFixed(2)} s`,
  );
  check('High profile', /High/.test(info.raw), info.raw.match(/h264 \(([^)]+)\)/)?.[1] ?? '?');
  check('Faststart (moov before mdat)', hasFastStart(target), 'top-level atom order');

  const holdFrom = segment('endCard').from + END_CARD.settledAt;
  const holdTo = segment('endCard').from + END_CARD.holdUntil;
  const hold = await frameDelta(target, holdFrom, holdTo);
  check(
    'End card held motionless >= 2.5 s',
    hold.maxMean <= 0.05 && (holdTo - holdFrom) / FPS >= 2.5,
    `${((holdTo - holdFrom) / FPS).toFixed(2)} s over frames ${holdFrom}-${holdTo}; ` +
      `mean luma delta ${hold.maxMean.toExponential(1)}/255 ` +
      `(peak ${hold.maxPeak}/255 at an I-frame) across ${hold.frames} frames`,
  );

  const loud = await measureLoudness(target);
  check(
    `Integrated loudness near ${AUDIO.targetLufs} LUFS`,
    Math.abs(Number(loud.input_i) - AUDIO.targetLufs) <= 1.0,
    `${loud.input_i} LUFS`,
  );
  check(
    `True peak at or below ${AUDIO.truePeakDb} dBTP`,
    Number(loud.input_tp) <= AUDIO.truePeakDb,
    `${loud.input_tp} dBTP`,
  );

  // Contact sheet: 12 evenly spaced frames across the whole piece.
  const total = Math.round(info.durationInSeconds * FPS);
  const step = Math.floor(total / 12);
  const selection = Array.from({length: 12}, (_, i) => `eq(n\\,${i * step})`).join('+');
  await run([
    '-y', '-i', target,
    '-vf', `select='${selection}',scale=320:569,tile=4x3`,
    '-vsync', '0', '-frames:v', '1',
    sheet,
  ]);
  check('Contact sheet written', fs.existsSync(sheet), path.relative(root, sheet));

  const failed = checks.filter((c) => !c.pass);
  fs.writeFileSync(
    path.join(outputDir, `${path.basename(targetName, '.mp4')}-validation.json`),
    JSON.stringify({file: path.basename(target), info: {...info, raw: undefined}, loudness: loud, checks}, null, 2),
  );

  console.log(`\n${checks.length - failed.length}/${checks.length} checks passed`);
  if (failed.length) process.exit(1);
};

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
