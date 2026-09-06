/**
 * Original score for the Micro-Mouse '26 teaser.
 *
 * Everything here is synthesised from scratch — no sampled, licensed or
 * third-party audio is used, and the pacing reference's music is never touched.
 * All randomness is seeded, so repeated runs are byte-identical.
 *
 * Output: public/score.wav, loudness-normalised to the targets in timeline.mjs.
 */
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {run} from './ffmpeg.mjs';
import {AUDIO, DURATION_IN_SECONDS} from '../src/timeline.mjs';

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, '..');
const publicDir = path.join(root, 'public');

const SR = AUDIO.sampleRate;
const N = Math.ceil(DURATION_IN_SECONDS * SR);
const left = new Float32Array(N);
const right = new Float32Array(N);

/** Deterministic PRNG so the score never changes between runs. */
const mulberry32 = (seed) => () => {
  seed |= 0;
  seed = (seed + 0x6d2b79f5) | 0;
  let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
  t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
  return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
};
const rand = mulberry32(20260728);

const clamp01 = (v) => Math.max(0, Math.min(1, v));
const expDecay = (p, k = 5) => Math.exp(-k * p);
/** Short fade at both ends of a grain to avoid clicks. */
const edge = (p, w = 0.02) =>
  Math.min(1, p / w) * Math.min(1, (1 - p) / w);

const write = (i, l, r) => {
  if (i < 0 || i >= N) return;
  left[i] += l;
  right[i] += r;
};

/** Adds a tone whose frequency and amplitude are functions of progress 0..1. */
const tone = (t0, dur, freqFn, ampFn, {pan = 0, phase = 0} = {}) => {
  const start = Math.floor(t0 * SR);
  const len = Math.floor(dur * SR);
  let ph = phase;
  const gl = Math.cos(((pan + 1) * Math.PI) / 4);
  const gr = Math.sin(((pan + 1) * Math.PI) / 4);
  for (let i = 0; i < len; i++) {
    const p = i / len;
    const f = freqFn(p);
    ph += (2 * Math.PI * f) / SR;
    const s = Math.sin(ph) * ampFn(p) * edge(p);
    write(start + i, s * gl, s * gr);
  }
};

/**
 * Filtered noise grain. `tilt` above 0.5 leans bright (high-passed), below
 * leans dark (low-passed) — enough shaping for air, clicks and risers.
 */
const noise = (t0, dur, ampFn, {tilt = 0.5, pan = 0, cutoffFn} = {}) => {
  const start = Math.floor(t0 * SR);
  const len = Math.floor(dur * SR);
  const gl = Math.cos(((pan + 1) * Math.PI) / 4);
  const gr = Math.sin(((pan + 1) * Math.PI) / 4);
  let lp = 0;
  let prev = 0;
  for (let i = 0; i < len; i++) {
    const p = i / len;
    const white = rand() * 2 - 1;
    const cutoff = cutoffFn ? cutoffFn(p) : 2000;
    const a = 1 - Math.exp((-2 * Math.PI * cutoff) / SR);
    lp += a * (white - lp);
    const hp = white - lp;
    const s = (tilt >= 0.5 ? hp : lp) * ampFn(p) * edge(p);
    // Slight decorrelation gives the bed a little width without phase issues.
    const w = 0.12;
    write(start + i, s * gl, (s * (1 - w) + prev * w) * gr);
    prev = s;
  }
};

const cues = AUDIO.cues;

// ---------------------------------------------------------------------------
// 1. Low electrical ambience — present from the first frame, slowly swelling.
// ---------------------------------------------------------------------------
const ambienceEnd = cues.fadeStart;
tone(0, ambienceEnd, () => 55, (p) => 0.055 * clamp01(p * 6) * (1 - 0.25 * p), {pan: -0.25});
tone(0, ambienceEnd, () => 82.5, (p) => 0.032 * clamp01(p * 5), {pan: 0.25});
tone(0, ambienceEnd, () => 110.2, (p) => 0.016 * clamp01(p * 4), {pan: 0.1});
noise(0, ambienceEnd, (p) => 0.011 * clamp01(p * 5), {
  tilt: 0.2,
  cutoffFn: (p) => 240 + 500 * p,
});

