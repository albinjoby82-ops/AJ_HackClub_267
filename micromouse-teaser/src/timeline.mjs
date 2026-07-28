/**
 * Micro-Mouse '26 teaser — single source of truth.
 *
 * Everything downstream (Remotion components, the audio generator, the QA
 * tools) imports timings, colours, copy and asset paths from this file. Do not
 * duplicate any of these numbers elsewhere.
 *
 * The composition runs at the same frame rate as the source footage (30 fps),
 * so one composition frame maps to exactly one source frame. That keeps every
 * cut frame-accurate and avoids duplicate-frame stutter.
 */

export const FPS = 30;
export const WIDTH = 1080;
export const HEIGHT = 1920;

/** Primary source footage: 478x850, 30 fps, 20.30 s. */
export const SOURCE = {
  video: 'primary-1080.mp4',
  fps: 30,
  durationInSeconds: 20.3,
};

export const ASSETS = {
  logo: 'elecsoc-logo.png',
  font: 'fonts/bahnschrift.ttf',
  score: 'score.wav',
};

/** ElecSoc identity palette. */
export const COLORS = {
  navy: '#03131A',
  teal: '#0B3948',
  cyan: '#91BEC1',
  orange: '#E76533',
  offWhite: '#EEF3F5',
};

/** Exact copy. The apostrophe in the title is U+2019. */
export const COPY = {
  teaser: 'THE MAZE IS WAITING.',
  impacts: ['SMALLER.', 'FASTER.', 'SMARTER.'],
  title: 'MICRO-MOUSE ’26',
  tagline: 'BUILD IT. CODE IT. RACE IT.',
  comingSoon: 'COMING SOON',
};

/**
 * Vertical-video safe margins. The bottom band is reserved for platform
 * overlays (TikTok caption/buttons), so no critical text may enter it.
 */
export const SAFE = {
  side: 96,
  top: 220,
  bottom: 300,
};

/**
 * Source ranges that are free of the animation's own baked-in typography.
 * The render already contains "SMALLER." (1.75-2.50 s), "FASTER."
 * (3.90-4.70 s) and "SMARTER." (6.30-7.10 s) burned into the picture, plus a
 * low-resolution end card from 15.4 s. We cut around all of it and lay in our
 * own crisp type instead.
 *
 * `zoom` / `focus` drive a transform-origin scale on the video, which is how
 * the tight detail crops are achieved without letterboxing or distortion.
 */
const SEGMENTS = [
  {
    id: 'preBlack',
    durationInFrames: 12,
    kind: 'black',
  },
  {
    id: 'coldOpen',
    durationInFrames: 30,
    kind: 'video',
    sourceStartFrame: 0, // 0.000 s
    zoom: [1.12, 1.04],
    focus: [0.42, 0.42],
    brightness: [0.55, 1.0],
  },
  {
    id: 'detailFront',
    durationInFrames: 21,
    kind: 'video',
    sourceStartFrame: 30, // 1.000 s
    zoom: [1.5, 1.62],
    focus: [0.42, 0.6],
  },
  { id: 'gap1', durationInFrames: 3, kind: 'black' },
  {
    // Tight wheel/route detail. The 2.08x crop deliberately sits below the
    // baked-in "SMALLER." so this range stays usable.
    id: 'detailWheel',
    durationInFrames: 25,
    kind: 'video',
    sourceStartFrame: 52, // 1.733 s
    zoom: [2.08, 2.2],
    focus: [0.31, 0.76],
  },
  { id: 'gap2', durationInFrames: 3, kind: 'black' },
  {
    id: 'detailMid',
    durationInFrames: 39,
    kind: 'video',
    sourceStartFrame: 77, // 2.567 s
    zoom: [1.26, 1.16],
    focus: [0.5, 0.55],
  },
  {
    id: 'steady',
    durationInFrames: 45,
    kind: 'video',
    sourceStartFrame: 143, // 4.767 s
    zoom: [1.0, 1.05],
    focus: [0.5, 0.55],
  },
  {
    id: 'chase',
    durationInFrames: 199,
    kind: 'video',
    sourceStartFrame: 215, // 7.167 s
    zoom: [1.0, 1.0],
    focus: [0.5, 0.5],
  },
  {
    // The orange route line draws the ElecSoc circle. This is the bridge into
    // the reveal, and it ends just before the source's own soft logo card.
    id: 'bridge',
    durationInFrames: 40,
    kind: 'video',
    sourceStartFrame: 414, // 13.800 s
    zoom: [1.0, 1.03],
    focus: [0.44, 0.4],
  },
  {
    id: 'endCard',
    durationInFrames: 164,
    kind: 'endCard',
  },
];

