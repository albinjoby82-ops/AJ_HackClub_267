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
 * the ElecSoc logo, the "ONE CONTACT DETECTED" kicker with IT KNOWS THE WAY
 * OUT under it, the radar crosshair and its orange contact, then DUBLIN
 * MICROMOUSE OPEN / 2026 · COMING SOON — settling into a tall soft ellipse
 * that keeps the poster's edges in deep shadow.
 *
 * Poster geometry (1080×1920): ElecSoc logo (540, 168) spanning x 410–655;
 * "ONE CONTACT DETECTED" (540, 418); headline lines y≈545 / 672 / 805, block
 * x 250–840; radar rings centred (540, 1140) with the orange contact dot on
 * the crosshair; "DUBLIN MICROMOUSE OPEN" y≈1655 spanning x 100–985;
 * "2026 · COMING SOON" y≈1745.
 */
export const POSTER2_TRACK: SpotKey[] = [
  {f: 324, x: 540, y: 170, rx: 120, ry: 88, it: 0.1},
  // beat 1 — ElecSoc logo
  {f: 325, x: 540, y: 170, rx: 130, ry: 94, it: 0.16},
  {f: 330, x: 540, y: 168, rx: 215, ry: 130, it: 0.7},
  {f: 349, x: 547, y: 174, rx: 220, ry: 134, it: 0.68},
  // beat 2 — the kicker and the headline together, wide enough that
  // "IT KNOWS THE WAY OUT" reads as one block
  {f: 356, x: 540, y: 655, rx: 410, ry: 275, it: 0.76},
  {f: 375, x: 532, y: 664, rx: 416, ry: 279, it: 0.74},
  // beat 3 — the radar contact
  {f: 382, x: 540, y: 1140, rx: 300, ry: 285, it: 0.8},
  {f: 401, x: 548, y: 1146, rx: 305, ry: 290, it: 0.78},
  // beat 4 — DUBLIN MICROMOUSE OPEN / 2026 · COMING SOON
  {f: 408, x: 540, y: 1690, rx: 500, ry: 150, it: 0.82},
  {f: 427, x: 534, y: 1684, rx: 505, ry: 154, it: 0.81},
  // settle — centred low enough that the headline, the radar and the
  // "DUBLIN MICROMOUSE OPEN" line all sit inside the beam's clear zone rather
  // than its feathered edge; the logo stays in shadow at the top.
  // "DUBLIN MICROMOUSE OPEN" is nearly full-bleed (x 100–985), so the beam has
  // to be wide as well as tall or its outer letters sit in the feather.
  {f: 442, x: 540, y: 1170, rx: 720, ry: 840, it: 0.9},
  {f: 499, x: 546, y: 1164, rx: 725, ry: 845, it: 0.89},
];

export const ASSETS = {
  poster1: 'dublin/poster1.png',
  poster2: 'dublin/poster2.png',
  turn1: 'dublin/turn1.mp4',
  turn2: 'dublin/turn2.mp4',
};
