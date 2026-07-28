import { el } from '../dom.js';
import { LOGO_VIDEO, frames } from '../timing.js';

/**
 * SCENE 7 — LOGO REVEAL (pre-rendered)
 *
 * The supplied "Logo Reveal-4.mp4" is the authoritative payoff, so it is
 * played rather than rebuilt. Only the payoff section is used — see
 * LOGO_VIDEO.in in timing.js.
 *
 * The delivered file is 1280x720 landscape and therefore occupies a centre
 * band of the 9:16 frame. The surround is animated from the film's near-black
 * to the video's white end card so the letterbox never reads as a mistake.
 * When a 1080x1920 re-render is dropped in, set LOGO_VIDEO.native = true and
 * the surround is skipped entirely.
 */
export function build({ root, tl, t0, dur, video, backdrop }) {
  // The replacement asset is expected to be portrait. Infer that from the
  // decoded dimensions so dropping it at the documented path is enough; the
  // explicit timing flag remains available for an asset whose framing needs
  // to override the aspect-ratio heuristic.
  const native = LOGO_VIDEO.native || (video.videoWidth > 0 && video.videoHeight > video.videoWidth);

  // The surround lives in #video-backdrop, which is a sibling *before* the
  // video element. Putting it in the overlay would draw it on top and hide
  // the reveal entirely.
  const surround = backdrop;

  // Softens the band edges while the video content is still dark.
  const seam = el('div');
  Object.assign(seam.style, {
    position: 'absolute',
    inset: '0',
    background:
      'linear-gradient(180deg, rgba(5,9,11,1) 0%, rgba(5,9,11,0) 32%, rgba(5,9,11,0) 68%, rgba(5,9,11,1) 100%)',
    opacity: '0.85',
    pointerEvents: 'none',
  });
  if (!native) root.append(seam);

  tl.set(root, { opacity: 1 }, t0);
  tl.set(video, { opacity: 1 }, t0);
  if (!native) tl.set(surround, { opacity: 1 }, t0);

  // The video's own white wipe lands ~0.4s into the trimmed clip; the surround
  // and the seam follow it so the frame turns white as one piece.
  const wipeAt = t0 + 0.4;
  if (!native) {
    tl.to(surround, { background: '#ffffff', duration: frames(3), ease: 'power2.in' }, wipeAt);
    tl.to(seam, { opacity: 0, duration: frames(3) }, wipeAt);
  }

  // Video stays on screen through the title hold — scene 8 draws on top of
  // its final frame rather than recreating the logo lockup.
  tl.set(root, { opacity: 1 }, t0 + dur);

  /**
   * Frame-accurate video sync. Resolves once the decoder has actually
   * presented the requested frame, which matters for headless capture.
   */
  function syncVideo(globalTime) {
    const local = Math.max(0, Math.min(dur, globalTime - t0));
    const target = LOGO_VIDEO.in + local;
    if (Math.abs(video.currentTime - target) < 0.001) return Promise.resolve();
    return new Promise((resolve) => {
      let settled = false;
      const done = () => {
        if (settled) return;
        settled = true;
        resolve();
      };
      if ('requestVideoFrameCallback' in video) video.requestVideoFrameCallback(done);
      else video.addEventListener('seeked', done, { once: true });
      // Never let a dropped seek stall the whole capture.
      setTimeout(done, 400);
      video.currentTime = target;
    });
  }

  return {
    syncVideo,
    isActive: (time) => time >= t0 - 0.1,
  };
}
