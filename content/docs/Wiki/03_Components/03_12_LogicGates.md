---
title: Logic Gates and Digital ICs
layout: default
parent: 4. Components
nav_order: 12
---

# Logic Gates and Digital ICs

Logic gates process digital high and low signals. Common functions include NOT, AND, OR, NAND, NOR, XOR, and XNOR.

## Truth tables

| A | B | AND | OR | XOR |
| --- | --- | --- | --- | --- |
| 0 | 0 | 0 | 0 | 0 |
| 0 | 1 | 0 | 1 | 1 |
| 1 | 0 | 0 | 1 | 1 |
| 1 | 1 | 1 | 1 | 0 |

A NOT gate outputs the opposite of its input.

## IC families

Part numbers often identify the family and function, such as `74HC00` for four NAND gates. Families differ in supply voltage, input thresholds, speed, and output drive.

Do not assume a `5 V` logic output is safe for a `3.3 V` input, or that a `3.3 V` output meets every `5 V` family's high threshold.

## Using a DIP logic IC

1. Disconnect power.
2. Place the chip across the breadboard centre gap.
3. Find pin 1 from the notch or dot.
4. Check the datasheet pinout.
5. Connect power and ground.
6. Add a `100 nF` decoupling capacitor close to the supply pins.
7. Give every input a defined high or low state.
8. Connect outputs only to suitable loads.

{: .warning}
> Never leave CMOS logic inputs floating. A floating input can switch unpredictably and increase current consumption.

## Useful digital ICs

- Logic gates
- Flip-flops and latches
- Counters
- Shift registers
- Multiplexers and decoders
- Schmitt-trigger buffers
- Level shifters

## Common problems

- Wrong chip orientation or pin numbering
- Missing power connection
- Floating inputs
- Incompatible logic levels
- Output contention between two driven outputs
- Missing decoupling capacitor