// A faint mains-style hum keeps the "powered equipment in the dark" feel.
tone(0, cues.chaseStart, () => 100, (p) => 0.012 * clamp01(p * 3), {pan: -0.4});

// ---------------------------------------------------------------------------
// 2. Power-on swell as the sensor beams ignite.
// ---------------------------------------------------------------------------
tone(cues.powerOn, 1.1, (p) => 38 + 150 * p * p, (p) => 0.16 * Math.sin(Math.PI * p));
noise(cues.powerOn, 1.0, (p) => 0.05 * Math.sin(Math.PI * p) ** 2, {
  tilt: 0.8,
  cutoffFn: (p) => 600 + 5200 * p,
});

// ---------------------------------------------------------------------------
// 3. Single sensor ping, with two quiet reflections.
// ---------------------------------------------------------------------------
const ping = (t, amp, freq) => {
  tone(t, 0.42, () => freq, (p) => amp * expDecay(p, 7));
  tone(t, 0.42, () => freq * 1.5, (p) => amp * 0.35 * expDecay(p, 9));
};
ping(cues.sensorPing, 0.13, 2350);
ping(cues.sensorPing + 0.19, 0.05, 2350);
ping(cues.sensorPing + 0.35, 0.02, 2350);

// ---------------------------------------------------------------------------
// 4. Servo / motor clicks on the activation details.
// ---------------------------------------------------------------------------
const servoClick = (t, amp = 0.09, pan = 0) => {
  noise(t, 0.045, (p) => amp * expDecay(p, 16), {
    tilt: 0.9,
    pan,
    cutoffFn: () => 3200,
  });
  tone(t, 0.06, (p) => 700 - 240 * p, (p) => amp * 0.5 * expDecay(p, 14), {pan});
};
for (const [i, t] of cues.servoClicks.entries()) {
  servoClick(t, 0.1, i % 2 === 0 ? -0.3 : 0.3);
  servoClick(t + 0.075, 0.05, i % 2 === 0 ? 0.2 : -0.2);
}

// ---------------------------------------------------------------------------
// 5. Rhythmic pulse through the chase, tightening as the edit accelerates.
// ---------------------------------------------------------------------------
const pulseThump = (t, amp) => {
  tone(t, 0.3, (p) => 62 - 18 * p, (p) => amp * expDecay(p, 8));
  noise(t, 0.07, (p) => amp * 0.28 * expDecay(p, 14), {
    tilt: 0.3,
    cutoffFn: () => 900,
  });
};

{
  let t = cues.pulseStart;
  const rampFrom = cues.pulseStart;
  const rampTo = cues.riserStart;
  // The pulse drives all the way to the direct cut, tightening as it goes.
  while (t < cues.revealHit) {
    const p = clamp01((t - rampFrom) / (rampTo - rampFrom));
    const interval = 0.50 - 0.26 * p;
    const amp = 0.10 + 0.10 * p;
    pulseThump(t, amp);
    t += interval;
  }
}

// Sparse motor ticks once the chase is running.
{
  let t = cues.chaseStart + 0.14;
  while (t < cues.riserStart) {
    servoClick(t, 0.035, rand() * 1.6 - 0.8);
    t += 0.24 + rand() * 0.2;
  }
}

