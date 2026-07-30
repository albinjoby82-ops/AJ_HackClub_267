/**
 * Automated checks for the Dublin teaser delivery.
 *
 * Usage: node tools/validate-dublin.mjs <final.mp4>
 */
import {spawnSync} from 'node:child_process';
import {probe, FFMPEG} from './ffmpeg.mjs';

const [file] = process.argv.slice(2);
if (!file) {
  console.error('Usage: node tools/validate-dublin.mjs <final.mp4>');
  process.exit(1);
}

const countFrames = (f) => {
  const result = spawnSync(
    FFMPEG,
    ['-hide_banner', '-i', f, '-map', '0:v:0', '-f', 'null', '-'],
    {encoding: 'utf8', maxBuffer: 1024 * 1024 * 64},
  );
  // ffmpeg writes progress lines; the last "frame= N" is the decoded count.
  const matches = [...String(result.stderr ?? '').matchAll(/frame=\s*(\d+)/g)];
  return matches.length ? Number(matches[matches.length - 1][1]) : null;
};

const info = probe(file);
const frames = countFrames(file);

const checks = [
  ['resolution 1080x1920', info.width === 1080 && info.height === 1920],
  ['30 fps constant', info.fps === 30],
  ['exactly 500 video frames', frames === 500],
  ['video duration 16.667 s (500/30)', frames === 500 && info.fps === 30],
  ['H.264 video', info.codec === 'h264'],
  ['yuv420p pixel format', info.pixelFormat?.startsWith('yuv420p')],
  ['AAC audio present', info.audioCodec === 'aac'],
  ['44.1 kHz stereo', info.sampleRate === 44100 && info.channels === 'stereo'],
  ['container duration ≈ 16.67 s', Math.abs((info.durationInSeconds ?? 0) - 16.667) < 0.05],
];

let failed = 0;
for (const [name, ok] of checks) {
  console.log(`${ok ? 'PASS' : 'FAIL'}  ${name}`);
  if (!ok) failed++;
}
console.log(`\nvideo frames decoded: ${frames}; container: ${info.durationInSeconds}s`);
process.exit(failed ? 1 : 0);
