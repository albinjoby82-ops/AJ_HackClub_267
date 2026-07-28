import { ASSETS } from '../assets.js';
import { photo, statBlock, impactWord, objectShot, projectLabel, fill } from '../dom.js';
import { frames } from '../timing.js';

/**
 * SCENE 4 — ROBOEXPO (0:16–0:24)
 * Heavier bass. Two statistics, one closing line, then the four featured
 * projects presented as hero objects — each one displaced by the next on a hit.
 */

const SHOTS = [
  { src: ASSETS.roboexpo.heroCrowd, at: 0.0, hold: 1.0, rect: { x: 0, y: 0, w: 1080, h: 1920 }, from: { scale: 1.2 }, to: { scale: 1.03 }, focal: '50% 40%' },
  { src: ASSETS.roboexpo.crowdWide, at: 1.0, hold: 0.8, rect: { x: 0, y: 180, w: 1080, h: 1520 }, from: { scale: 1.16, x: 40 }, to: { scale: 1.02, x: -34 } },
  { src: ASSETS.roboexpo.robotTrack, at: 1.8, hold: 0.7, rect: { x: 0, y: 360, w: 1080, h: 1280 }, from: { scale: 1.24, y: 24 }, to: { scale: 1.04, y: -16 } },
  { src: ASSETS.roboexpo.demoersRoom, at: 2.5, hold: 0.6, rect: { x: 0, y: 240, w: 1080, h: 1440 }, from: { scale: 1.18, x: -40 }, to: { scale: 1.03, x: 24 } },
  { src: ASSETS.roboexpo.teamsRoom, at: 3.1, hold: 0.6, rect: { x: 0, y: 380, w: 1080, h: 1240 }, from: { scale: 1.2, rotate: -1 }, to: { scale: 1.02, rotate: 0.3 } },
  { src: ASSETS.roboexpo.officersGroup, at: 3.7, hold: 1.1, rect: { x: 0, y: 0, w: 1080, h: 1920 }, from: { scale: 1.14, y: 20 }, to: { scale: 1.0, y: -12 }, focal: '50% 44%' },
];

// Placed in the gaps between statistics — the cards have their own baked-in
// numbers and overlap illegibly with the kinetic type otherwise.
// roboexpo_year_of_work is deliberately unused: the same message is carried
// by the "A YEAR OF WORK. ONE ROOM." type beat and there is no clean gap.
const CARD_FLASHES = [
  { src: ASSETS.cards.roboexpoHero, at: 0.0, hold: 0.34 },
  { src: ASSETS.cards.roboexpoStats, at: 3.5, hold: 0.32 },
  { src: ASSETS.cards.roboexpoDemoers, at: 4.72, hold: 0.22 },
  { src: ASSETS.cards.roboexpoTeams, at: 4.96, hold: 0.24 },
];

const STATS = [
  { num: '180<em>+</em>', label: 'Attendees', at: 0.42, out: 2.0, top: 700 },
  { num: '20<em>+</em>', label: 'Projects', at: 2.18, out: 3.44, top: 700 },
];

