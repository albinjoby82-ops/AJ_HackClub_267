---
title: Sensors and Modules
layout: default
parent: 4. Components
nav_order: 17
---

# Sensors and Modules

Sensors convert a physical property—such as temperature, light, distance, force, motion, or pressure—into an electrical signal or digital reading.

A bare sensor may require biasing, amplification, calibration, and protection. A sensor **module** often adds support components and an easier connector, but its voltage and pinout must still be checked.

## Common output types

| Output | How it is read |
| --- | --- |
| Analogue voltage | ADC input |
| Variable resistance | Voltage divider or measurement circuit |
| Digital high/low | GPIO input |
| Pulse or frequency | Timer, interrupt, or pulse measurement |
| I²C | Shared two-wire digital bus |
| SPI | Clocked digital bus with chip select |
| UART | Serial transmit/receive |

## Before connecting

1. Identify the exact part or module.
2. Check supply and logic voltages.
3. Confirm pin order; labels such as `VCC`, `GND`, `SDA`, and `SCL` are not always arranged alike.
4. Check whether pull-up resistors are already fitted.
5. Check the expected signal range.
6. Install the correct library only if it supports the exact device.

{: .warning}
> Some “5 V compatible” modules have a regulator for power but still expose `3.3 V`-only signal pins. Read the schematic or documentation rather than relying on a shop listing.

## Calibration and testing

- Compare against a known reference.
- Record units and conversion equations.
- Test minimum and maximum expected conditions.
- Account for warm-up, drift, noise, and sampling rate.
- Reject physically impossible readings in software.

## Common problems

- Wrong I²C address
- Missing common ground
- Bus pull-ups connected to the wrong voltage
- Analogue signal outside ADC range
- Sensor mounted where it measures heat, vibration, or light from the project itself
- Library intended for a similar but different chip
