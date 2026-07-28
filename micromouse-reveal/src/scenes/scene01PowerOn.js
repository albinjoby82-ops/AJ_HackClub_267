import { ASSETS } from '../assets.js';
import { el, photo, impactWord, fill } from '../dom.js';
import { frames } from '../timing.js';

/**
 * SCENE 1 — POWER ON (0:00–0:03)
 * Black, one relay click, circuit traces light in sequence, the logo is only
 * half-booted. Macro fragments flicker. "WE BUILT." lands on the last beat.
 */
export function build({ root, tl, t0 }) {
  root.append(fill('#05090b'));

  // Circuit traces — drawn with dash offsets so the reveal is frame-exact.
  const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
  svg.setAttribute('viewBox', '0 0 1080 1920');
  Object.assign(svg.style, { position: 'absolute', inset: '0', width: '100%', height: '100%' });

  const paths = [
    'M -40 620 H 300 V 430 H 640',
    'M 1120 780 H 780 V 980 H 430',
    'M -40 1180 H 250 V 1340 H 700 V 1180 H 1120',
    'M 540 -40 V 240 H 860 V 520',
    'M 180 1960 V 1620 H 520',
  ];

  const traces = paths.map((d) => {
    const p = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    p.setAttribute('d', d);
    p.setAttribute('fill', 'none');
    p.setAttribute('stroke', '#6ff0d2');
    p.setAttribute('stroke-width', '3');
    p.setAttribute('opacity', '0.85');
    svg.append(p);
    return p;
  });

  // Nodes sit at trace corners and pop as the current reaches them.
  const nodePts = [
    [300, 430],
    [780, 980],
    [700, 1180],
    [860, 240],
    [520, 1620],
  ];
  const nodes = nodePts.map(([cx, cy]) => {
    const c = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
    c.setAttribute('cx', cx);
    c.setAttribute('cy', cy);
    c.setAttribute('r', '10');
    c.setAttribute('fill', '#ff5b2e');
    svg.append(c);
    return c;
  });

  root.append(svg);

  // Macro fragments — shallow, tight, barely lit.
  const macro1 = photo(ASSETS.robotics.buildCloseup, { x: 120, y: 480, w: 840, h: 620 });
  const macro2 = photo(ASSETS.makerlabs.soldering01, { x: 220, y: 700, w: 640, h: 520 });
  root.append(macro1, macro2);

  // Half-booted logo.
  const logo = el('div');
  Object.assign(logo.style, {
    position: 'absolute',
    left: '240px',
    top: '760px',
    width: '600px',
    height: '400px',
    background: `center / contain no-repeat url(${ASSETS.logo})`,
    filter: 'brightness(0) invert(1)',
    opacity: '0',
  });
  root.append(logo);

  const word = impactWord('We built.', { size: '-xl', top: 1240 });
  root.append(word);

  // ── Timeline ──────────────────────────────────────────────────────────
  tl.set(root, { opacity: 1 }, t0);

  // Relay click: one hard flash of the first trace before anything else.
  tl.fromTo(traces[0], { opacity: 0 }, { opacity: 1, duration: frames(1) }, t0 + 0.18);
  tl.to(traces[0], { opacity: 0, duration: frames(2) }, t0 + 0.22);

  traces.forEach((p, i) => {
    const len = p.getTotalLength();
    tl.set(p, { strokeDasharray: len, strokeDashoffset: len, opacity: 0.85 }, t0 + 0.35);
    tl.to(
      p,
      { strokeDashoffset: 0, duration: 0.55, ease: 'power2.inOut' },
      t0 + 0.4 + i * 0.16,
    );
  });

  nodes.forEach((c, i) => {
    tl.fromTo(
      c,
      { scale: 0, transformOrigin: 'center', svgOrigin: `${nodePts[i][0]} ${nodePts[i][1]}` },
      { scale: 1, duration: frames(3), ease: 'back.out(3)' },
      t0 + 0.85 + i * 0.16,
    );
  });

  // Macro flickers cut in over the traces.
  tl.fromTo(macro1, { opacity: 0, scale: 1.18 }, { opacity: 0.55, scale: 1.06, duration: 0.5, ease: 'power2.out' }, t0 + 0.9);
  tl.to(macro1, { opacity: 0, duration: frames(2) }, t0 + 1.5);
  tl.fromTo(macro2, { opacity: 0, scale: 1.22 }, { opacity: 0.5, scale: 1.08, duration: 0.4, ease: 'power2.out' }, t0 + 1.58);
  tl.to(macro2, { opacity: 0, duration: frames(2) }, t0 + 2.0);

  // Logo boots partially, then dims — it is not the payoff yet.
  tl.fromTo(logo, { opacity: 0 }, { opacity: 0.28, duration: 0.4, ease: 'power1.out' }, t0 + 1.2);
  tl.to(logo, { opacity: 0.1, duration: 0.6 }, t0 + 2.1);

  // "WE BUILT." — mask-on with a small overshoot, settling in 5 frames.
  const inner = word.querySelector('.mask > span');
  tl.set(word, { opacity: 1 }, t0 + 2.05);
  tl.fromTo(inner, { yPercent: 110 }, { yPercent: 0, duration: frames(6), ease: 'power3.out' }, t0 + 2.1);
  tl.fromTo(word, { scale: 1.06, letterSpacing: '0.06em' }, { scale: 1, letterSpacing: '0.01em', duration: frames(5), ease: 'power2.out' }, t0 + 2.1);

  // Hand off: everything drops out on the cut into scene 2.
  tl.to([svg, word, logo], { opacity: 0, duration: frames(2) }, t0 + 2.9);
  tl.set(root, { opacity: 0 }, t0 + 3.0);
}
