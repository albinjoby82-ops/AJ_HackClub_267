# Micromouse firmware — ESP32-C6 exploration

Arduino firmware for the Dublin Micromouse Open 2026 mouse. **Exploration only**
for now: the mouse drives slowly and smoothly through the maze, stays centred
between the walls, takes sensible turns, and never crashes — and when it *does*
stop, it always prints why.

This lives here as engineering source, not as part of the website. It is
excluded from the deployed static assets (see `.assetsignore`).

## Hardware (from the event's own build guides)

| Part | What it is | Bus / address |
| --- | --- | --- |
| ESP32-C6-DevKitC-1 | Controller (3.3 V logic only) | — |
| 3× VL53L0X | Left / front / right distance (ToF) | I2C → `0x30` / `0x31` / `0x32` |
| MPU-6050 (SEN0142) | 6-axis IMU — gyro used for heading | I2C `0x68` |
| DRI0044 | Dual motor driver (DIR + PWM per wheel) | — |
| 2× GA12-N20 | Gear motors with Hall encoders (A/B) | — |

All four I2C devices share one SDA/SCL bus. The three ToF sensors power up at the
same address (`0x29`), so they are re-addressed one at a time over their XSHUT
pins at every boot.

## What's here

- **`i2c_scanner/`** — a minimal, standalone reachability check. Flash it first.
- **`motor_encoder_test/`** — bench tool to verify the motors spin the right way
  and the encoders count the right way, and to **measure `ENC_TICKS_PER_REV`**.
  Serial-driven, wheels off the table.
- **`straight_test/`** — closed-loop straight driving with live CSV telemetry.
  Each wheel runs a **speed PID** (so it actually hits the commanded speed), an
  outer loop holds heading and centres between walls, and the front sensor stops
  it before a wall. This is the sketch that makes navigation *reliable*; tune it
  here before trusting the mapper.
- **`mouse_explore/`** — the simple reactive explorer: left-hand-rule wall
  following with centred, non-crashing driving. Good for a first "does it move
  without hitting walls" test. Does **not** build a map.
- **`mouse_map/`** — the real deal: keeps a wall map and runs **flood fill** to
  map a route to the centre on the first run. Shares its mapping brain
  (`maze.h`) with the simulator. Uses self-correcting odometry so the map stays
  honest. This is the one that "maps the maze."
- **`sim/`** — a desktop simulator that compiles the same `maze.h` and proves
  the mapping reaches the goal on 100% of solvable mazes, no hardware needed.
  See `sim/README.md`.

The sketches need the **VL53L0X** library by Pololu (Arduino Library Manager →
search `VL53L0X`) and ESP32 Arduino core **3.x** (required for the C6; uses the
`ledcAttach`/`ledcWrite` PWM API).

## Mapping: how it actually maps the maze first time

