/**
 * Generates the trailer's original deterministic soundtrack.
 *
 * No samples or external music are used. Every relay, impact, motor tone and
 * synth layer is produced from fixed math/seeded noise, so rebuilding creates
 * the same WAV byte-for-byte.
 */
import { mkdir, writeFile } from 'node:fs/promises';
import path from 'node:path';

const SAMPLE_RATE = 48000;
const DURATION = 45;
const samples = new Float32Array(SAMPLE_RATE * DURATION);
const TAU = Math.PI * 2;

let seed = 0x2672026;
function random() {
  seed ^= seed << 13;
  seed ^= seed >>> 17;
  seed ^= seed << 5;
  return (seed >>> 0) / 4294967296;
}

function addTone(start, duration, fromHz, toHz, gain, options = {}) {
  const startSample = Math.max(0, Math.floor(start * SAMPLE_RATE));
  const count = Math.min(Math.floor(duration * SAMPLE_RATE), samples.length - startSample);
  const attack = options.attack ?? 0.008;
  const release = options.release ?? Math.min(0.18, duration * 0.35);
  const harmonic = options.harmonic ?? 0;
  let phase = options.phase ?? 0;

  for (let i = 0; i < count; i++) {
    const time = i / SAMPLE_RATE;
    const progress = i / Math.max(1, count - 1);
    const frequency = fromHz * Math.pow(toHz / fromHz, progress);
    const envelope =
      Math.min(1, time / Math.max(attack, 1 / SAMPLE_RATE)) *
      Math.min(1, (duration - time) / Math.max(release, 1 / SAMPLE_RATE));
    phase += (TAU * frequency) / SAMPLE_RATE;
    const value = Math.sin(phase) + harmonic * Math.sin(phase * 2.01);
    samples[startSample + i] += value * gain * envelope;
  }
}

function addNoise(start, duration, gain, decay = 7, highPass = false) {
  const startSample = Math.max(0, Math.floor(start * SAMPLE_RATE));
  const count = Math.min(Math.floor(duration * SAMPLE_RATE), samples.length - startSample);
  let previous = 0;
  for (let i = 0; i < count; i++) {
    const progress = i / Math.max(1, count - 1);
    const raw = random() * 2 - 1;
    const value = highPass ? raw - previous * 0.92 : raw;
    previous = raw;
    samples[startSample + i] += value * gain * Math.exp(-decay * progress);
  }
}

function addKick(time, gain = 0.55) {
  addTone(time, 0.3, 118, 43, gain, { attack: 0.001, release: 0.24, harmonic: 0.12 });
  addNoise(time, 0.025, gain * 0.18, 14, true);
}

function addSnare(time, gain = 0.16) {
  addNoise(time, 0.14, gain, 8, true);
  addTone(time, 0.11, 190, 150, gain * 0.22, { attack: 0.001, release: 0.09 });
}

function addHat(time, gain = 0.055) {
  addNoise(time, 0.045, gain, 14, true);
}

function addBass(time, duration, frequency, gain) {
  addTone(time, duration, frequency, frequency * 0.995, gain, {
    attack: 0.012,
    release: 0.12,
    harmonic: 0.2,
  });
}

// Power-on: room electricity, relay and circuit ticks.
addTone(0, 3, 47, 52, 0.035, { attack: 0.25, release: 0.35, harmonic: 0.15 });
addNoise(0.18, 0.035, 0.32, 18, true);
addTone(0.18, 0.12, 92, 48, 0.22, { attack: 0.001, release: 0.1 });
for (const time of [0.86, 1.02, 1.18, 1.34, 1.5, 2.08]) {
  addTone(time, 0.055, 1350, 780, 0.055, { attack: 0.001, release: 0.045 });
}
addKick(2.08, 0.56);

// 130 BPM industrial recap.
const beat = 60 / 130;
const bassNotes = [55, 65.406, 73.416, 82.407];
let beatIndex = 0;
for (let time = 3; time < 24; time += beat, beatIndex++) {
  const energy = time < 9 ? 0.72 : time < 16 ? 1 : 0.9;
  addKick(time, 0.48 * energy);
  addHat(time + beat / 2, 0.048 * energy);
  if (beatIndex % 2 === 1) addSnare(time, 0.12 * energy);
  addBass(time + 0.015, beat * 0.82, bassNotes[beatIndex % bassNotes.length], 0.105 * energy);
}

