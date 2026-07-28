/**
 * Maze generation.
 *
 * The run route is hand-authored so the choreography is fixed, then a seeded
 * DFS maze is carved around it. The result is a genuinely connected maze with
 * junctions and dead ends, but a route that never changes between runs.
 */

export const COLS = 8;
export const ROWS = 16;

/** World units. One cell is 1.0 across. */
export const CELL = 1.0;
export const WALL_T = 0.07;
export const WALL_H = 0.5;
export const POST = 0.1;

/** Authored route, in [col, row] cells. Every leg is axis-aligned. */
export const ROUTE_CELLS = [
  [3, 0],
  [3, 3],
  [6, 3],
  [6, 6],
  [2, 6],
  [2, 9],
  [5, 9],
  [5, 12],
  [1, 12],
  [1, 15],
];

/** xorshift32 — deterministic across runs and machines. */
function rng(seed) {
  let s = seed >>> 0 || 1;
  return () => {
    s ^= s << 13;
    s ^= s >>> 17;
    s ^= s << 5;
    return (s >>> 0) / 4294967296;
  };
}

const key = (c, r) => `${c},${r}`;

/**
 * Builds the wall set.
 * Walls are stored as edges between neighbouring cells plus the outer border,
 * so no wall is ever emitted twice.
 */
export function buildMaze(seed = 20260214) {
  const rand = rng(seed);

  // Start fully walled, then carve.
  const cells = [];
  for (let c = 0; c < COLS; c++) {
    cells[c] = [];
    for (let r = 0; r < ROWS; r++) cells[c][r] = { n: true, s: true, e: true, w: true, visited: false };
  }

  const opposite = { n: 's', s: 'n', e: 'w', w: 'e' };
  const delta = { n: [0, 1], s: [0, -1], e: [1, 0], w: [-1, 0] };

  const carve = (c, r, dir) => {
    const [dc, dr] = delta[dir];
    const c2 = c + dc;
    const r2 = r + dr;
    if (c2 < 0 || c2 >= COLS || r2 < 0 || r2 >= ROWS) return;
    cells[c][r][dir] = false;
    cells[c2][r2][opposite[dir]] = false;
  };

  // Iterative DFS from the route start.
  const stack = [[ROUTE_CELLS[0][0], ROUTE_CELLS[0][1]]];
  cells[stack[0][0]][stack[0][1]].visited = true;

  while (stack.length) {
    const [c, r] = stack[stack.length - 1];
    const options = Object.keys(delta).filter((dir) => {
      const [dc, dr] = delta[dir];
      const c2 = c + dc;
      const r2 = r + dr;
      return c2 >= 0 && c2 < COLS && r2 >= 0 && r2 < ROWS && !cells[c2][r2].visited;
    });

    if (!options.length) {
      stack.pop();
      continue;
    }

    const dir = options[Math.floor(rand() * options.length) % options.length];
    carve(c, r, dir);
    const [dc, dr] = delta[dir];
    cells[c + dc][r + dr].visited = true;
    stack.push([c + dc, r + dr]);
  }

  // Force the authored route open, whatever the DFS decided.
  const route = expandRoute();
  for (let i = 0; i < route.length - 1; i++) {
    const [c1, r1] = route[i];
    const [c2, r2] = route[i + 1];
    const dir = c2 > c1 ? 'e' : c2 < c1 ? 'w' : r2 > r1 ? 'n' : 's';
    carve(c1, r1, dir);
  }

  // A few extra openings so the route reads as one choice among many.
  const routeSet = new Set(route.map(([c, r]) => key(c, r)));
  for (const [c, r] of route) {
    if (rand() < 0.35) {
      const dirs = ['n', 's', 'e', 'w'].filter((d) => {
        const [dc, dr] = delta[d];
        const c2 = c + dc;
        const r2 = r + dr;
        return c2 >= 0 && c2 < COLS && r2 >= 0 && r2 < ROWS && !routeSet.has(key(c2, r2));
      });
      if (dirs.length) carve(c, r, dirs[Math.floor(rand() * dirs.length) % dirs.length]);
    }
  }

  return { cells, route, walls: collectWalls(cells) };
}

/** Expands the authored corner list into every cell along the way. */
export function expandRoute() {
  const out = [];
  for (let i = 0; i < ROUTE_CELLS.length - 1; i++) {
    const [c1, r1] = ROUTE_CELLS[i];
    const [c2, r2] = ROUTE_CELLS[i + 1];
    const dc = Math.sign(c2 - c1);
    const dr = Math.sign(r2 - r1);
    let c = c1;
    let r = r1;
    while (c !== c2 || r !== r2) {
      out.push([c, r]);
      c += dc;
      r += dr;
    }
  }
  out.push(ROUTE_CELLS[ROUTE_CELLS.length - 1]);
  return out;
}

/**
 * Flattens the cell grid into deduplicated wall segments.
 * Each segment is { x, z, horizontal } in world space.
 */
function collectWalls(cells) {
  const walls = [];
  const seen = new Set();

  const push = (x, z, horizontal) => {
    const k = `${x.toFixed(3)},${z.toFixed(3)},${horizontal}`;
    if (seen.has(k)) return;
    seen.add(k);
    walls.push({ x, z, horizontal });
  };

  for (let c = 0; c < COLS; c++) {
    for (let r = 0; r < ROWS; r++) {
      const cell = cells[c][r];
      const x = c * CELL;
      const z = r * CELL;
      // Horizontal walls run along X, separating rows.
      if (cell.n) push(x, z + CELL / 2, true);
      if (cell.s) push(x, z - CELL / 2, true);
      // Vertical walls run along Z, separating columns.
      if (cell.e) push(x + CELL / 2, z, false);
      if (cell.w) push(x - CELL / 2, z, false);
    }
  }
  return walls;
}

/** World-space centre of a cell. */
export const cellCenter = ([c, r]) => ({ x: c * CELL, z: r * CELL });
