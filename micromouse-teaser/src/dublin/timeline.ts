/**
 * Master timeline for the Dublin Micromouse Open 2026 teaser — 500 frames at
 * 30 fps (16.667 s), 1080×1920. All cut points follow the brief; the four
 * beat frames in the final-poster section sit on the score's half-bar grid
 * (~138 BPM measured from the supplied track: hits at 10.83 / 11.70 / 12.57 /
 * 13.44 s, final accent ~14.35 s).
 */
export const WIDTH = 1080;
export const HEIGHT = 1920;
export const FPS = 30;
export const DURATION_IN_FRAMES = 500;

export const CUTS = {
  /** poster 1 spotlight reveal: frames 0–218 (0–7.300 s) */
  poster1End: 219,
  /** sharp turn shot 1: frames 219–271 (7.300–9.067 s) */
  turn1End: 272,
  /** sharp turn shot 2: frames 272–323 (9.067–10.800 s) */
  turn2End: 324,
  /** final poster four-beat reveal: frames 324–427 (10.800–14.267 s) */
  beatsEnd: 428,
  /** partial hold + fade: frames 428–499 */
  end: 500,
};

/** Musical hits inside the four-beat section (absolute frames). */
export const BEATS = [325, 351, 377, 403];

/** Near-black impact dip closing turn 2 (absolute frame → overlay opacity). */
export const TURN2_DIP: Array<[number, number]> = [
  [321, 0.5],
  [322, 0.85],
  [323, 0.95],
];

/** Fade toward near-black across the final 8 frames. */
export const END_FADE = {start: 492, opacity: 0.94};

export type SpotKey = {
  f: number; // absolute frame
  x: number;
  y: number;
  rx: number;
  ry: number;
  it: number; // beam intensity 0..1 (max brightness at the hole centre)
};

/**
 * Poster 1 track — top-down reveal: the beam opens cold on "ONE WAY OUT",
 * picks up "16 × 16" above it, then follows the maze route down through the
 * teal nodes and the orange line, landing on the glowing node on the 3.7 s
 * hit, and finally widens across "SOMETHING IS LEARNING THE MAZE".
 *
 * Poster geometry (1080×1920 composition space, measured off the 2160×3840
 * export): "16 × 16" (538, 149); "ONE WAY OUT" (533, 228) spanning x 254–811;
 * teal node top-right (902, 555); teal junction node (545, 573); the orange
 * route runs down x≈545 from y 595 to 826; glowing orange node (547, 872);
 * headline block x 163–922, y 1123–1459, centred (540, 1292).
 */
export const POSTER1_TRACK: SpotKey[] = [
  // first signal — a tight beam finding the middle of "ONE WAY OUT"
  {f: 0, x: 533, y: 230, rx: 90, ry: 52, it: 0},
  {f: 5, x: 533, y: 230, rx: 110, ry: 58, it: 0.28},
  {f: 13, x: 528, y: 229, rx: 165, ry: 66, it: 0.42},
  // widened until the line reads end to end
  {f: 30, x: 533, y: 228, rx: 330, ry: 78, it: 0.74},
  {f: 46, x: 538, y: 205, rx: 345, ry: 108, it: 0.78}, // "16 × 16" caught above
  {f: 58, x: 545, y: 232, rx: 330, ry: 92, it: 0.72},
  // down into the maze — the two teal nodes, then the route itself
  {f: 74, x: 880, y: 556, rx: 165, ry: 130, it: 0.56},
  {f: 88, x: 560, y: 574, rx: 180, ry: 140, it: 0.58},
  {f: 100, x: 546, y: 700, rx: 130, ry: 165, it: 0.54},
  // 3.7 s hit — settles on the glowing node, tight and bright
  {f: 111, x: 547, y: 872, rx: 150, ry: 145, it: 0.72},
  {f: 124, x: 547, y: 878, rx: 168, ry: 158, it: 0.7},
  // sweep down onto the headline, widening as it goes
  {f: 142, x: 470, y: 1160, rx: 245, ry: 165, it: 0.64},
  {f: 158, x: 560, y: 1265, rx: 320, ry: 205, it: 0.72},
  {f: 178, x: 540, y: 1292, rx: 400, ry: 262, it: 0.88}, // headline readable, 5.9 s
  {f: 198, x: 512, y: 1310, rx: 398, ry: 258, it: 0.87},
  {f: 218, x: 558, y: 1280, rx: 404, ry: 252, it: 0.86},
];

/**
 * Poster 2 track — near-total darkness, then four beat-synchronised jumps:
 * ElecSoc logo + DUBLIN, MICROMOUSE OPEN, the outlined 2026, then
 * BUILD IT. CODE IT. RACE IT. / COMING SOON — settling into a tall soft
 * ellipse that keeps ≥30% of the poster in deep shadow.
 * Poster geometry: logo (540, 320), DUBLIN y≈580, MICROMOUSE OPEN y≈700–930,
 * 2026 y≈1000–1290, tagline block y≈1400–1640, checkerboards y<170 / y>1720.
 */
export const POSTER2_TRACK: SpotKey[] = [
  {f: 324, x: 540, y: 430, rx: 130, ry: 95, it: 0.1},
  // beat 1 — logo / DUBLIN
  {f: 325, x: 540, y: 430, rx: 140, ry: 100, it: 0.16},
  {f: 330, x: 540, y: 430, rx: 300, ry: 245, it: 0.7},
  {f: 349, x: 549, y: 442, rx: 306, ry: 250, it: 0.68},
  // beat 2 — MICROMOUSE OPEN (wide enough that the whole wordmark reads)
  {f: 356, x: 540, y: 795, rx: 520, ry: 235, it: 0.74},
  {f: 375, x: 532, y: 806, rx: 526, ry: 239, it: 0.72},
  // beat 3 — 2026
  {f: 382, x: 540, y: 1145, rx: 465, ry: 248, it: 0.78},
  {f: 401, x: 548, y: 1152, rx: 470, ry: 252, it: 0.76},
  // beat 4 — BUILD IT. CODE IT. RACE IT. / COMING SOON
  {f: 408, x: 540, y: 1500, rx: 420, ry: 228, it: 0.8},
  {f: 427, x: 534, y: 1494, rx: 424, ry: 232, it: 0.79},
  // settle — the essential announcement readable, edges still shadowed
  {f: 442, x: 540, y: 1075, rx: 560, ry: 680, it: 0.9},
  {f: 499, x: 546, y: 1069, rx: 565, ry: 685, it: 0.89},
];

export const ASSETS = {
  poster1: 'dublin/poster1.png',
  poster2: 'dublin/poster2.png',
  turn1: 'dublin/turn1.mp4',
  turn2: 'dublin/turn2.mp4',
};
