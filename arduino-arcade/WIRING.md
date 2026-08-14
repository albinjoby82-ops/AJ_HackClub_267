# WIRING - Arduino Arcade controller

One breadboard. Six inputs. The same wiring works for all four games.

**Bill of materials:** Arduino Uno (or compatible), breadboard, 4 push buttons,
2 potentiometers (~10 kΩ, the exact value is not critical), jumper wires, USB cable.

No resistors are needed. The buttons use the Arduino's internal pull-ups.

---

## The six pins

| Arduino pin | Connects to | Notes |
|---|---|---|
| **D2** | Button 1 → GND | pressed = LOW |
| **D3** | Button 2 → GND | pressed = LOW |
| **D4** | Button 3 → GND | pressed = LOW |
| **D5** | Button 4 → GND | pressed = LOW |
| **A0** | Pot 1 wiper (centre pin) | 0–1023 |
| **A1** | Pot 2 wiper (centre pin) | 0–1023 |
| 5V | breadboard **+** rail | feeds both pots |
| GND | breadboard **−** rail | feeds both pots and all buttons |

---

## Diagram

```text
                      ARDUINO UNO
        +-------------------------------------+
        |                                     |
        |  5V  ---------------------------------------> + rail (red)
        |  GND ---------------------------------------> - rail (blue)
        |                                     |
        |  D2 ----------------------------+   |
        |  D3 --------------------------+ |   |
        |  D4 ------------------------+ | |   |
        |  D5 ----------------------+ | | |   |
        |                           | | | |   |
        |  A0 --------------+       | | | |   |
        |  A1 ------------+ |       | | | |   |
        +-----------------|-|-------|-|-|-|---+
                          | |       | | | |
                          | |       | | | |
   BUTTONS (any orientation that bridges the gap in the breadboard):

        D2 -----[ BUTTON 1 ]----- GND
        D3 -----[ BUTTON 2 ]----- GND
        D4 -----[ BUTTON 3 ]----- GND
        D5 -----[ BUTTON 4 ]----- GND

   POTENTIOMETER 1                POTENTIOMETER 2

        5V  --- outer pin              5V  --- outer pin
        A0  --- centre / wiper         A1  --- centre / wiper
        GND --- outer pin              GND --- outer pin
```

### Potentiometer detail

```text
        +5V
         |
        [ ]  outer pin 1
         |
        (o)---- wiper (centre pin) ----> A0  (or A1)
         |
        [ ]  outer pin 3
         |
        GND
```

**Swapping the two outer pins simply reverses the direction of the knob.**
It cannot damage anything. If a knob turns the wrong way you can either swap the
two outer wires, or leave the wiring alone and tick *invert* on the Calibration
screen (`[B3]` for pot 1, `[B4]` for pot 2).

### Button detail

A typical 4-pin tactile switch connects its pins in pairs. Straddle the centre
channel of the breadboard and use pins on **opposite** corners:

```text
        D2 ----o  o---- (internally joined to the pin below)
                 |
        GND ---o  o
```

If a button seems permanently pressed, you have probably used two pins that are
already joined internally - rotate the switch 90°.

---

## Layout that fits on one half-size breadboard

```text
    +-------------------------------------------------------------+
    |  +  - - - - - - - - - - - - - - - - - - - - - - - - - - -   |  <- 5V rail
    |  -  - - - - - - - - - - - - - - - - - - - - - - - - - - -   |  <- GND rail
    |                                                             |
    |   [POT 1]        [POT 2]                                    |
    |    | | |          | | |                                     |
    |    5V A0 GND      5V A1 GND                                 |
    |                                                             |
    |   [BTN1]  [BTN2]  [BTN3]  [BTN4]                            |
    |    D2      D3      D4      D5    (other leg of each -> GND) |
    +-------------------------------------------------------------+
```

Put the two pots on the left where a player's hands naturally fall, and the four
buttons in a row on the right. Twin Pong is much more fun if pot 1 and pot 2 are
far enough apart for two people to grab one each.

---

## Verify the wiring in 30 seconds

1. Upload `arduino/arcade_controller/arcade_controller.ino`.
2. Close the Arduino IDE Serial Monitor.
3. Start the arcade and open **CONTROLLER TEST**.
4. Turn each knob: its bar should sweep smoothly from 0 to ~1023.
5. Press each button: its dot should light up, and the press counter increments.

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Button shows **always pressed** | The two wires are on pins that are internally joined, or the pin is wired to 5V instead of GND | Rotate the switch 90°; make sure one leg goes to **GND**, not 5V |
| Button **never responds** | Wrong digital pin, loose leg, or the switch straddles the breadboard channel incorrectly | Check D2–D5 in order; push the switch fully in; test that leg with another button |
| Pot **stuck at 0** | Wiper on the wrong pin, or the 5V outer pin is not connected | The **centre** pin goes to A0/A1; check the + rail actually reaches the pot |
| Pot **stuck at 1023** | GND outer pin not connected | Check the − rail wire on the pot's other outer pin |
| Pot **jumps around** while untouched | Floating wiper - one outer pin is loose | Reseat both outer pins; a little jitter is normal and is filtered in software |
| Pot **direction reversed** | Outer pins swapped (harmless) | Swap the two outer wires, or use *invert* in Calibration |
| Pot only uses **part of the range** | Cheap pot, or calibration recorded a short sweep | Run **CALIBRATION** and turn both knobs fully in both directions |
| **No serial port listed** | Driver missing (common with CH340 clones), or a charge-only USB cable | Install the CH340 driver; try another USB cable/port |
| **Access denied / port busy** on the COM port | The Arduino IDE Serial Monitor (or another program) already owns the port | Close the Serial Monitor, then reconnect from **SETTINGS → SELECT ARDUINO** |
| Arduino **reconnects repeatedly** | Marginal USB cable, unpowered hub, or a short on the breadboard | Use a different cable, plug directly into the laptop, check for touching wires |
| Everything works but games ignore the knobs | Calibration recorded a tiny range | Re-run **CALIBRATION** from Settings |

If nothing helps, you can always keep the workshop moving: press **K** or pick
**PLAY WITHOUT ARDUINO** and play on the keyboard.
