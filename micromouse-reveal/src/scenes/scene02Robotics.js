import { ASSETS } from '../assets.js';
import { photo, impactWord, fill } from '../dom.js';
import { frames } from '../timing.js';

/**
 * SCENE 2 — ROBOTICS + MAKERLABS (0:03–0:09)
 * Fast tactile montage. Nothing sits still: every shot enters on a push-in or
 * a lateral parallax drift and is cut away rather than dissolved.
 */

// Each shot is a full-bleed or offset frame with its own move.
const SHOTS = [
  { src: ASSETS.robotics.handsOn, at: 0.0, hold: 0.8, rect: { x: 0, y: 0, w: 1080, h: 1920 }, from: { scale: 1.24, x: -40 }, to: { scale: 1.08, x: 20 }, focal: '50% 42%' },
  { src: ASSETS.makerlabs.soldering02, at: 0.8, hold: 0.62, rect: { x: 0, y: 240, w: 1080, h: 1440 }, from: { scale: 1.18, y: 30 }, to: { scale: 1.02, y: -18 } },
  { src: ASSETS.robotics.workspace, at: 1.42, hold: 0.74, rect: { x: 0, y: 0, w: 1080, h: 1920 }, from: { scale: 1.02, x: 60 }, to: { scale: 1.16, x: -40 }, focal: '50% 55%' },
  { src: ASSETS.makerlabs.printFarm, at: 2.16, hold: 0.8, rect: { x: 0, y: 400, w: 1080, h: 1180 }, from: { scale: 1.3, rotate: -1.5 }, to: { scale: 1.04, rotate: 0.4 } },
  { src: ASSETS.robotics.buildCloseup, at: 2.96, hold: 0.66, rect: { x: 0, y: 220, w: 1080, h: 1420 }, from: { scale: 1.22, x: 40 }, to: { scale: 1.04, x: -30 } },
  { src: ASSETS.makerlabs.soldering01, at: 3.62, hold: 0.6, rect: { x: 0, y: 380, w: 1080, h: 1240 }, from: { scale: 1.26, y: -24 }, to: { scale: 1.06, y: 14 } },
  { src: ASSETS.makerlabs.audience, at: 4.22, hold: 0.72, rect: { x: 0, y: 0, w: 1080, h: 1920 }, from: { scale: 1.2 }, to: { scale: 1.03 }, focal: '50% 38%' },
  { src: ASSETS.makerlabs.group, at: 4.94, hold: 1.06, rect: { x: 0, y: 0, w: 1080, h: 1920 }, from: { scale: 1.16, y: 24 }, to: { scale: 1.0, y: -10 }, focal: '50% 45%' },
];

const WORDS = [
  { text: 'We wired.', at: 0.15, out: 1.3, top: 1380 },
  { text: 'We coded.', at: 1.5, out: 2.8, top: 1380 },
  { text: 'We made it move.', at: 3.7, out: 5.9, top: 1330, size: '-lg' },
];

export function build({ root, tl, t0 }) {
  root.append(fill('#05090b'));

  tl.set(root, { opacity: 1 }, t0);

  for (const shot of SHOTS) {
    const node = photo(shot.src, shot.rect, { focal: shot.focal });
    root.append(node);

    const start = t0 + shot.at;
    tl.set(node, { opacity: 0, ...shot.from }, start - 0.01);
    // Hard cut in. A 1-frame fade leaves the scene's opening frame black,
    // which reads as a dropped frame between scenes.
    tl.set(node, { opacity: 1 }, start);
    tl.to(node, { ...shot.to, duration: shot.hold + 0.12, ease: 'none' }, start);
    // Hard cut out — no dissolve.
    tl.set(node, { opacity: 0 }, start + shot.hold);
  }

  for (const w of WORDS) {
    const word = impactWord(w.text, { size: w.size ?? '-xl', top: w.top });
    root.append(word);
    const inner = word.querySelector('.mask > span');
    const start = t0 + w.at;

    tl.set(word, { opacity: 1 }, start);
    tl.fromTo(inner, { yPercent: 115 }, { yPercent: 0, duration: frames(5), ease: 'power3.out' }, start);
    tl.fromTo(
      word,
      { scale: 1.07, letterSpacing: '0.07em' },
      { scale: 1, letterSpacing: '0.01em', duration: frames(6), ease: 'power2.out' },
      start,
    );
    tl.set(word, { opacity: 0 }, t0 + w.out);
  }

  tl.set(root, { opacity: 0 }, t0 + 6.0);
}
