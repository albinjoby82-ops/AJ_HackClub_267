---
title: Prepare at Home
layout: default
parent: Workshop 01 - RGB Controllers
nav_order: 0
---

# Prepare at Home

Choose either the simulator route or the physical route. Both teach the same circuit and programming ideas.

## Free simulator route

1. Create a free Tinkercad account.
2. Open **Circuits** and create a new circuit.
3. Add an Arduino Uno, small breadboard, RGB LED, and three resistors.
4. Set each resistor to a value between `220 Ω` and `470 Ω`.
5. Open the code panel and select text code.

## Physical route

You need:

- Arduino Uno or compatible `5 V` board
- Data-capable USB cable
- Breadboard
- RGB LED
- Three `220–470 Ω` resistors
- Male-to-male jumper wires
- Arduino IDE

## Identify the RGB LED

RGB LEDs are commonly:

- **Common cathode:** shared pin connects to ground; higher PWM values make colours brighter
- **Common anode:** shared pin connects to `5 V`; lower PWM values make colours brighter

Check the part information or use diode mode. Pin order varies between manufacturers.

{: .warning}
> Disconnect USB power before moving physical wires. Never connect an LED colour directly to a GPIO pin without its own resistor.