/** Adds cumulative `from` offsets so no start frame is hand-maintained. */
function withOffsets(segments) {
  let from = 0;
  return segments.map((segment) => {
    const withFrom = { ...segment, from };
    from += segment.durationInFrames;
    return withFrom;
  });
}

export const TIMELINE = withOffsets(SEGMENTS);

export const DURATION_IN_FRAMES = TIMELINE.reduce(
  (total, segment) => total + segment.durationInFrames,
  0,
);

export const segment = (id) => {
  const found = TIMELINE.find((s) => s.id === id);
  if (!found) throw new Error(`Unknown segment: ${id}`);
  return found;
};

/**
 * Typography cues, in absolute composition frames.
 *
 * The teaser line clears the screen before the chase begins, and each impact
 * word gets its own moment with no overlap.
 */
export const TEXT_CUES = {
  teaser: { from: 96, durationInFrames: 68 },
  impacts: [
    { word: COPY.impacts[0], from: 195, durationInFrames: 33 },
    { word: COPY.impacts[1], from: 250, durationInFrames: 33 },
    { word: COPY.impacts[2], from: 305, durationInFrames: 33 },
  ],
};

/**
 * End-card beats, relative to the start of the end card segment.
 * `hold` is the fully-assembled, completely motionless stretch.
 */
export const END_CARD = {
  blackLead: 6,
  ring: { from: 4, durationInFrames: 22 },
  logo: { from: 6, durationInFrames: 20 },
  title: { from: 22, durationInFrames: 20 },
  tagline: { from: 40, durationInFrames: 16 },
  comingSoon: { from: 54, durationInFrames: 16 },
  /**
   * Everything is settled by frame 70 and nothing moves again until the fade
   * begins at 148 — a 78-frame (2.60 s) genuinely motionless hold.
   */
  settledAt: 70,
  holdUntil: 148,
  fadeOutFrames: 16,
};

/** Audio cue sheet, in seconds, consumed by tools/generate-audio.mjs. */
export const AUDIO = {
  sampleRate: 48000,
  targetLufs: -14,
  /** Delivery requirement for the finished MP4. */
  truePeakDb: -1,
  /**
   * The WAV is normalised to a lower ceiling than the delivery target because
   * the AAC encode overshoots sample peaks by roughly 1 dB. Normalising the
   * WAV straight to -1 dBTP lands the finished file just over 0 dBTP.
   */
  wavTruePeakDb: -2.5,
  cues: {
    powerOn: segment('coldOpen').from / FPS,
    sensorPing: segment('detailFront').from / FPS,
    servoClicks: [
      segment('detailWheel').from / FPS,
      segment('detailMid').from / FPS,
    ],
    pulseStart: segment('steady').from / FPS,
    chaseStart: segment('chase').from / FPS,
    impacts: TEXT_CUES.impacts.map((cue) => cue.from / FPS),
    riserStart: 338 / FPS,
    bridge: segment('bridge').from / FPS,
    revealHit: (segment('endCard').from + END_CARD.logo.from) / FPS,
    finalHit: (segment('endCard').from + END_CARD.comingSoon.from) / FPS,
    fadeStart: (segment('endCard').from + END_CARD.holdUntil) / FPS,
  },
};

export const DURATION_IN_SECONDS = DURATION_IN_FRAMES / FPS;
