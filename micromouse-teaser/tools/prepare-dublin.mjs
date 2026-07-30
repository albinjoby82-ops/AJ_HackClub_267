/**
 * Media prep for the Dublin Micromouse Open teaser re-edit.
 *
 * Cuts the two sharp-turn shots out of dublin-src/source/current_mouse_animation.mp4
 * at true 1.0x — no speed ramp, no retiming. Every output frame is a distinct
 * source frame, so the motion is exactly as smooth as the original render.
 * Each range is sized in whole frames to fill its slot in the 500-frame master
 * timeline. Also stages the two posters into public/dublin.
 *
 * The source has burned-in titles at frames 223-256 ("FASTER.") and 317-347
 * ("SMARTER."), measured from the luma of the title band. Turn 1 ends at 222,
 * before the first. Turn 2 overlaps the second, which the composition removes
 * with a bottom-anchored crop — the text sits entirely above the crop window.
 *
 * Turn 1 — source frames 170-222 (5.667-7.433 s), overhead corner snap, 53 out.
 * Turn 2 — source frames 298-349 (9.933-11.633 s), banked low angle,  52 out.
 */
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {probe, run} from './ffmpeg.mjs';

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, '..');
const src = path.join(root, 'dublin-src');
const out = path.join(root, 'public', 'dublin');

const SOURCE = path.join(src, 'source', 'current_mouse_animation.mp4');

/** Frame-exact, 1:1 source-to-output. `end` is exclusive. */
const CLIPS = {
  'turn1.mp4': {start: 170, end: 223},
  'turn2.mp4': {start: 298, end: 350},
};

const main = async () => {
  fs.mkdirSync(out, {recursive: true});

  for (const poster of ['01_something_is_learning_the_maze.png', '02_it_knows_the_way_out.png']) {
    const from = path.join(src, 'posters', poster);
    const to = path.join(out, poster.startsWith('01') ? 'poster1.png' : 'poster2.png');
    fs.copyFileSync(from, to);
  }

  const info = probe(SOURCE);
  console.log(`source: ${info.width}x${info.height} @ ${info.fps} fps, ${info.durationInSeconds}s`);
  if (info.width !== 1080 || info.height !== 1920 || info.fps !== 30) {
    throw new Error('Unexpected source geometry — frame ranges assume 1080x1920 @ 30fps');
  }

  for (const [name, clip] of Object.entries(CLIPS)) {
    const dest = path.join(out, name);
    const frames = clip.end - clip.start;
    await run([
      '-y',
      '-i', SOURCE,
      // trim by frame number, then rebase the timestamps to a clean 30 fps
      // grid. No setpts scaling, so no frame is dropped or repeated.
      '-vf', `trim=start_frame=${clip.start}:end_frame=${clip.end},setpts=N/(30*TB)`,
      '-an',
      '-c:v', 'libx264',
      '-crf', '12',
      '-preset', 'medium',
      '-pix_fmt', 'yuv420p',
      '-r', '30',
      dest,
    ]);
    const out2 = probe(dest);
    console.log(
      `→ ${name}: source ${clip.start}-${clip.end - 1} (${frames} frames), ` +
        `${out2.width}x${out2.height}, ${out2.durationInSeconds}s`,
    );
  }
};

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
