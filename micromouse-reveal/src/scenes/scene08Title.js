import { el } from '../dom.js';
import { frames } from '../timing.js';

/**
 * SCENE 8 — EVENT TITLE (title hold)
 *
 * The logo lockup and MICRO-MOUSE '26 are already burned into the supplied
 * video, so this scene holds that final frame and lands only what the video
 * does not carry: the tagline, the event block and COMING SOON.
 *
 * Event details are placeholders on purpose — nothing here is invented.
 */
export function build({ root, tl, t0, dur }) {
  const card = el('div', 'title-card');
  // Transparent: the video's own white end frame shows through underneath.
  card.style.background = 'transparent';
  card.style.justifyContent = 'flex-end';
  card.style.paddingBottom = '210px';
  card.style.gap = '52px';

  const tagline = el('div', 'tagline', 'Build it. Code it. Race it.');
  const eventBlock = el(
    'div',
    'event-block',
    '[DATE] · [TIME]<br />[VENUE]<br />[SIGN-UP URL]',
  );
  const comingSoon = el('div', 'coming-soon', 'Coming soon');

  card.append(tagline, eventBlock, comingSoon);
  root.append(card);

  tl.set(root, { opacity: 1 }, t0);

  // Tagline lands first, on the beat after the logo settles.
  tl.fromTo(
    tagline,
    { opacity: 0, y: 26, letterSpacing: '0.5em' },
    { opacity: 1, y: 0, letterSpacing: '0.3em', duration: frames(8), ease: 'power3.out' },
    t0 + 0.12,
  );

  tl.fromTo(
    eventBlock,
    { opacity: 0, y: 20 },
    { opacity: 1, y: 0, duration: frames(7), ease: 'power2.out' },
    t0 + 0.62,
  );

  tl.fromTo(
    comingSoon,
    { opacity: 0, scale: 1.12 },
    { opacity: 1, scale: 1, duration: frames(6), ease: 'power3.out' },
    t0 + 1.0,
  );

  // Hold well past the 2.2s minimum before the film ends.
  tl.set(root, { opacity: 1 }, t0 + dur);
}
