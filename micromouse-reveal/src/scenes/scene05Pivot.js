import { el, impactWord, fill } from '../dom.js';
import { frames } from '../timing.js';

/**
 * SCENE 5 — THE PIVOT (0:24–0:27)
 * Hard cut to black and near-total silence. The question lands slowly, then a
 * pair of IR beams flicker on and something small corrects itself in the dark.
 */
export function build({ root, tl, t0 }) {
  root.append(fill('#000'));
  tl.set(root, { opacity: 1 }, t0);

  const word = impactWord("So… what's next?", { size: '-lg', top: 860 });
  root.append(word);
  const inner = word.querySelector('.mask > span');

  // Deliberately slower than every other type beat in the film.
  tl.set(word, { opacity: 1 }, t0 + 0.25);
  tl.fromTo(inner, { yPercent: 105 }, { yPercent: 0, duration: 0.55, ease: 'power2.out' }, t0 + 0.25);
  tl.fromTo(word, { letterSpacing: '0.16em', opacity: 0 }, { letterSpacing: '0.02em', opacity: 1, duration: 0.7, ease: 'power2.out' }, t0 + 0.25);
  tl.to(word, { opacity: 0, duration: frames(4) }, t0 + 1.75);

  // Two IR emitters wake up in the dark.
  const beams = [-1, 1].map((side) => {
    const beam = el('div');
    Object.assign(beam.style, {
      position: 'absolute',
      left: `${540 + side * 96 - 7}px`,
      top: '1120px',
      width: '14px',
      height: '14px',
      borderRadius: '50%',
      background: '#6ff0d2',
      boxShadow: '0 0 26px 8px rgba(111,240,210,.75)',
      opacity: '0',
    });
    root.append(beam);
    return beam;
  });

  // Flicker: two false starts before they hold.
  const flickerAt = [1.82, 1.9, 2.02];
  beams.forEach((beam, i) => {
    flickerAt.forEach((f, k) => {
      tl.set(beam, { opacity: k === 2 ? 1 : 0.65 }, t0 + f + i * frames(1));
      if (k < 2) tl.set(beam, { opacity: 0 }, t0 + f + frames(1) + i * frames(1));
    });
  });

  // Projected beam cones, faint, reaching forward into nothing.
  const cones = [-1, 1].map((side) => {
    const cone = el('div');
    Object.assign(cone.style, {
      position: 'absolute',
      left: `${540 + side * 96 - 60}px`,
      top: '900px',
      width: '120px',
      height: '230px',
      background: `linear-gradient(0deg, rgba(111,240,210,.28), rgba(111,240,210,0))`,
      clipPath: 'polygon(42% 100%, 58% 100%, 100% 0%, 0% 0%)',
      opacity: '0',
      filter: 'blur(6px)',
    });
    root.append(cone);
    return cone;
  });
  tl.to(cones, { opacity: 1, duration: frames(4), ease: 'power2.out' }, t0 + 2.04);

  // One tiny corrective wheel movement, then the spool-up begins.
  const wheel = el('div');
  Object.assign(wheel.style, {
    position: 'absolute',
    left: '470px',
    top: '1180px',
    width: '140px',
    height: '140px',
    borderRadius: '50%',
    border: '10px solid rgba(111,240,210,.5)',
    borderTopColor: '#ff5b2e',
    opacity: '0',
  });
  root.append(wheel);

  tl.to(wheel, { opacity: 0.9, duration: frames(2) }, t0 + 2.2);
  tl.fromTo(wheel, { rotation: 0 }, { rotation: 14, duration: frames(3), ease: 'power3.out' }, t0 + 2.3);
  tl.to(wheel, { rotation: 220, duration: 0.45, ease: 'power2.in' }, t0 + 2.55);

  // Everything is swallowed by the launch into the maze.
  tl.to([...beams, ...cones, wheel], { opacity: 0, duration: frames(2) }, t0 + 2.94);
  tl.set(root, { opacity: 0 }, t0 + 3.0);
}
