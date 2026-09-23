/*
 * ============================================================================
 *  maze_sim.cpp  -  desktop test harness for the mapping brain
 * ============================================================================
 *
 *  Runs the EXACT flood-fill code the robot uses (../mouse_map/maze.h) against
 *  generated mazes, with a perfect "virtual mouse" (no motion or sensor error),
 *  and checks that it maps its way to the goal every time. This is the standard
 *  micromouse advice made real: the algorithm can be proven with no hardware,
 *  so any first-time-mapping failure on the robot is a motion/sensing problem,
 *  not an algorithm problem.
 *
 *  It also runs a right-hand wall follower on the same mazes so you can see, in
 *  numbers, why real mice use flood fill: a wall follower is not guaranteed to
 *  reach a central goal once the maze has loops, flood fill always is.
 *
 *  Build & run (no dependencies):
 *      cd firmware/sim
 *      g++ -std=c++17 -O2 -Wall maze_sim.cpp -o maze_sim
 *      ./maze_sim
 * ============================================================================
 */
#include "../mouse_map/maze.h"

#include <cstdio>
#include <cstdint>
#include <random>
#include <vector>

static const int W = 16, H = 16;

// ---- Ground-truth maze (what really exists; the mouse must discover it) ----
struct TrueMaze {
  bool wall[16][16][4];   // wall[x][y][dir] present?

  bool has(int x, int y, int d) const {
    if (x < 0 || x >= W || y < 0 || y >= H) return true;   // border solid
    return wall[x][y][d];
  }
  void removeWall(int x, int y, int d) {
    wall[x][y][d] = false;
    int nx = x + DIR_DX[d], ny = y + DIR_DY[d];
    if (nx >= 0 && nx < W && ny >= 0 && ny < H) wall[nx][ny][dirOpposite(d)] = false;
  }

  // Recursive-backtracker perfect maze, then braided (extra walls removed to
  // create loops), then the centre 2x2 opened into a room - like a real maze.
  void generate(std::mt19937 &rng) {
    for (int x = 0; x < W; x++)
      for (int y = 0; y < H; y++)
        for (int d = 0; d < 4; d++) wall[x][y][d] = true;

    bool visited[16][16] = {{false}};
    std::vector<std::pair<int,int>> stack;
    stack.push_back({0, 0});
    visited[0][0] = true;
    while (!stack.empty()) {
      auto [x, y] = stack.back();
      int order[4] = {0, 1, 2, 3};
      for (int i = 3; i > 0; i--) { int j = rng() % (i + 1); std::swap(order[i], order[j]); }
      bool advanced = false;
      for (int i = 0; i < 4; i++) {
        int d = order[i];
        int nx = x + DIR_DX[d], ny = y + DIR_DY[d];
        if (nx < 0 || nx >= W || ny < 0 || ny >= H || visited[nx][ny]) continue;
        removeWall(x, y, d);
        visited[nx][ny] = true;
        stack.push_back({nx, ny});
        advanced = true;
        break;
      }
      if (!advanced) stack.pop_back();
    }

    // Braid: knock out ~15% of remaining interior walls to make loops.
    std::uniform_real_distribution<double> u(0.0, 1.0);
    for (int x = 0; x < W; x++)
      for (int y = 0; y < H; y++)
        for (int d = 0; d < 2; d++) {          // N and E only, avoids double work
          int nx = x + DIR_DX[d], ny = y + DIR_DY[d];
          if (nx < 0 || nx >= W || ny < 0 || ny >= H) continue;
          if (wall[x][y][d] && u(rng) < 0.15) removeWall(x, y, d);
        }

    // Open the centre 2x2 into a room (walls between the four centre cells).
    int cx = W / 2, cy = H / 2;             // cells (cx-1,cy-1)..(cx,cy)
    removeWall(cx - 1, cy - 1, DIR_N);
    removeWall(cx - 1, cy - 1, DIR_E);
    removeWall(cx,     cy,     DIR_S);
    removeWall(cx,     cy,     DIR_W);
  }
};

// ---- ASCII render of any "hasWall(x,y,d)" source, with a marker cell -------
template <class HasWall>
void render(HasWall hw, int mx, int my, const char *title) {
  printf("%s\n", title);
  for (int y = H - 1; y >= 0; y--) {
    // top edge of this row
    for (int x = 0; x < W; x++) printf("+%s", hw(x, y, DIR_N) ? "---" : "   ");
    printf("+\n");
    // cell row
    for (int x = 0; x < W; x++) {
      printf("%s", hw(x, y, DIR_W) ? "|" : " ");
      int cx = W / 2, cy = H / 2;
      bool goal = (x == cx - 1 || x == cx) && (y == cy - 1 || y == cy);
      if (x == mx && y == my) printf(" M ");
      else if (goal)          printf(" G ");
      else                    printf("   ");
    }
    printf("%s\n", hw(W - 1, 0, DIR_E) ? "|" : " ");
  }
  // bottom border
  for (int x = 0; x < W; x++) printf("+%s", hw(x, 0, DIR_S) ? "---" : "   ");
  printf("+\n");
}

