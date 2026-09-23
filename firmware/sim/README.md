# Maze mapping simulator

Tests the flood-fill mapping **brain** (`../mouse_map/maze.h`) with no hardware,
the way every micromouse guide recommends: the algorithm is small and provable
in a simulator, so if the real mouse fails to map, you know the bug is in
motion/sensing, not the algorithm.

It compiles the *exact same* `maze.h` the robot runs.

## Build and run

```sh
cd firmware/sim
g++ -std=c++17 -O2 -Wall maze_sim.cpp -o maze_sim
./maze_sim
```

## What it does

1. Prints one reproducible maze, runs the flood-fill explorer on it, and shows
   the map the (perfect-motion) virtual mouse discovered on the way to the goal.
2. Runs a batch of random braided 16×16 mazes and reports:
   - **Flood fill** — should reach the goal on **100%** of them.
   - **Right-hand wall follower** — reaches a *central* goal only a fraction of
     the time, which is the concrete reason real mice map with flood fill.
3. Exits non-zero if flood fill ever fails to reach a solvable goal, so it can
   be wired into CI.

Typical output: flood fill 100%, wall follower ~20%. That 100% is your evidence
that the mapping logic is correct before you trust it to the motors.
