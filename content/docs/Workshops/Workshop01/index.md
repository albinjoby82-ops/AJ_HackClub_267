---
title: Workshop 01 - RGB Controllers
layout: default
nav_order: 2
---

# Workshop 01 - RGB Controllers

Learn how microcontrollers work by building and programming an Arduino circuit. This workshop goes beyond blinking a single LED: participants create a pseudo-RGB light strip, use PWM to mix colours, and explore how multiple Arduinos can communicate to build longer chains of lights and effects.

This workshop is designed for beginners and can be completed at home in either of two ways:

- **Physical route:** Arduino Uno-compatible board, USB cable, breadboard, jumper wires, one RGB LED, and three `220–470 Ω` resistors
- **Free simulator route:** Tinkercad Circuits using its virtual Arduino, breadboard, RGB LED, and resistors

You do not need an oscilloscope, bench supply, soldering iron, or specialist laboratory equipment.

## What you will make

A controllable RGB light that:

1. Displays red, green, and blue
2. Mixes colours using PWM
3. Runs a colour sequence
4. Can be extended with Serial commands or a potentiometer

## Workshop route

### Preparation

- [Prepare at home](AtHome.md)
- [Introduction](Intro.md)

### Core tasks

1. [Task 1 - Build the RGB circuit](Task0.md)
2. [Task 2 - Program colour sequences](Task1.md)
3. [Task 3 - Control colour with Serial](SerialControl.md)

### Advanced tasks

4. [Advanced Task 1 - Build a sensor-controlled lamp](SensorColour.md)
5. [Advanced Task 2 - Drive an addressable LED strip](AddressableLED.md)

{: .warning}
> Use one current-limiting resistor for each LED colour. Check whether your RGB LED is common-anode or common-cathode before applying power.

![Hackers learning Arduino in the RGB Controllers workshop](../../assets/images/Workshop1-Image1.jpeg)