// 0.65s each — enter on a mechanical move, label flashes, displaced on the hit.
const PROJECTS = [
  { src: ASSETS.projects.spider, label: 'Robot spider', at: 5.3 },
  { src: ASSETS.projects.drum, label: 'Analogue drum', at: 5.95 },
  { src: ASSETS.projects.sand, altSrc: ASSETS.projects.sandAlt, label: 'Sand machine', at: 6.6 },
  { src: ASSETS.projects.jarvis, label: 'Desktop Jarvis', at: 7.25 },
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
    const node = photo(card.src, { x: 70, y: 260, w: 940, h: 1400 }, { plain: true });
    node.querySelector('img').style.objectFit = 'contain';
    node.style.zIndex = '4';
    root.append(node);
    const start = t0 + card.at;
    tl.set(node, { opacity: 0, scale: 1.08 }, start - 0.01);
    tl.to(node, { opacity: 1, scale: 1, duration: frames(2), ease: 'power2.out' }, start);
    tl.set(node, { opacity: 0 }, start + card.hold);
  }

  for (const s of STATS) {
    const block = statBlock(s.num, s.label, { top: s.top });
    root.append(block);
    const num = block.querySelector('.num');
    const label = block.querySelector('.label');
    const start = t0 + s.at;
    tl.set(block, { opacity: 1 }, start);
    tl.fromTo(num, { opacity: 0, scale: 1.18, y: 20 }, { opacity: 1, scale: 1, y: 0, duration: frames(4), ease: 'power3.out' }, start);
    tl.fromTo(label, { opacity: 0, letterSpacing: '0.6em' }, { opacity: 1, letterSpacing: '0.34em', duration: frames(5), ease: 'power2.out' }, start + frames(3));
    tl.set(block, { opacity: 0 }, t0 + s.out);
  }

  // Closing line over the officers group.
  const line = impactWord('A year of work.<br>One room.', { size: '-lg', top: 1180 });
  root.append(line);
  const lineInner = line.querySelector('.mask > span');
  tl.set(line, { opacity: 1 }, t0 + 3.9);
  tl.fromTo(lineInner, { yPercent: 112 }, { yPercent: 0, duration: frames(6), ease: 'power3.out' }, t0 + 3.9);
  tl.fromTo(line, { scale: 1.05 }, { scale: 1, duration: frames(6), ease: 'power2.out' }, t0 + 3.9);
  tl.set(line, { opacity: 0 }, t0 + 4.68);

  buildProjectSequence(root, tl, t0);

  tl.set(root, { opacity: 0 }, t0 + 8.0);
}

function buildProjectSequence(root, tl, t0) {
  // Dark field so the cut-out objects read cleanly.
  const field = fill('linear-gradient(180deg,#0a2028 0%,#05090b 70%)');
  field.style.opacity = '0';
  root.append(field);
  tl.set(field, { opacity: 1 }, t0 + 5.24);
  tl.set(field, { opacity: 0 }, t0 + 7.9);

  PROJECTS.forEach((p, i) => {
    const shot = objectShot(p.src);
    const altShot = p.altSrc ? objectShot(p.altSrc) : null;
    const label = projectLabel(p.label, { top: 1420 });
    root.append(shot);
    if (altShot) root.append(altShot);
    root.append(label);

    const start = t0 + p.at;
    const dir = i % 2 === 0 ? 1 : -1;

    // 1. precise mechanical entry
    tl.set(shot, { opacity: 0, x: 140 * dir, scale: 0.92 }, start - 0.01);
    tl.set(shot, { opacity: 1 }, start);
    tl.to(shot, { x: 0, scale: 1, duration: frames(5), ease: 'power4.out' }, start);
    tl.to(shot, { scale: 1.04, duration: frames(13), ease: 'none' }, start + frames(5));

    // Match-cut between the two supplied CAD views so both read as one
    // engineered object without taking time from another project.
    if (altShot) {
      tl.set(altShot, { opacity: 0, x: 24 * dir, scale: 0.98 }, start - 0.01);
      tl.set(shot, { opacity: 0 }, start + 0.31);
      tl.set(altShot, { opacity: 1 }, start + 0.31);
      tl.to(altShot, { x: 0, scale: 1.03, duration: frames(4), ease: 'power3.out' }, start + 0.31);
      tl.to(altShot, { x: -160 * dir, opacity: 0, duration: frames(3), ease: 'power2.in' }, start + 0.56);
    }

    // 2. label flashes in just behind the object
    tl.set(label, { opacity: 1 }, start + frames(2));
    tl.fromTo(label, { opacity: 0, letterSpacing: '0.7em' }, { opacity: 1, letterSpacing: '0.42em', duration: frames(4), ease: 'power2.out' }, start + frames(2));

    // 3. displaced by the next object on the hit
    tl.to(shot, { x: -160 * dir, opacity: 0, duration: frames(3), ease: 'power2.in' }, start + 0.56);
    tl.set(label, { opacity: 0 }, start + 0.6);
  });
}
