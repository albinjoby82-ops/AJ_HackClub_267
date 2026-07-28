import {execFile, execFileSync} from 'node:child_process';
import {promisify} from 'node:util';
import {createRequire} from 'node:module';

const require = createRequire(import.meta.url);
const execFileAsync = promisify(execFile);

export const FFMPEG = require('ffmpeg-static');

export const run = async (args, {quiet = true} = {}) => {
  try {
    const {stderr} = await execFileAsync(FFMPEG, args, {
      maxBuffer: 1024 * 1024 * 64,
    });
    return stderr;
  } catch (error) {
    if (!quiet) console.error(error.stderr ?? error.message);
    throw error;
  }
};

/**
 * ffmpeg-static ships ffmpeg only, so metadata is read by parsing the banner
 * that `ffmpeg -i` writes to stderr.
 */
export const probe = (file) => {
  let stderr = '';
  try {
    execFileSync(FFMPEG, ['-hide_banner', '-i', file], {
      stdio: ['ignore', 'ignore', 'pipe'],
    });
  } catch (error) {
    stderr = String(error.stderr ?? '');
  }

  const video = stderr.match(
    /Stream #\d+:\d+.*?: Video: (\w+).*?, (\w+)\(?.*?\)?, (\d+)x(\d+).*?, ([\d.]+) fps/,
  );
  const audio = stderr.match(
    /Stream #\d+:\d+.*?: Audio: (\w+).*?, (\d+) Hz, (\w+)/,
  );
  const duration = stderr.match(/Duration: (\d+):(\d+):([\d.]+)/);

  return {
    exists: Boolean(video),
    codec: video?.[1] ?? null,
    pixelFormat: video?.[2] ?? null,
    width: video ? Number(video[3]) : null,
    height: video ? Number(video[4]) : null,
    fps: video ? Number(video[5]) : null,
    audioCodec: audio?.[1] ?? null,
    sampleRate: audio ? Number(audio[2]) : null,
    channels: audio?.[3] ?? null,
    durationInSeconds: duration
      ? Number(duration[1]) * 3600 + Number(duration[2]) * 60 + Number(duration[3])
      : null,
    raw: stderr,
  };
};