A plain wall-follower **cannot** guarantee finding the centre of a competition
maze — the centre is effectively an island. The standard, proven answer is
**flood fill**: number every cell by its distance to the goal (only stepping
where there's no wall), then always move to the lowest-numbered neighbour.
Unknown walls are assumed open, so the mouse optimistically heads for the goal,
discovers real walls, re-floods, and repeats — which is exactly what maps it.

The widely-repeated micromouse truth: the flood-fill algorithm is small and can
be **fully tested in a simulator with no hardware**; the hard part is that
*wall detection has no partial credit* — one wrong wall corrupts the map — and
after ~10 cells the mouse no longer knows exactly where it is unless you fight
odometry drift. So `mouse_map` pins all three degrees of freedom against the
walls every cell:

- **Heading** — gyro closed-loop turns, angle reset each move, so every cell
  re-squares to the cardinal direction.
- **Sideways** — centre between the side walls while crossing each cell.
- **Forward** — stop a fixed distance from a wall ahead (front ToF), pinning how
  far along the cell you are.

And it only reads walls while stopped and squared up, writing each wall to both
cells that share it so the map can't contradict itself.

Prove the brain before trusting the motors:

```sh
cd sim && g++ -std=c++17 -O2 -Wall maze_sim.cpp -o maze_sim && ./maze_sim
```

## Reliable driving is built bottom-up (do not skip a layer)

Navigation that never hits a wall or gets stuck is not one clever program — it's
four layers, each verified on the bench before the next. This is the order that
actually works, and each bench sketch produces the numbers the next layer needs:

1. **Electrics** (`motor_encoder_test`) — forward drives each wheel forward, each
   encoder counts up, and you've measured `ENC_TICKS_PER_REV`. Nothing above
   this can work until it does.
2. **Wheel speed** (`straight_test`, steering off) — each wheel hits its
   commanded speed via its own PID. Two cheap motors differ, so *without this
   the mouse curves before any wall pushes it*. This is the layer most DIY mice
   skip and then fight forever.
3. **Straight + centred** (`straight_test`, steering on) — gyro holds heading and
   the side walls trim it to the middle of the corridor.
4. **Don't hit anything** — the front ToF cuts speed to zero before contact.

Only once all four hold on the bench do `mouse_explore` / `mouse_map` become
reliable — they sit *on top* of exactly these layers.

## Run order — do not skip step 1

1. **Flash `i2c_scanner`.** Open Serial at **115200**. Every device must print
   `FOUND`. Any `MISSING` line names the sensor and the wires to check (XSHUT,
   SDA/SCL, VIN, GND) for *that* device. Fix wiring until all 4 are `FOUND`.
2. **Flash `mouse_explore`** with the **wheels off the table**. Watch Serial:
   each sensor prints `... initialized OK`, the IMU prints `initialized OK`, then
   the gyro bias line. If a sensor fails to come up, it halts loudly and says
   which one — it never limps on silently.
3. **Put it in the maze and let it explore.** Every stop prints a reason. If it
   ever gives up, it prints
   `STOP: gave up after 3 recovery attempts. Reposition and RESET.` and blinks
   the status LED — it does not freeze silently.

## Set these before you drive (top of `mouse_explore.ino`)

- **Pins** — every `PIN_*` and `XSHUT[]` value to match your wiring. Avoid the
  ESP32-C6 strapping pins (GPIO 4, 5, 8, 9, 15) and the USB pins (GPIO 12, 13).
- **Geometry** — `WHEEL_DIAMETER_MM` and `ENC_TICKS_PER_REV`. **Measure these**
  (guide H6): roll the wheel one turn by hand and count ticks. They set
  `TICKS_PER_CELL`, which is how the mouse knows one 180 mm cell.
- **Wall thresholds** — `SIDE_WALL_NEAR/FAR_MM`, `FRONT_WALL_MM`, `FRONT_STOP_MM`.
  Tune on the **real maze walls in the real room** (guide H4). They use
  hysteresis so a wall doesn't flicker in and out near the threshold.
- **Signs** — if a wheel spins the wrong way, flip `L_DIR_SIGN` / `R_DIR_SIGN`.
  If left turns read negative on the gyro, flip `GYRO_SIGN`.

## How exploration works (kept light on purpose)

- **Left-hand rule.** Each step the mouse turns left if the left is open, else
  goes straight, else turns right, else turns around — then advances one cell.
  There is always a legal move, so it keeps exploring instead of giving up.
- **Centred, non-crashing forward drive.** Straightness comes first, so the
  mouse stays *parallel* to the corridor instead of weaving into a wall at an
  angle. Every iteration it sums: (1) a gyro heading-hold with rate damping,
  (2) a wheel-match term keeping left/right ticks equal, and (3) a gentle wall
  centring trim that is applied *only* when a side wall is close enough to trust
  (`WALL_TRUST_MM`) — so a wall that ends can't yank the steering. The front
  sensor stops it short of any wall ahead (`FRONT_STOP_MM`). This mirrors how the
  reference mouse drives: heading first, walls as a trim.
- **Accurate turns.** 90°/180° turns are closed-loop on the gyro heading, slowing
  down near the target, with a timeout fallback so a bad gyro can't hang it.
- **Recovery, not silence.** If forward progress stalls, it backs up a third of a
  cell and re-looks. Only after 3 honest tries does it stop — loudly.

This is a starting point tuned conservatively for reliability. Get it moving,
then raise `CRUISE_PWM` and the gains once it behaves.
