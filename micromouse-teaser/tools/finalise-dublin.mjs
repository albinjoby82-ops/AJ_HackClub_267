/**
 * Delivery mux for the Dublin teaser.
 *
 * The supplied soundtrack (dublin-src/audio/reference_music_trimmed.m4a) is
 * already the exact production audio — AAC-LC 44.1 kHz. It is stream-copied,
 * never re-encoded, so the musical timing and levels are untouched from
 * frame one. The Remotion master's video stream is likewise copied.
 *
 * Usage: node tools/finalise-dublin.mjs <master.mp4> <output.mp4>
 */
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {probe, run} from './ffmpeg.mjs';

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, '..');

const [master, out] = process.argv.slice(2);
if (!master || !out) {
  console.error('Usage: node tools/finalise-dublin.mjs <master.mp4> <output.mp4>');
  process.exit(1);
}

const music = path.join(root, 'dublin-src', 'audio', 'reference_music_trimmed.m4a');

const main = async () => {
  if (!fs.existsSync(master)) throw new Error(`Missing master: ${master}`);
  if (!fs.existsSync(music)) throw new Error(`Missing music: ${music}`);

  await run([
    '-y',
    '-i', master,
    '-i', music,
    '-map', '0:v:0',
    '-map', '1:a:0',
    '-c:v', 'copy',
    '-c:a', 'copy',
    '-movflags', '+faststart',
    out,
  ]);

  const info = probe(out);
  console.log(
    `→ ${out}: ${info.width}x${info.height}, ${info.fps} fps, ` +
      `${info.durationInSeconds?.toFixed(3)} s, ${info.codec}/${info.audioCodec} ` +
      `${info.sampleRate} Hz, ${info.pixelFormat}`,
  );
};

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
