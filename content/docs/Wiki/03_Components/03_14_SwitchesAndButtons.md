---
title: Switches and Buttons
layout: default
parent: 4. Components
nav_order: 14
---

# Switches and Buttons

Switches create or break electrical connections. A push button is momentary; many toggle and slide switches retain their position.

## Contact terminology

- **Normally open (NO):** open until activated
- **Normally closed (NC):** closed until activated
- **Common (COM):** moving contact on changeover switches
- **SPST:** one circuit, on/off
- **SPDT:** one common contact selects between two paths
- **DPDT:** two SPDT sections operated together

## Reading a button

An input needs a defined default state. Connect a button to ground and use an internal pull-up where available:

```cpp
pinMode(2, INPUT_PULLUP);
bool pressed = digitalRead(2) == LOW;
```

## Four-leg tactile buttons

On common tactile buttons, the two pins on each side are permanently connected. Pressing the button joins the two sides. Rotate it incorrectly on a breadboard and the input may be permanently shorted.

Check continuity before wiring.

## Contact bounce

Mechanical contacts can switch repeatedly for a few milliseconds when pressed or released. Handle this with:

- A short software debounce interval
- State-change timing
- An RC network
- A Schmitt-trigger input

## Ratings

Switches have voltage and current ratings. Small signal buttons are not suitable for motors, heaters, mains, or other substantial loads.

{: .warning}
> Do not interrupt an inductive load without suitable suppression. Arcing can damage switch contacts and create interference.
