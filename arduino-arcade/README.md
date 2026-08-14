# ARDUINO ARCADE

Four neon arcade games on your laptop, played with a physical Arduino
controller: **4 buttons + 2 potentiometers on one breadboard**.

| | Game | What it is |
|---|---|---|
| 1 | **NEON DRIFT** | Endless pseudo-3D neon highway racer. Steer, throttle, boost, chase near-miss combos. |
| 2 | **ORBITAL DEFENDER** | Slide a turret around a space station, aim, fire, shield, missiles, EMP, waves and heavy drones. |
| 3 | **REACTOR SYNC** | Twist both knobs to hold two reactor channels in their moving safe zones while alarms demand buttons. |
| 4 | **TWIN PONG** | Genuine two-player pong with blasts, power-ups and rally escalation - one player per knob. |

The Arduino is *only* a controller: it streams the state of the six inputs over
USB serial and the laptop runs the games.

**No Arduino yet? Everything runs on the keyboard.** Nothing here needs
hardware to start.

---

## Quick start (Windows)

```bat
setup.bat
```

then

```bat
run_arcade.bat
```

`setup.bat` checks Python, creates `.venv`, installs `pygame` + `pyserial` +
`pytest` and tells you what to do next. `run_arcade.bat` starts the arcade.

**Play without an Arduino:**

```bat
run_arcade.bat --keyboard
```

…or just pick **PLAY WITHOUT ARDUINO** on the device screen / press **K** at any time.

### PowerShell (no .bat files)

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

Requires **Python 3.9+** (3.11+ recommended).

---

## Uploading the Arduino firmware

1. Open the **Arduino IDE**.
2. Plug the Arduino into the laptop with the USB cable.
3. Open `arduino/arcade_controller/arcade_controller.ino`.
4. **Tools → Board →** *Arduino Uno* (or your compatible board).
5. **Tools → Port →** the COM port that appeared when you plugged the board in.
6. Click **Upload** and wait for "Done uploading".
7. **Close the Serial Monitor.** ← this step matters, see below.
8. Run Arduino Arcade.

> ### Why the Serial Monitor must be closed
> A COM port can only be opened by one program at a time. If the Arduino IDE's
> Serial Monitor still has the port open, Python cannot open it and you get
> *"Access is denied"* or *"could not open port"*. Close the Serial Monitor (or
> the whole IDE) and the arcade will connect on its next retry - no restart needed.

You only need to upload the firmware **once**. It stays on the board.

---

## Wiring

Full diagram, breadboard layout and a troubleshooting table: **[WIRING.md](WIRING.md)**.

```text
D2 -> Button 1 -> GND        A0 -> Pot 1 wiper
D3 -> Button 2 -> GND        A1 -> Pot 2 wiper
D4 -> Button 3 -> GND        Pot outer pins -> 5V and GND
D5 -> Button 4 -> GND        (buttons use INPUT_PULLUP - no resistors)
```

Open **CONTROLLER TEST** in the launcher to check every input live.

---

## Controls

Menus: **POT 1** moves, **B1** selects, **B2** backs out, **B3** switches row,
**B4** jumps to Controller Test. Mouse and keyboard work everywhere too.

| | NEON DRIFT | ORBITAL DEFENDER | REACTOR SYNC | TWIN PONG |
|---|---|---|---|---|
| **POT 1** | Steer | Orbit position | Tune channel A | P1 paddle |
| **POT 2** | Throttle | Aim angle | Tune channel B | P2 paddle |
| **B1** | Boost | Fire | Lock channel A | P1 blast |
| **B2** | Drift / brake | Shield | Vent coolant | P1 serve |
| **B3** | Use power-up | Missile | Lock channel B | P2 blast |
| **B4** | Recentre | EMP | Discharge core | P2 serve |

### Keyboard equivalents

| Control | Keys |
|---|---|
| Pot 1 | **A** / **D** (also S / W) |
| Pot 2 | **←** / **→** (also ↓ / ↑) |
| Buttons 1–4 | **1 2 3 4** (B1 = Space, B2 = Shift) |
| Menus | arrows, Enter, Space, Escape, mouse |

