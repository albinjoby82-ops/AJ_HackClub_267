/*
 * ============================================================================
 *  maze.h  -  portable maze map + flood fill  (the "brain", no hardware)
 * ============================================================================
 *
 *  This is the part of a micromouse that everyone agrees on and that you can
 *  test WITHOUT a robot: a grid of cells, the walls you've discovered, and a
 *  flood fill that turns "where are the walls" into "which way is the goal".
 *
 *  It has zero Arduino / hardware dependencies on purpose, so the exact same
 *  file is compiled by:
 *    - the robot sketch      (firmware/mouse_map/mouse_map.ino), and
 *    - the desktop simulator  (firmware/sim/maze_sim.cpp)
 *  The simulator proves the mapping logic reaches the goal on real maze layouts
 *  before you ever risk it on hardware. If mapping fails on the mouse but passes
 *  in the sim, the bug is in motion/sensing, not here.
 *
 *  FLOOD FILL in one paragraph: give every cell a number = how many cell-steps
 *  it is from the goal, only stepping between cells with no wall between them.
 *  The goal is 0. To get to the goal from anywhere, always step to the
 *  neighbour with the smallest number. Unknown walls are assumed OPEN, so the
 *  mouse optimistically heads for the goal, discovers real walls as it goes,
 *  re-floods, and tries again - which is exactly what maps the maze.
 *
 *  Conventions:
 *    x = column, 0..W-1, EAST is +x.   y = row, 0..H-1, NORTH is +y.
 *    Directions N=0, E=1, S=2, W=3.    Walls stored per cell as a 4-bit mask.
 *    A wall is always written on BOTH cells that share it (symmetric), so the
 *    map can never disagree with itself.
 * ============================================================================
 */
#ifndef MICROMOUSE_MAZE_H
#define MICROMOUSE_MAZE_H

#include <stdint.h>

// Directions and the step they represent.
enum { DIR_N = 0, DIR_E = 1, DIR_S = 2, DIR_W = 3 };
static const int8_t  DIR_DX[4]   = {  0, +1,  0, -1 };
static const int8_t  DIR_DY[4]   = { +1,  0, -1,  0 };
static const uint8_t WALL_BIT[4] = {  1,  2,  4,  8 };

inline int dirOpposite(int d) { return (d + 2) & 3; }
inline int dirLeft(int d)     { return (d + 3) & 3; }   // 90 deg CCW
inline int dirRight(int d)    { return (d + 1) & 3; }   // 90 deg CW

// Turn cost from one heading to another: 0 straight, 1 a quarter turn, 2 about.
inline int turnCost(int from, int to) {
  int diff = (to - from) & 3;
  if (diff == 0) return 0;
  if (diff == 2) return 2;
  return 1;
}

template <uint8_t MAXW = 16, uint8_t MAXH = 16>
class Maze {
public:
  uint8_t  W = MAXW, H = MAXH;
  uint8_t  walls[MAXW][MAXH];     // discovered walls, 4-bit mask per cell
  uint16_t dist[MAXW][MAXH];      // flood-fill distance to nearest goal
  uint8_t  goalX[4], goalY[4], nGoals = 0;

  // Reset to an empty maze of size w x h: no interior walls known yet, just the
  // outer border, and the goal set to the centre.
  void begin(uint8_t w, uint8_t h) {
    W = w; H = h;
    for (uint8_t x = 0; x < W; x++)
      for (uint8_t y = 0; y < H; y++) { walls[x][y] = 0; dist[x][y] = 0xFFFF; }
    for (uint8_t x = 0; x < W; x++) { setWall(x, 0, DIR_S); setWall(x, H - 1, DIR_N); }
    for (uint8_t y = 0; y < H; y++) { setWall(0, y, DIR_W); setWall(W - 1, y, DIR_E); }
    setGoalCenter();
  }

  bool inBounds(int x, int y) const { return x >= 0 && x < W && y >= 0 && y < H; }

