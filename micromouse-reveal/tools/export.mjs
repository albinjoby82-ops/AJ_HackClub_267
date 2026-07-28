/**
 * Encodes the captured frames to an Instagram-ready vertical MP4.
 *
 *   node tools/export.mjs
 *
 * Uses the ffmpeg binary from ffmpeg-static so the pipeline does not depend on
 * a system install. Set FFMPEG_PATH to override.
 */
import { spawn } from 'node:child_process';
import { mkdir, access } from 'node:fs/promises';
import path from 'node:path';

const FRAMES = path.resolve('out/frames');
const OUT_DIR = path.resolve('out');
const OUT_FILE = path.join(OUT_DIR, 'micromouse-26-reveal.mp4');
const FPS = 30;

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

await access(path.join(FRAMES, '00000.png')).catch(() => {
  console.error('No frames found. Run `npm run capture` first.');
  process.exit(1);
});

await mkdir(OUT_DIR, { recursive: true });
const ffmpeg = await resolveFfmpeg();

const args = [
  '-y',
  '-framerate', String(FPS),
  '-i', path.join(FRAMES, '%05d.png'),
  '-c:v', 'libx264',
  '-preset', 'slow',
  '-crf', '17',
  '-pix_fmt', 'yuv420p',
  // Instagram is happiest with closed GOPs and a web-friendly moov atom.
  '-g', String(FPS * 2),
  '-movflags', '+faststart',
  '-colorspace', 'bt709',
  '-color_primaries', 'bt709',
  '-color_trc', 'bt709',
  OUT_FILE,
];

console.log(`encoding → ${OUT_FILE}`);
const proc = spawn(ffmpeg, args, { stdio: ['ignore', 'inherit', 'inherit'] });

proc.on('close', (code) => {
  if (code === 0) console.log(`\ndone: ${OUT_FILE}`);
  else {
    console.error(`\nffmpeg exited with ${code}`);
    process.exit(code ?? 1);
  }
});