Analog keys ramp smoothly, so keyboard play feels like turning a knob rather
than flipping a switch.

### Global keys

| Key | Action |
|---|---|
| **F3** | Developer overlay (FPS, port, raw + normalised pots, buttons, scene) |
| **F11** | Toggle fullscreen |
| **Ctrl+M** | Mute / unmute |
| **K** | Switch to keyboard mode (when the controller is missing) |
| **Esc** | Back / pause |
| **P** | Pause |

---

## Command line

```bash
python main.py                      # auto-detect the Arduino, else keyboard
python main.py --keyboard           # no hardware at all
python main.py --event              # fullscreen Event Mode for a stall/booth
python main.py --port COM5          # force a serial port
python main.py --game twin_pong     # jump straight into a game
python main.py --size 1600x900      # window size
python main.py --no-audio           # silent
python main.py --list-ports         # print detected serial ports and exit
```

### Event Mode

`--event` starts fullscreen, hides the developer-facing menu entries, keeps the
connection indicator prominent, and bounces back to the launcher after ~75 s of
inactivity so the next student always finds a clean menu. High scores persist
between players.

---

## First run with real hardware

1. Upload the firmware, close the Serial Monitor, start the arcade.
2. If exactly one likely Arduino port is found it connects automatically;
   if several are found you get a device-selection screen.
3. On first connection you are taken to **CALIBRATION**: turn both knobs fully
   left then fully right, press **B1**, check the direction, press **B1** to save.
   Calibration is stored and never asked for again (redo it from Settings).
4. Open **CONTROLLER TEST** to confirm all six inputs.
5. Play.

---

## Where things are saved

`%APPDATA%\ArduinoArcade\settings.json` on Windows, `~/.config/ArduinoArcade/`
elsewhere. It holds calibration, high scores, volume/mute, fullscreen and the
preferred serial port. If the file is missing or damaged the arcade starts with
defaults, tells you, and keeps going.

---

## Tests and tooling

```bash
python -m pytest -q                 # unit tests (headless, no hardware)
python scripts/smoke_test.py        # drive every screen and game with a scripted controller
python scripts/capture.py           # render screens to build/shots/*.png
```

The smoke test and the test suite both run with dummy SDL video/audio drivers,
so they work on a machine with no display and no sound card.

---

## Project layout

```text
main.py                    entry point, CLI, launcher wiring
arcade/
  controller.py            shared Controller API + packet parser
  serial_controller.py     PySerial backend (the only module importing serial)
  keyboard_controller.py   keyboard backend
  simulated_controller.py  scripted backend for tests/smoke runs
  calibration.py           pot normalisation, dead zones, invert
  settings.py              JSON persistence, high scores
  audio.py                 procedurally generated WAV sound effects
  effects.py               particles, screen shake, floating text, transitions
  ui.py                    palette, fonts, glow, panels, bars
  app.py                   window, scene stack, overlays, event mode
  game.py                  BaseGame: state machine, pause, game over
  scenes/                  launcher, controller test, calibration, settings, help, device select
games/                     neon_drift, orbital_defender, reactor_sync, twin_pong
arduino/arcade_controller/ the single firmware sketch
tests/                     pytest suite
scripts/                   smoke_test.py, capture.py
```

Design notes and per-game tuning: **[GAME_DESIGN.md](GAME_DESIGN.md)**.
Repository rules for future contributors (and Claude Code): **[CLAUDE.md](CLAUDE.md)**.

---

## Serial protocol

115200 baud, one newline-terminated ASCII packet at ~80 Hz:

```text
POT1,POT2,B1,B2,B3,B4\n        e.g.  512,831,0,1,0,0
```

`POT1`/`POT2` are 0–1023; buttons are `1` when physically pressed. Malformed
lines, partial packets, boot garbage and disconnects are all tolerated - a bad
packet is counted and dropped, never crashed on.

---

## Licence / assets

All graphics are drawn at runtime with Pygame primitives and all sound effects
are synthesised locally into `assets/sounds/` on first run. No downloaded or
copyrighted assets are used. The arcade works completely offline once the Python
dependencies are installed.
