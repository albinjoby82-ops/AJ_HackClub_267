---
title: Workshop 03 - Servos & Linkages
layout: default
nav_order: 4
---

# Workshop 03 - Servos & Linkages

Bring together the RGB LEDs from Workshop 01 and the servos from Workshop 02. Guided tasks cover the fundamentals, while confident builders can take on advanced mechanisms, interface design and integration challenges.

This workshop explores:

- **Driving RGB LEDs** with PWM for colour mixing and timed effects
- **Advanced servo mechanisms**, including angle mapping and multiple servos
- **Mechanical linkages and robotic arms**, mounting and basic kinematics
- **Interfacing an LCD screen** to show live values and simple menus

By the end, you can have a working prototype that combines light, motion, controls and mechanical linkages.

## Equipment

For the core tasks:

- Arduino Uno-compatible board and USB cable, or Tinkercad Circuits
- One or two micro servos
- One `10 kΩ` potentiometer
- One RGB LED and three `220 Ω` to `330 Ω` resistors
- Breadboard and jumper wires
- Cardboard, tape, ruler, pencil and scissors
- Paper fasteners, cocktail sticks or small bolts for pivots

For the advanced interface task, add a `16×2` LCD—preferably with an I²C backpack—and a second potentiometer or joystick.

{: .warning}
> A single small unloaded servo may work from the Arduino's `5V` pin, but multiple or loaded servos should use a suitable separate `5V` supply. Always connect the external supply ground to Arduino ground. Stop power if a servo stalls, buzzes continuously or becomes hot.

## Workshop route

### Core tasks

1. [Task 1 - Build a cardboard servo arm](Build.md)
2. [Task 2 - Add RGB status feedback](RGBFeedback.md)
3. [Task 3 - Build a two-servo linkage](DualServo.md)

### Advanced tasks

4. [Advanced Task 1 - Add an LCD control panel](LCDControl.md)
5. [Advanced Task 2 - Coordinate motion with kinematics](Kinematics.md)
6. Combine the tasks into your own light-and-motion machine.

The electronics for Tasks 1–3 can be prototyped in Tinkercad. The cardboard mechanism avoids the need for a 3D printer or specialist workshop tools.

![Servo wiring diagram](../../assets/images/Workshop2-Image3.png)