// ---------------------------------------------------------------------------
// 6. One cinematic impact per word — V2 has two: FASTER. and SMARTER.
//    The SMALLER. beat is gone with its word; the cue sheet drives the count.
// ---------------------------------------------------------------------------
const impact = (t, base, bright) => {
  // Short anticipation swell before the hit.
  noise(t - 0.26, 0.26, (p) => 0.05 * p * p, {
    tilt: 0.8,
    cutoffFn: (p) => 1200 + 5000 * p,
  });
  // The hit itself: a fast pitch drop with a noise transient on top.
  tone(t, 0.85, (p) => base * Math.exp(-2.6 * p) + 42, (p) => 0.30 * expDecay(p, 4.2));
  tone(t, 0.5, (p) => base * 1.5 * Math.exp(-3.4 * p) + 60, (p) => 0.10 * expDecay(p, 7));
  noise(t, 0.2, (p) => 0.085 * bright * expDecay(p, 11), {
    tilt: 0.8,
    cutoffFn: (p) => 5200 - 3000 * p,
  });
  // Sub tail.
  tone(t + 0.01, 1.0, () => 44, (p) => 0.13 * expDecay(p, 3.4));
};
{
  const bases = [142, 152];
  const brights = [1.0, 1.15];
  cues.impacts.forEach((t, i) => impact(t, bases[i] ?? 152, brights[i] ?? 1.15));
}

// ---------------------------------------------------------------------------
// 7. Controlled rise into the reveal.
// ---------------------------------------------------------------------------
{
  const dur = cues.revealHit - cues.riserStart;
  noise(cues.riserStart, dur, (p) => 0.075 * p ** 2.1, {
    tilt: 0.8,
    cutoffFn: (p) => 700 + 7200 * p ** 2,
  });
  tone(cues.riserStart, dur, (p) => 90 + 520 * p ** 2.4, (p) => 0.055 * p ** 2);
  tone(cues.riserStart, dur, (p) => 45 + 60 * p, (p) => 0.07 * p ** 1.5);
}

// ---------------------------------------------------------------------------
// 8. The reveal hit — the strongest impact in the piece, landing exactly on
//    the direct cut to the announcement — then a sustained low tail that
//    carries the motionless card through to the fade.
// ---------------------------------------------------------------------------
tone(cues.revealHit, 2.6, (p) => 120 * Math.exp(-3.2 * p) + 41, (p) => 0.38 * expDecay(p, 1.9));
tone(cues.revealHit, 0.6, (p) => 190 * Math.exp(-4.0 * p) + 60, (p) => 0.12 * expDecay(p, 6));
noise(cues.revealHit, 0.5, (p) => 0.07 * expDecay(p, 6), {
  tilt: 0.8,
  cutoffFn: (p) => 6000 - 4000 * p,
});
// Sustained bed under the announcement: a slow 55/41 Hz pair decaying gently
// into the master fade rather than dying early.
tone(cues.revealHit, 4.0, () => 55, (p) => 0.10 * expDecay(p, 0.9), {pan: 0.25});
tone(cues.revealHit + 0.02, 4.0, () => 41.2, (p) => 0.09 * expDecay(p, 0.8), {pan: -0.25});

// ---------------------------------------------------------------------------
// 9. Master shaping: fade to silence over the fade to black, then normalise.
// ---------------------------------------------------------------------------
const fadeStartSample = Math.floor(cues.fadeStart * SR);
for (let i = fadeStartSample; i < N; i++) {
  const p = (i - fadeStartSample) / (N - fadeStartSample);
  const g = Math.cos((Math.PI * p) / 2) ** 1.6;
  left[i] *= g;
  right[i] *= g;
}
// Guard the very first samples against a click.
for (let i = 0; i < 480; i++) {
  const g = i / 480;
  left[i] *= g;
  right[i] *= g;
}

// Soft-clip anything that overshoots, then scale to a safe pre-normalise peak.
let peak = 0;
for (let i = 0; i < N; i++) {
  left[i] = Math.tanh(left[i] * 1.05);
  right[i] = Math.tanh(right[i] * 1.05);
  peak = Math.max(peak, Math.abs(left[i]), Math.abs(right[i]));
}
const gain = peak > 0 ? 0.89 / peak : 1;
for (let i = 0; i < N; i++) {
  left[i] *= gain;
  right[i] *= gain;
}

