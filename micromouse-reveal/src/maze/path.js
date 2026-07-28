/**
 * Arc-length parameterised run path.
 *
 * The authored route is a chain of hard 90-degree corners. Real micromice do
 * not pivot in place at speed — they cut a tight arc — so each corner is
 * replaced with a short quadratic arc. The radius is deliberately small
 * (0.3 of a cell) so the turn still reads as a right angle, and it keeps both
 * the mouse and the chase camera inside the corridor.
 */

import { ROUTE_CELLS, cellCenter } from './maze.js';

const CORNER_R = 0.3;
const SAMPLES_PER_UNIT = 90;

function quadratic(p0, p1, p2, t) {
  const u = 1 - t;
  return {
    x: u * u * p0.x + 2 * u * t * p1.x + t * t * p2.x,
    z: u * u * p0.z + 2 * u * t * p1.z + t * t * p2.z,
  };
}

const sub = (a, b) => ({ x: a.x - b.x, z: a.z - b.z });
const len = (v) => Math.hypot(v.x, v.z);
const norm = (v) => {
  const l = len(v) || 1;
  return { x: v.x / l, z: v.z / l };
};
const add = (a, b) => ({ x: a.x + b.x, z: a.z + b.z });
const scale = (v, k) => ({ x: v.x * k, z: v.z * k });

export function buildPath() {
  const corners = ROUTE_CELLS.map(cellCenter);
  const raw = [];

  raw.push(corners[0]);

  for (let i = 1; i < corners.length - 1; i++) {
    const prev = corners[i - 1];
    const cur = corners[i];
    const next = corners[i + 1];

    const inDir = norm(sub(cur, prev));
    const outDir = norm(sub(next, cur));

    // Clamp the radius so short legs cannot overlap their neighbours' arcs.
    const r = Math.min(CORNER_R, len(sub(cur, prev)) / 2, len(sub(next, cur)) / 2);

    const arcStart = add(cur, scale(inDir, -r));
    const arcEnd = add(cur, scale(outDir, r));

    raw.push(arcStart);
    const steps = 12;
    for (let s = 1; s < steps; s++) raw.push(quadratic(arcStart, cur, arcEnd, s / steps));
    raw.push(arcEnd);
  }

  raw.push(corners[corners.length - 1]);

  // Resample uniformly so lookups are cheap and stable.
  const cumulative = [0];
  for (let i = 1; i < raw.length; i++) cumulative.push(cumulative[i - 1] + len(sub(raw[i], raw[i - 1])));
  const total = cumulative[cumulative.length - 1];

  const count = Math.ceil(total * SAMPLES_PER_UNIT);
  const samples = [];
  let seg = 0;
  for (let i = 0; i <= count; i++) {
    const target = (i / count) * total;
    while (seg < cumulative.length - 2 && cumulative[seg + 1] < target) seg++;
    const spanStart = cumulative[seg];
    const spanLen = cumulative[seg + 1] - spanStart || 1;
    const t = (target - spanStart) / spanLen;
    samples.push({
      x: raw[seg].x + (raw[seg + 1].x - raw[seg].x) * t,
      z: raw[seg].z + (raw[seg + 1].z - raw[seg].z) * t,
    });
  }

  const step = total / count;

  const pointAt = (s) => {
    const clamped = Math.max(0, Math.min(total, s));
    const idx = clamped / step;
    const i = Math.min(samples.length - 2, Math.floor(idx));
    const t = idx - i;
    return {
      x: samples[i].x + (samples[i + 1].x - samples[i].x) * t,
      z: samples[i].z + (samples[i + 1].z - samples[i].z) * t,
    };
  };

  /** Forward unit vector at arc-length s. */
  const tangentAt = (s) => {
    const a = pointAt(s - 0.02);
    const b = pointAt(s + 0.02);
    return norm(sub(b, a));
  };

  /** Signed curvature magnitude, used to drive camera roll and speed ramps. */
  const curvatureAt = (s) => {
    const t1 = tangentAt(s - 0.12);
    const t2 = tangentAt(s + 0.12);
    const cross = t1.x * t2.z - t1.z * t2.x;
    return cross;
  };

  return { pointAt, tangentAt, curvatureAt, length: total };
}
