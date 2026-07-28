/**
 * Central timing configuration.
 *
 * Every scene reads its start/duration from here so pacing can be retuned
 * without touching scene logic. Times are seconds on the master timeline.
 */

export const FPS = 30;
export const WIDTH = 1080;
export const HEIGHT = 1920;

/**
 * The pre-rendered logo reveal (public/video/logo-reveal.mp4).
 *
 * Only the payoff is used: the supplied file opens with its own ~4.6s maze
 * sequence, which would duplicate scene 6. IN is the moment the circuit
 * completes, just before the white wipe.
 *
 * The delivered file is 1280x720 landscape and is letterboxed into the 9:16
 * frame. A 1080x1920 re-render can be dropped in at the same path — set
 * LOGO_VIDEO.native to true and the letterbox surround is skipped.
 */
export const LOGO_VIDEO = {
  src: '/video/logo-reveal.mp4',
  in: 4.6,
  out: 7.8,
  native: false,
};

export const LOGO_VIDEO_DURATION = LOGO_VIDEO.out - LOGO_VIDEO.in;

export const SCENES = {
  powerOn: { start: 0.0, duration: 3.0 },
  robotics: { start: 3.0, duration: 6.0 },
  makerthon: { start: 9.0, duration: 7.0 },
  roboExpo: { start: 16.0, duration: 8.0 },
  pivot: { start: 24.0, duration: 3.0 },
  mazeRun: { start: 27.0, duration: 11.0 },
  logoVideo: { start: 38.0, duration: LOGO_VIDEO_DURATION },
  // Holds the video's final logo state while the tagline and event block land.
  title: { start: 38.0 + LOGO_VIDEO_DURATION, duration: 3.8 },
};

export const TOTAL_DURATION = SCENES.title.start + SCENES.title.duration;
export const TOTAL_FRAMES = Math.round(TOTAL_DURATION * FPS);

/** Convert a frame index to a timeline time. */
export const frameToTime = (frame) => frame / FPS;

/** Beat helper: n frames expressed in seconds, for snappy type timing. */
export const frames = (n) => n / FPS;
