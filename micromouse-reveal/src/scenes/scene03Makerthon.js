import { ASSETS } from '../assets.js';
import { photo, statBlock, fill } from '../dom.js';
import { frames } from '../timing.js';

/**
 * SCENE 3 — MAKERTHON (0:09–0:16)
 * The beat drops. Three statistics land on three bass hits; on CHAOS the
 * cards and photographs collide, rotate and settle without ever obscuring
 * the readable type.
 */

const SHOTS = [
  { src: ASSETS.makerthon.crowdWide, at: 0.0, hold: 1.0, rect: { x: 0, y: 0, w: 1080, h: 1920 }, from: { scale: 1.22 }, to: { scale: 1.04 }, focal: '50% 40%' },
  { src: ASSETS.makerthon.room, at: 1.0, hold: 0.78, rect: { x: 0, y: 180, w: 1080, h: 1500 }, from: { scale: 1.16, x: -50 }, to: { scale: 1.02, x: 30 } },
  { src: ASSETS.makerthon.teamWorking, at: 1.78, hold: 0.82, rect: { x: 0, y: 300, w: 1080, h: 1340 }, from: { scale: 1.2, y: 30 }, to: { scale: 1.03, y: -20 } },
  { src: ASSETS.makerthon.prizesTable, at: 2.6, hold: 1.0, rect: { x: 0, y: 0, w: 1080, h: 1920 }, from: { scale: 1.18, x: 40 }, to: { scale: 1.02, x: -30 }, focal: '50% 52%' },
  { src: ASSETS.makerthon.winners, at: 3.6, hold: 0.98, rect: { x: 0, y: 0, w: 1080, h: 1920 }, from: { scale: 1.14 }, to: { scale: 1.0 }, focal: '50% 42%' },
  { src: ASSETS.makerthon.mentorshipRoom, at: 5.5, hold: 0.9, rect: { x: 0, y: 340, w: 1080, h: 1300 }, from: { scale: 1.2, rotate: 1.2 }, to: { scale: 1.02, rotate: -0.3 } },
];

// Designed cards are memory flashes only — never on screen past ~0.45s, and
// never while a statistic is up. The cards carry their own baked-in "85+ /
// €250 / 100%" text, which collides illegibly with the kinetic type.
const CARD_FLASHES = [
  { src: ASSETS.cards.makerthonHero, at: 0.0, hold: 0.36 },
  { src: ASSETS.cards.makerthonStats, at: 5.86, hold: 0.38 },
];

const STATS = [
  { num: '85<em>+</em>', label: 'Sign-ups', at: 0.62, out: 2.4, top: 700 },
  { num: '<em>€</em>250', label: 'In prizes', at: 2.66, out: 4.1, top: 700 },
];

export function build({ root, tl, t0 }) {
  root.append(fill('#05090b'));
  tl.set(root, { opacity: 1 }, t0);

  for (const shot of SHOTS) {
    const node = photo(shot.src, shot.rect, { focal: shot.focal });
    root.append(node);
    const start = t0 + shot.at;
    tl.set(node, { opacity: 0, ...shot.from }, start - 0.01);
    // Hard cut in — a 1-frame fade leaves the scene's opening frame black.
    tl.set(node, { opacity: 1 }, start);
    tl.to(node, { ...shot.to, duration: shot.hold + 0.12, ease: 'none' }, start);
    tl.set(node, { opacity: 0 }, start + shot.hold);
  }

  for (const card of CARD_FLASHES) {
    const node = photo(card.src, { x: 60, y: 430, w: 960, h: 1060 }, { plain: true });
    node.querySelector('img').style.objectFit = 'contain';
    root.append(node);
    const start = t0 + card.at;
    tl.set(node, { opacity: 0, scale: 1.1 }, start - 0.01);
    tl.to(node, { opacity: 1, scale: 1.0, duration: frames(2), ease: 'power2.out' }, start);
    tl.set(node, { opacity: 0 }, start + card.hold);
  }

  for (const s of STATS) {
    const block = statBlock(s.num, s.label, { top: s.top });
    root.append(block);
    const num = block.querySelector('.num');
    const label = block.querySelector('.label');
    const start = t0 + s.at;

    tl.set(block, { opacity: 1 }, start);
    // Number lands first...
    tl.fromTo(num, { opacity: 0, scale: 1.18, y: 20 }, { opacity: 1, scale: 1, y: 0, duration: frames(4), ease: 'power3.out' }, start);
    // ...label follows three frames later.
    tl.fromTo(label, { opacity: 0, letterSpacing: '0.6em' }, { opacity: 1, letterSpacing: '0.34em', duration: frames(5), ease: 'power2.out' }, start + frames(3));
    tl.set(block, { opacity: 0 }, t0 + s.out);
  }

  buildChaos(root, tl, t0 + 4.16);

  tl.set(root, { opacity: 0 }, t0 + 7.0);
}

/**
 * "100% CHAOS": the frame briefly loses control. Photographs tumble in at
 * angles, collide and settle into a loose stack behind the type — which stays
 * upright and fully legible throughout.
 */
function buildChaos(root, tl, start) {
  const debris = [
    { src: ASSETS.makerthon.teamWorking, x: 40, y: 300, w: 460, h: 340, rot: -14, fromX: -520, fromY: -180 },
    { src: ASSETS.makerthon.prizesTable, x: 560, y: 380, w: 470, h: 350, rot: 11, fromX: 560, fromY: -240 },
    { src: ASSETS.makerthon.crowdWide, x: 120, y: 1200, w: 500, h: 360, rot: 8, fromX: -480, fromY: 420 },
    { src: ASSETS.makerthon.winners, x: 520, y: 1290, w: 480, h: 350, rot: -9, fromX: 520, fromY: 460 },
    { src: ASSETS.makerthon.room, x: 300, y: 760, w: 440, h: 320, rot: 4, fromX: 0, fromY: -560 },
  ];

  debris.forEach((d, i) => {
    const node = photo(d.src, { x: d.x, y: d.y, w: d.w, h: d.h });
    node.style.boxShadow = '0 24px 60px rgba(0,0,0,.55)';
    root.append(node);
    const at = start + i * frames(2);

    tl.set(node, { opacity: 0, x: d.fromX, y: d.fromY, rotation: d.rot * 3, scale: 1.2 }, at - 0.01);
    tl.to(node, { opacity: 1, duration: frames(1) }, at);
    // Impact, then a short settle — the collision reads as physical.
    tl.to(node, { x: 0, y: 0, rotation: d.rot, scale: 1, duration: frames(7), ease: 'power4.out' }, at);
    tl.to(node, { rotation: d.rot * 0.82, duration: frames(6), ease: 'sine.inOut' }, at + frames(7));
    tl.to(node, { opacity: 0, duration: frames(2) }, start + 1.5);
  });

  // Type sits above the debris and never rotates.
  const stat = statBlock('100<em>%</em>', 'Chaos', { top: 700 });
  stat.style.zIndex = '5';
  root.append(stat);
  const num = stat.querySelector('.num');
  const label = stat.querySelector('.label');

  tl.set(stat, { opacity: 1 }, start + frames(1));
  tl.fromTo(num, { opacity: 0, scale: 1.24 }, { opacity: 1, scale: 1, duration: frames(4), ease: 'power4.out' }, start + frames(1));
  tl.fromTo(label, { opacity: 0, letterSpacing: '0.7em' }, { opacity: 1, letterSpacing: '0.34em', duration: frames(5), ease: 'power2.out' }, start + frames(4));
  tl.set(stat, { opacity: 0 }, start + 1.62);
}