  // Record a wall on side d of (x,y) AND the matching side of its neighbour.
  void setWall(int x, int y, int d) {
    if (!inBounds(x, y)) return;
    walls[x][y] |= WALL_BIT[d];
    int nx = x + DIR_DX[d], ny = y + DIR_DY[d];
    if (inBounds(nx, ny)) walls[nx][ny] |= WALL_BIT[dirOpposite(d)];
  }

  // Out-of-bounds counts as walled so the border is always solid.
  bool hasWall(int x, int y, int d) const {
    if (!inBounds(x, y)) return true;
    return (walls[x][y] & WALL_BIT[d]) != 0;
  }

  // --- Goal handling ------------------------------------------------------
  void clearGoals() { nGoals = 0; }
  void addGoal(uint8_t x, uint8_t y) {
    if (nGoals < 4) { goalX[nGoals] = x; goalY[nGoals] = y; nGoals++; }
  }
  // Standard micromouse goal: the centre 2x2 block (single cell if odd-sized).
  void setGoalCenter() {
    nGoals = 0;
    uint8_t cx = W / 2, cy = H / 2;
    if ((W & 1) == 0 && (H & 1) == 0) {
      addGoal(cx - 1, cy - 1); addGoal(cx, cy - 1);
      addGoal(cx - 1, cy);     addGoal(cx, cy);
    } else {
      addGoal(cx, cy);
    }
  }
  bool isGoal(int x, int y) const {
    for (uint8_t i = 0; i < nGoals; i++)
      if (goalX[i] == x && goalY[i] == y) return true;
    return false;
  }

  // --- The flood fill -----------------------------------------------------
  // BFS outward from the goal cells across edges with no known wall. After this
  // runs, dist[x][y] is the shortest number of cells from (x,y) to the goal
  // given everything discovered so far (unknown edges treated as open).
  void flood() {
    for (uint8_t x = 0; x < W; x++)
      for (uint8_t y = 0; y < H; y++) dist[x][y] = 0xFFFF;

    // A simple ring buffer queue. Coords fit in a byte (maze <= 16), and these
    // are static so the ESP32 keeps them off the stack.
    static uint8_t qx[MAXW * MAXH], qy[MAXW * MAXH];
    int head = 0, tail = 0;

    for (uint8_t i = 0; i < nGoals; i++) {
      dist[goalX[i]][goalY[i]] = 0;
      qx[tail] = goalX[i]; qy[tail] = goalY[i]; tail++;
    }
    while (head < tail) {
      int x = qx[head], y = qy[head]; head++;
      uint16_t nd = dist[x][y] + 1;
      for (int d = 0; d < 4; d++) {
        if (hasWall(x, y, d)) continue;
        int nx = x + DIR_DX[d], ny = y + DIR_DY[d];
        if (!inBounds(nx, ny)) continue;
        if (nd < dist[nx][ny]) {
          dist[nx][ny] = nd;
          qx[tail] = nx; qy[tail] = ny; tail++;
        }
      }
    }
  }

  // Pick the next direction to step from (x,y): the open neighbour with the
  // lowest flood value. Ties are broken to turn as little as possible (fewer
  // turns = less error and less time). Returns -1 if boxed in (no open, known
  // neighbour) - which in a solvable maze only happens once you're on the goal.
  int bestDir(int x, int y, int heading) const {
    int best = -1; uint16_t bestDist = 0xFFFF; int bestTurn = 99;
    for (int d = 0; d < 4; d++) {
      if (hasWall(x, y, d)) continue;
      int nx = x + DIR_DX[d], ny = y + DIR_DY[d];
      if (!inBounds(nx, ny)) continue;
      uint16_t nd = dist[nx][ny];
      if (nd == 0xFFFF) continue;
      int t = turnCost(heading, d);
      if (nd < bestDist || (nd == bestDist && t < bestTurn)) {
        bestDist = nd; bestTurn = t; best = d;
      }
    }
    return best;
  }
};

#endif // MICROMOUSE_MAZE_H
