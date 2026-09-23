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

## Two sketches

- **`i2c_scanner/`** — a minimal, standalone reachability check. Flash it first.
- **`mouse_explore/`** — the exploration program. Needs the **VL53L0X** library
  by Pololu (Arduino Library Manager → search `VL53L0X`).

Both are built for ESP32 Arduino core **3.x** (required for the C6; uses the
`ledcAttach`/`ledcWrite` PWM API).

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
- **Centred, non-crashing forward drive.** While crossing a cell it steers from
  whatever it can see: centre between two walls → hug a single wall → hold gyro
  heading when there are no side walls, plus an encoder term to keep the wheels
  matched. The front sensor stops it short of any wall ahead (`FRONT_STOP_MM`).
- **Accurate turns.** 90°/180° turns are closed-loop on the gyro heading, slowing
  down near the target, with a timeout fallback so a bad gyro can't hang it.
- **Recovery, not silence.** If forward progress stalls, it backs up a third of a
  cell and re-looks. Only after 3 honest tries does it stop — loudly.

This is a starting point tuned conservatively for reliability. Get it moving,
then raise `CRUISE_PWM` and the gains once it behaves.
