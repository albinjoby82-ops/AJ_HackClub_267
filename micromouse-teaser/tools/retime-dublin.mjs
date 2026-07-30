/**
 * Retimer for the two sharp-turn shots. Cuts turn1.mp4 / turn2.mp4 into
 * public/dublin; `reshot` is the variant that ships.
 *
 * It builds a dense intermediate from the source window, then samples one
 * output frame per slot frame along an easing curve. Slot lengths (53 and 52
 * frames) are fixed by the 500-frame master, so music sync never moves.
 *
 * Why it exists — the turns read as rough for three separate reasons, and it
 * took all three fixes:
 *
 * 1. The ramps in prepare-dublin.mjs changed speed instantly at each segment
 *    boundary (turn 2 jumped 0.5x -> 1.5x on one frame) and used non-integer
 *    ratios, so frames were dropped on an uneven cadence. Hence the continuous
 *    easing curves below.
 *
 * 2. Turn 1's original window (5.85-7.05 s) straddled scene cuts at 5.90, 6.07
 *    and 6.80 s — three camera setups inside one 1.8 s shot. No retime removes
 *    a camera jump, so turn 1 was re-cut from 8.72-9.60 s, which is one
 *    continuous camera (there is no cut between 7.567 and 10.167 s) and clear
 *    of the burned-in "FASTER." title, which ends at 8.72 s.
 *
 * 3. Interpolation itself was the last artefact. See DENSE_FILTER: mci tears
 *    the flat vector geometry, and blend double-images the mouse. Turn 1 now
 *    runs at an exact 0.5x hold with no interpolation at all.
 *
 * Usage: node tools/retime-dublin.mjs [--variant=<name>] [--motion=<mode>]
 *                                     [--out=<dir>]
 *   --variant  reshot (shipped) | retime | single. See VARIANTS.
 *   --motion   dup | blend | mci — default for shots that do not set their own.
 *   --out      write the clips somewhere other than public/dublin, for
 *              building candidates side by side.
 */
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {probe, run} from './ffmpeg.mjs';

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, '..');
const SOURCE = path.join(root, 'dublin-src', 'source', 'current_mouse_animation.mp4');
const out = path.join(root, 'public', 'dublin');

const FPS = 30;
const WORK_FPS = 120;

/**
 * frames  — the slot each shot fills in the 500-frame master (never changes).
 * from/to — source window in seconds.
 * k       — easing depth, 0 = constant speed, 0.6 = apex runs at 0.4x the mean.
 * apex    — optional {p, w}: place the slow point at output progress p rather
 *           than the midpoint. See easePlaced.
 * motion  — optional per-shot override of --motion.
 *
 * retime and single are kept as the rejected steps on the way to reshot: the
 * first fixes only the motion, the second also trims to a single camera. Both
 * still ghost, because both still interpolate.
 */
const VARIANTS = {
  retime: {
    'turn1.mp4': {frames: 53, from: 5.85, to: 7.05, k: 0.55},
    'turn2.mp4': {frames: 52, from: 10.05, to: 11.65, k: 0.6},
  },
  single: {
    // 6.10-6.79 sits wholly inside the overhead corner shot (cuts at 6.067
    // and 6.80 are excluded), so 0.69 s stretches across 53 frames at ~0.39x.
    'turn1.mp4': {frames: 53, from: 6.1, to: 6.79, k: 0.5},
    // 10.18 starts just after the cut at 10.167, on the bank initiation.
    'turn2.mp4': {frames: 52, from: 10.18, to: 11.3, k: 0.6},
  },
  // Ships.
  reshot: {
    // Turn 1, glitch-free. Blending was the glitch: at any fractional speed a
    // source frame is cross-dissolved across several output frames, and on a
    // fast-rotating rigid body that reads as a double image, not motion blur.
    // Dropping to an exact 0.5x hold with no interpolation removes it outright
    // — every source frame shows for exactly two output frames, so the cadence
    // is perfectly even and nothing is ever mixed. 26.5 source frames
    // (8.72-9.60 s) fill the 53-frame slot, and there is no easing, so the turn
    // itself plays about 3x faster than the eased apex it replaces.
    'turn1.mp4': {frames: 53, from: 8.72, to: 9.6, k: 0, motion: 'dup'},
    // Turn 2 untouched — it never read as rough.
    'turn2.mp4': {frames: 52, from: 10.05, to: 11.65, k: 0.6},
  },
};

/**
 * How the dense intermediate is built.
 *
 * mci   true motion-compensated in-betweens. Rejected for these shots: the
 *       camera rolls fast over thin high-contrast wall edges on near-black,
 *       block matching fails and the flat vector geometry tears.
 * blend cross-dissolves neighbouring frames. No geometry is invented, so
 *       nothing can tear; in motion it reads as natural shutter blur.
 * dup   nearest source frame. Honest but steppy — this is what the original
 *       ramps did.
 */
const DENSE_FILTER = {
  mci: (fps) =>
    `minterpolate=fps=${fps}:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1`,
  blend: (fps) => `minterpolate=fps=${fps}:mi_mode=blend`,
  dup: (fps) => `fps=${fps}`,
};