// ---------------------------------------------------------------------------
// WAV output (32-bit float, stereo) then two-pass loudness normalisation.
// ---------------------------------------------------------------------------
const writeWav = (file) => {
  const bytesPerSample = 4;
  const dataSize = N * 2 * bytesPerSample;
  const buffer = Buffer.alloc(44 + dataSize);
  buffer.write('RIFF', 0);
  buffer.writeUInt32LE(36 + dataSize, 4);
  buffer.write('WAVE', 8);
  buffer.write('fmt ', 12);
  buffer.writeUInt32LE(16, 16);
  buffer.writeUInt16LE(3, 20); // IEEE float
  buffer.writeUInt16LE(2, 22);
  buffer.writeUInt32LE(SR, 24);
  buffer.writeUInt32LE(SR * 2 * bytesPerSample, 28);
  buffer.writeUInt16LE(2 * bytesPerSample, 32);
  buffer.writeUInt16LE(32, 34);
  buffer.write('data', 36);
  buffer.writeUInt32LE(dataSize, 40);
  let offset = 44;
  for (let i = 0; i < N; i++) {
    buffer.writeFloatLE(left[i], offset);
    buffer.writeFloatLE(right[i], offset + 4);
    offset += 8;
  }
  fs.writeFileSync(file, buffer);
};

/** Runs a loudnorm analysis pass and returns the parsed measurement. */
const measure = async (file) => {
  const stderr = await run([
    '-hide_banner', '-i', file,
    '-af',
      `loudnorm=I=${AUDIO.targetLufs}:TP=${AUDIO.wavTruePeakDb}:LRA=11:print_format=json`,
    '-f', 'null', '-',
  ]);
  return JSON.parse(
    stderr.slice(stderr.lastIndexOf('{'), stderr.lastIndexOf('}') + 1),
  );
};

const main = async () => {
  fs.mkdirSync(publicDir, {recursive: true});
  const raw = path.join(publicDir, 'score-raw.wav');
  const staged = path.join(publicDir, 'score-staged.wav');
  const out = path.join(publicDir, 'score.wav');
  writeWav(raw);
  console.log(`Synthesised ${DURATION_IN_SECONDS.toFixed(2)} s of score → score-raw.wav`);

  const first = await measure(raw);
  console.log(`  raw: ${first.input_i} LUFS, TP ${first.input_tp} dBTP, LRA ${first.input_lra}`);

  // Two-pass loudnorm. Its own true-peak limiter handles the ceiling, so no
  // extra limiter is stacked on top — that would pull integrated loudness off
  // target and defeat the measurement.
  await run([
    '-y', '-i', raw,
    '-af',
      `loudnorm=I=${AUDIO.targetLufs}:TP=${AUDIO.wavTruePeakDb}:LRA=11:` +
      `measured_I=${first.input_i}:measured_TP=${first.input_tp}:` +
      `measured_LRA=${first.input_lra}:measured_thresh=${first.input_thresh}:` +
      `offset=${first.target_offset}`,
    '-ar', String(SR), '-ac', '2', '-c:a', 'pcm_s24le',
    staged,
  ]);

  // loudnorm can land up to ~1 LU off target when it falls back to dynamic
  // mode, so verify and apply a corrective gain rather than trusting it.
  const check = await measure(staged);
  const delta = AUDIO.targetLufs - Number(check.input_i);
  console.log(`  staged: ${check.input_i} LUFS, TP ${check.input_tp} dBTP (delta ${delta.toFixed(2)} LU)`);

  if (Math.abs(delta) > 0.2) {
    const ceiling = (10 ** (AUDIO.wavTruePeakDb / 20)).toFixed(4);
    await run([
      '-y', '-i', staged,
      '-af', `volume=${delta.toFixed(2)}dB,alimiter=limit=${ceiling}:level=disabled`,
      '-ar', String(SR), '-ac', '2', '-c:a', 'pcm_s24le',
      out,
    ]);
  } else {
    fs.copyFileSync(staged, out);
  }

  const final = await measure(out);
  console.log(
    `  → public/score.wav: ${final.input_i} LUFS, TP ${final.input_tp} dBTP ` +
      `(WAV ceiling ${AUDIO.wavTruePeakDb} dBTP leaves headroom for the AAC encode)`,
  );

  fs.rmSync(raw, {force: true});
  fs.rmSync(staged, {force: true});
};

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