// Statistics and project-change impacts.
for (const time of [9.62, 11.66, 13.16, 16.42, 18.18, 21.3, 21.95, 22.6, 23.25]) {
  addKick(time, 0.7);
  addNoise(time, 0.06, 0.09, 10, true);
}

// The pivot: hard stop, room tone, sensor ticks and a motor pre-spin.
addTone(24, 3, 39, 44, 0.018, { attack: 0.15, release: 0.08 });
addKick(24, 0.34);
for (const time of [25.82, 25.9, 26.02, 26.1]) {
  addTone(time, 0.032, 1850, 1250, 0.075, { attack: 0.001, release: 0.025 });
}
addTone(26.18, 0.82, 54, 230, 0.13, { attack: 0.02, release: 0.04, harmonic: 0.35 });
addNoise(26.45, 0.55, 0.028, 2, true);

// Maze run: beat returns with a rising motor bed and restrained wheel scrubs.
addTone(27, 11, 68, 112, 0.055, { attack: 0.04, release: 0.12, harmonic: 0.42 });
beatIndex = 0;
for (let time = 27; time < 38; time += beat, beatIndex++) {
  const ramp = 0.72 + ((time - 27) / 11) * 0.28;
  addKick(time, 0.43 * ramp);
  addHat(time + beat / 2, 0.052 * ramp);
  if (beatIndex % 2 === 1) addSnare(time, 0.09 * ramp);
  addBass(time + 0.01, beat * 0.76, bassNotes[(beatIndex + 1) % bassNotes.length], 0.095 * ramp);
}
for (const time of [31.55, 33.52, 35.72]) {
  addNoise(time, 0.16, 0.095, 5, true);
  addTone(time, 0.18, 340, 145, 0.06, { attack: 0.002, release: 0.13 });
}

// Route completion: rising electrical charge, then the clean logo impact.
addTone(38, 3.15, 165, 920, 0.105, { attack: 0.05, release: 0.04, harmonic: 0.32 });
addTone(38.45, 2.7, 330, 1380, 0.035, { attack: 0.08, release: 0.04 });
for (let time = 38.2; time < 41.1; time += 0.18) addHat(time, 0.018 + (time - 38.2) * 0.009);
addKick(41.2, 0.92);
addNoise(41.2, 0.22, 0.12, 6, true);
addTone(41.2, 1.35, 52, 38, 0.32, { attack: 0.001, release: 0.95, harmonic: 0.2 });

// Final card: warm restrained chord and one closing circuit stinger.
for (const frequency of [110, 138.591, 164.814, 220]) {
  addTone(41.32, 3.2, frequency, frequency * 1.003, 0.043, {
    attack: 0.08,
    release: 1.1,
    harmonic: 0.12,
  });
}
addKick(43.18, 0.42);
for (const frequency of [110, 146.832, 184.997]) {
  addTone(43.2, 1.65, frequency, frequency, 0.035, { attack: 0.03, release: 0.9, harmonic: 0.1 });
}
addTone(44.25, 0.38, 820, 1640, 0.045, { attack: 0.005, release: 0.3 });

// Normalise once, then encode mono 16-bit PCM.
let peak = 0;
for (const sample of samples) peak = Math.max(peak, Math.abs(sample));
const scale = peak > 0 ? 0.92 / peak : 1;
const pcm = Buffer.alloc(samples.length * 2);
for (let i = 0; i < samples.length; i++) {
  const value = Math.max(-1, Math.min(1, samples[i] * scale));
  pcm.writeInt16LE(Math.round(value * 32767), i * 2);
}

const header = Buffer.alloc(44);
header.write('RIFF', 0);
header.writeUInt32LE(36 + pcm.length, 4);
header.write('WAVE', 8);
header.write('fmt ', 12);
header.writeUInt32LE(16, 16);
header.writeUInt16LE(1, 20);
header.writeUInt16LE(1, 22);
header.writeUInt32LE(SAMPLE_RATE, 24);
header.writeUInt32LE(SAMPLE_RATE * 2, 28);
header.writeUInt16LE(2, 32);
header.writeUInt16LE(16, 34);
header.write('data', 36);
header.writeUInt32LE(pcm.length, 40);

const output = path.resolve('public/audio/score.wav');
await mkdir(path.dirname(output), { recursive: true });
await writeFile(output, Buffer.concat([header, pcm]));
console.log(`audio: ${output} (${DURATION}s, ${SAMPLE_RATE}Hz mono PCM)`);