/**
 * Symmetric ease — slow apex fixed at the midpoint of the shot.
 *   e(u) = u + k*sin(2*pi*u)/(2*pi)
 */
const easeCentred = (u, k) => u + (k * Math.sin(2 * Math.PI * u)) / (2 * Math.PI);

/**
 * Placed ease — a Gaussian dip in the speed profile, so the slowest moment can
 * be put wherever the turn actually happens rather than at the midpoint:
 *
 *   v(u) = 1 - k*exp(-((u-p)/w)^2)
 *
 * p is the apex position in output progress, w its width, k its depth. The
 * profile is integrated and normalised to the window, so it stays C1-continuous
 * (no instantaneous speed change) while the shot can open at full rate, drop
 * hard through the whip, and recover.
 */
const easePlaced = (u, {k, p, w}) => {
  const STEPS = 2000;
  const v = (x) => 1 - k * Math.exp(-(((x - p) / w) ** 2));
  let total = 0;
  let upto = 0;
  for (let i = 0; i < STEPS; i++) {
    const x = (i + 0.5) / STEPS;
    const dv = v(x) / STEPS;
    total += dv;
    if (x < u) upto += dv;
  }
  return upto / total;
};

const ease = (u, shot) =>
  shot.apex ? easePlaced(u, {k: shot.k, ...shot.apex}) : easeCentred(u, shot.k);

const main = async () => {
  const arg = process.argv.find((a) => a.startsWith('--variant='));
  const variant = arg ? arg.split('=')[1] : 'retime';
  const plan = VARIANTS[variant];
  if (!plan) throw new Error(`Unknown variant: ${variant}`);

  const motionArg = process.argv.find((a) => a.startsWith('--motion='));
  const motion = motionArg ? motionArg.split('=')[1] : 'blend';
  if (!DENSE_FILTER[motion]) throw new Error(`Unknown motion mode: ${motion}`);

  const destDirArg = process.argv.find((a) => a.startsWith('--out='));
  const destDir = destDirArg ? path.resolve(root, destDirArg.split('=')[1]) : out;

  const info = probe(SOURCE);
  if (info.width !== 1080 || info.height !== 1920 || info.fps !== 30) {
    throw new Error('Unexpected source geometry — retime assumes 1080x1920 @ 30fps');
  }
  fs.mkdirSync(destDir, {recursive: true});

  for (const [name, shot] of Object.entries(plan)) {
    const work = fs.mkdtempSync(path.join(root, 'output', `retime-${name}-`));
    const dense = path.join(work, 'dense');
    const picked = path.join(work, 'picked');
    fs.mkdirSync(dense);
    fs.mkdirSync(picked);

    // 1. motion-interpolated intermediate at 120 fps, one PNG per frame.
    //    A little head/tail padding keeps the interpolator from guessing at
    //    the window edges, and is trimmed away by the sampling step below.
    const pad = 0.1;
    const from = Math.max(0, shot.from - pad);
    const to = shot.to + pad;
    await run([
      '-y',
      '-ss', String(from),
      '-to', String(to),
      '-i', SOURCE,
      '-vf', DENSE_FILTER[shot.motion ?? motion](WORK_FPS),
      '-vsync', '0',
      path.join(dense, '%05d.png'),
    ]);

    const denseFrames = fs.readdirSync(dense).sort();
    const offset = (shot.from - from) * WORK_FPS; // window start within the pad

    // 2. sample the eased curve — one output frame per slot frame.
    const span = (shot.to - shot.from) * WORK_FPS;
    for (let i = 0; i < shot.frames; i++) {
      const u = shot.frames === 1 ? 0 : i / (shot.frames - 1);
      const idx = Math.min(
        denseFrames.length - 1,
        Math.max(0, Math.round(offset + span * ease(u, shot))),
      );
      fs.copyFileSync(
        path.join(dense, denseFrames[idx]),
        path.join(picked, `${String(i + 1).padStart(5, '0')}.png`),
      );
    }

    const dest = path.join(destDir, name);
    await run([
      '-y',
      '-framerate', String(FPS),
      '-i', path.join(picked, '%05d.png'),
      '-an',
      '-c:v', 'libx264',
      '-crf', '12',
      '-preset', 'medium',
      '-pix_fmt', 'yuv420p',
      dest,
    ]);

    fs.rmSync(work, {recursive: true, force: true});

    const clip = probe(dest);
    const mean = (shot.to - shot.from) / (shot.frames / FPS);
    console.log(
      `→ ${name} [${variant}/${shot.motion ?? motion}]: ${shot.from}-${shot.to}s over ${shot.frames} frames, ` +
        `mean ${mean.toFixed(3)}x (apex ${(mean * (1 - shot.k)).toFixed(3)}x, ` +
        `ends ${(mean * (1 + shot.k)).toFixed(3)}x), ` +
        `${clip.width}x${clip.height}, ${clip.durationInSeconds}s`,
    );
  }
};

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
