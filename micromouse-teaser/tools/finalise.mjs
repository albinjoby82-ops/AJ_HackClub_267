/**
 * Delivery encode.
 *
 * Remotion renders a muted H.264 High/yuv420p master. This step copies that
 * video stream untouched — so there is no second generation of lossy video —
 * and muxes the score in as a single AAC encode straight from the 24-bit WAV.
 * Encoding the audio only once is what keeps the true peak predictable.
 *
 * Usage: node tools/finalise.mjs <master.mp4> <output.mp4>
 */
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {probe, run} from './ffmpeg.mjs';
import {ASSETS, AUDIO} from '../src/timeline.mjs';

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, '..');

const [master, out] = process.argv.slice(2);
if (!master || !out) {
  console.error('Usage: node tools/finalise.mjs <master.mp4> <output.mp4>');
  process.exit(1);
}

const score = path.join(root, 'public', ASSETS.score);

const main = async () => {
  if (!fs.existsSync(master)) throw new Error(`Missing master: ${master}`);
  if (!fs.existsSync(score)) throw new Error(`Missing score: ${score}. Run npm run audio.`);

  await run([
    '-y',
    '-i', master,
    '-i', score,
    '-map', '0:v:0',
    '-map', '1:a:0',
    '-c:v', 'copy',
    '-c:a', 'aac',
    '-profile:a', 'aac_low',
    '-b:a', '192k',
    '-ar', String(AUDIO.sampleRate),
    '-ac', '2',
    // Trim the audio to the video length rather than the other way round.
    '-shortest',
    '-movflags', '+faststart',
    out,
  ]);

  const info = probe(out);
  console.log(
    `→ ${path.relative(root, out)}: ${info.width}x${info.height}, ${info.fps} fps, ` +
      `${info.durationInSeconds?.toFixed(2)} s, ${info.codec}/${info.audioCodec} ` +
      `${info.sampleRate} Hz, ${info.pixelFormat}`,
  );
};

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
