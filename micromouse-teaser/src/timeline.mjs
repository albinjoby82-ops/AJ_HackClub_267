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
  /**
   * The supplied 1080x1920 announcement poster. It is the end card — it already
   * carries the logo, the headline, the event name and the date line, so it is
   * laid in at native resolution rather than rebuilt as live type.
   */
  endPoster: 'dublin/end-poster.png',
};

/** ElecSoc identity palette. */
export const COLORS = {
  navy: '#03131A',
  teal: '#0B3948',
  cyan: '#91BEC1',
  orange: '#E76533',
  offWhite: '#EEF3F5',
};

/**
 * Exact copy. The apostrophe in the title is U+2019.
 * V2 drops SMALLER. entirely — it is not replaced with another word.
 */
export const COPY = {
  teaser: 'THE MAZE IS WAITING.',
  impacts: ['FASTER.', 'SMARTER.'],
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
    // Runs through the robot's final head-on approach and stops on source
    // frame 416 — the last frame with a fully static route line. From source
    // 417 the orange route begins its step-draw into the question-mark
    // animation, which V2 removes entirely. The action peaks as the robot
    // arrives at the wall, then hard-cuts to the card.
    id: 'chase',
    durationInFrames: 202,
    kind: 'video',
    sourceStartFrame: 215, // 7.167 s
    zoom: [1.0, 1.0],
    focus: [0.5, 0.5],
  },
  {
    id: 'endCard',
    durationInFrames: 120,
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
 * V2: only FASTER. and SMARTER. remain — SMALLER. and its beat are removed and
 * the gap is closed rather than left as a pause. Each word still gets its own
 * moment with no overlap, and the teaser line clears before the first impact.
 */
export const TEXT_CUES = {
  teaser: { from: 96, durationInFrames: 60 },
  impacts: [
    { word: COPY.impacts[0], from: 222, durationInFrames: 39 },
    { word: COPY.impacts[1], from: 315, durationInFrames: 36 },
  ],
};

/**
 * End-card beats, relative to the start of the end card segment.
 *
 * V3: the end card is the supplied announcement poster, and the chase hard-cuts
 * straight onto it. There is still exactly one reveal — no ring match-cut, no
 * logo-first screen, no line-by-line assembly. The poster lifts out of black
 * over eight frames while a three-frame orange flash sells the cut on the bass
 * hit, and it is fully lit and readable from frame 8 onward.
 */
export const END_CARD = {
  /** Frames of the brief accent flash laid over the incoming poster. */
  flashFrames: 3,
  /**
   * The lights-up reveal: the poster rises from black to full brightness while
   * a whisper of scale settles out. Must finish by `settledAt` so the hold that
   * follows is genuinely motionless.
   */
  settleFrames: 8,
  /**
   * Nothing moves from frame 8 to the last frame — a 112-frame (3.73 s)
   * motionless hold on the poster. V3 removes the fade to black entirely: the
   * final frame of the teaser is the poster artwork itself, at full strength.
   */
  settledAt: 8,
  holdUntil: 108,
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
    /** Rise out of SMARTER. straight into the cut. */
    riserStart: 350 / FPS,
    /** The strongest hit lands exactly on the direct cut to the card. */
    revealHit: segment('endCard').from / FPS,
    fadeStart: (segment('endCard').from + END_CARD.holdUntil) / FPS,
  },
};

export const DURATION_IN_SECONDS = DURATION_IN_FRAMES / FPS;
