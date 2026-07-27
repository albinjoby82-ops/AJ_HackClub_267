---
title: Task 1 - Build the RGB Circuit
layout: default
parent: Workshop 01 - RGB Controllers
nav_order: 3
---

# Task 1 - Build the RGB Circuit

## What you need

- Arduino Uno-compatible board
- One RGB LED
- Three `220 Ω` to `330 Ω` resistors
- Breadboard and jumper wires
- Data-capable USB cable

You can build the same circuit in Tinkercad if you do not have the parts.

## Identify the RGB LED

An RGB LED is usually **common cathode** or **common anode**. Check its datasheet or supplier description:

- Common cathode: connect the common leg to `GND`; larger PWM values mean brighter colours.
- Common anode: connect the common leg to `5V`; smaller PWM values mean brighter colours.

Do not guess from leg length alone, because packages vary.

## Wire it

Place the LED so each leg enters a different breadboard row. Connect each red, green and blue leg through its **own resistor** to PWM pins `3`, `5` and `6`. Connect the common leg to `GND` or `5V`, depending on the LED type.

One resistor per colour gives more predictable brightness and protects both the LED and Arduino.

## Check the Arduino

1. Connect the board with a data-capable USB cable.
2. In Arduino IDE, select **Arduino Uno** and the board's port.
3. Open **File > Examples > 01.Basics > Blink**.
4. Upload it and check that the onboard LED blinks.

If no port appears, try another USB port or cable. Many USB cables can charge devices but cannot transfer data.