// ---- Flood-fill explorer: returns steps to reach goal, or -1 if it failed --
int exploreFloodFill(const TrueMaze &truth, bool verbose) {
  Maze<16, 16> m;
  m.begin(W, H);

  int x = 0, y = 0, heading = DIR_N;
  const int cap = W * H * 20;
  int steps = 0;

  while (steps <= cap) {
    // Sense the three sides a real mouse can see (front, left, right). The side
    // behind was already known from the cell we came from.
    int look[3] = { heading, dirLeft(heading), dirRight(heading) };
    for (int i = 0; i < 3; i++)
      if (truth.has(x, y, look[i])) m.setWall(x, y, look[i]);

    if (m.isGoal(x, y)) {
      if (verbose) {
        auto hw = [&](int cx, int cy, int d) { return m.hasWall(cx, cy, d); };
        render(hw, x, y, "\nDiscovered map when the mouse reached the goal:");
        printf("Reached goal at (%d,%d) in %d moves.\n", x, y, steps);
      }
      return steps;
    }

    m.flood();
    int d = m.bestDir(x, y, heading);
    if (d < 0) return -1;              // boxed in (shouldn't happen if reachable)

    heading = d;                       // (robot would turn here)
    x += DIR_DX[d];
    y += DIR_DY[d];
    steps++;
  }
  return -1;                           // ran out of moves
}

// ---- Right-hand wall follower, for comparison ------------------------------
int exploreWallFollower(const TrueMaze &truth) {
  int x = 0, y = 0, heading = DIR_N;
  const int cap = W * H * 20;
  int cx = W / 2, cy = H / 2;
  for (int steps = 0; steps <= cap; steps++) {
    bool goal = (x == cx - 1 || x == cx) && (y == cy - 1 || y == cy);
    if (goal) return steps;

    int r = dirRight(heading), f = heading, l = dirLeft(heading), b = dirOpposite(heading);
    int d;
    if      (!truth.has(x, y, r)) d = r;
    else if (!truth.has(x, y, f)) d = f;
    else if (!truth.has(x, y, l)) d = l;
    else                          d = b;
    heading = d;
    x += DIR_DX[d];
    y += DIR_DY[d];
  }
  return -1;
}

int main() {
  printf("=== Micromouse mapping simulator ===\n");
  printf("Maze: %dx%d, goal = centre 2x2. Virtual mouse, perfect motion.\n\n", W, H);

  // 1) One detailed, reproducible run so you can eyeball it.
  {
    std::mt19937 rng(12345);
    TrueMaze truth;
    truth.generate(rng);
    auto ghw = [&](int x, int y, int d) { return truth.has(x, y, d); };
    render(ghw, 0, 0, "Ground-truth maze (what actually exists, M = start):");
    int steps = exploreFloodFill(truth, true);
    printf(steps >= 0 ? "\n=> FLOOD FILL MAPPED IT.\n" : "\n=> FLOOD FILL FAILED.\n");
  }

  // 2) Batch: prove flood fill maps every maze; measure the wall follower too.
  const int N = 3000;
  int ffOk = 0, wfOk = 0;
  long ffSteps = 0;
  std::mt19937 rng(2024);
  for (int i = 0; i < N; i++) {
    TrueMaze truth;
    truth.generate(rng);
    int ff = exploreFloodFill(truth, false);
    int wf = exploreWallFollower(truth);
    if (ff >= 0) { ffOk++; ffSteps += ff; }
    if (wf >= 0) { wfOk++; }
  }
  printf("\n=== %d random braided mazes ===\n", N);
  printf("Flood fill  : reached goal %d/%d  (%.1f%%),  avg %.1f moves\n",
         ffOk, N, 100.0 * ffOk / N, (double)ffSteps / (ffOk ? ffOk : 1));
  printf("Wall follower: reached goal %d/%d  (%.1f%%)\n",
         wfOk, N, 100.0 * wfOk / N);
  printf("\nTakeaway: flood fill is meant to map 100%% of solvable mazes. If the\n");
  printf("mouse fails on real hardware, the map logic is fine - look at motion\n");
  printf("and wall sensing (odometry drift, a mis-read wall).\n");

  return (ffOk == N) ? 0 : 1;   // non-zero exit if the algorithm ever failed
}
