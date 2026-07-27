---
title: Prepare at Home
layout: default
parent: Workshop 02 - Signals to Speed
nav_order: 0
---

# Prepare at Home

The entire core workshop works in Tinkercad Circuits. Physical hardware is optional.

## Free simulator route

Create a circuit containing:

- Arduino Uno
- Micro servo
- `10 kΩ` potentiometer
- Breadboard
- Jumper wires

Tinkercad supplies virtual power and includes Serial Monitor.

## Physical route

You need:

- Arduino Uno-compatible board and USB cable
- SG90-style micro servo
- `10 kΩ` potentiometer
- Breadboard and jumper wires
- Optional separate regulated `5 V` servo supply

Typical servo wire colours are brown/black for ground, red for power, and orange/yellow/white for signal—but verify the servo.

{: .warning-title}
> Protect the board
>
> Never connect servo power to a GPIO pin. Small servos may work from the board's `5 V` rail under light load, but sudden current demand can reset or damage the setup. A suitable external supply is safer for physical builds; connect its ground to Arduino ground.
