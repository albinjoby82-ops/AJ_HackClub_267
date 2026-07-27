---
title: Sensors and Modules
layout: default
parent: 4. Components
nav_order: 17
---

# Sensors and Modules

Sensors convert temperature, light, distance, force, motion or another physical property into an electrical signal or digital reading.

A bare sensor may require extra components and calibration. A module often adds those parts and an easier connector, but its voltage and pinout still need checking.

## Common sensor types

| Sensor | Typical use | Typical output |
| --- | --- | --- |
| Photoresistor | Light level | Variable resistance |
| Potentiometer | Position or user control | Analogue voltage |
| Thermistor | Temperature | Variable resistance |
| Hall sensor | Magnet or current detection | Analogue or digital |
| Ultrasonic module | Distance | Timed pulse |
| IMU | Acceleration and rotation | I²C or SPI |
| Digital temperature sensor | Temperature | One-wire, I²C or SPI |

## Output interfaces

| Output | How it is read |
| --- | --- |
| Analogue voltage | ADC input |
| Variable resistance | Voltage divider |
| Digital HIGH/LOW | GPIO input |
| Pulse or frequency | Timer or pulse measurement |
| I²C | Shared clock and data bus |
| SPI | Clocked bus with chip select |
| UART | Serial transmit and receive |

## Before connecting

1. Identify the exact sensor or module.
2. Check supply and logic voltage.
3. Confirm pin order.
4. Check whether pull-up resistors are already fitted.
5. Check the expected signal range.
6. Check whether the library supports the exact chip.

{: .warning}
> A module advertised as “5 V compatible” may have a regulator for its supply while still exposing `3.3 V`-only signal pins.

## Calibration

Calibration converts a raw reading into a useful estimate.

1. Compare the sensor against known conditions or a reference instrument.
2. Record several points across the useful range.
3. Fit or choose an appropriate conversion.
4. Test conditions not used to create the conversion.
5. Record units and expected uncertainty.

## Sampling and filtering

- Sample fast enough to capture meaningful change.
- Avoid sampling so fast that repeated noise dominates.
- Average or filter noisy readings when response delay is acceptable.
- Reject impossible values and report sensor faults.
- Keep sensor wiring away from motors and other noisy loads.

## Mounting matters

A perfectly coded sensor can still measure the wrong thing. Avoid heat from regulators, shadows from the enclosure, vibration from motors and blocked airflow.

## Common problems

- Wrong I²C address
- Missing common ground
- Pull-ups connected to the wrong voltage
- Analogue output outside ADC range
- Similar-looking but different chip
- Incorrect units or conversion
- Self-heating or poor mounting
