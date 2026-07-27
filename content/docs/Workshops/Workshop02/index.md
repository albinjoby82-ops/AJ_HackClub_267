---
title: Workshop 02 - Signals to Speed
layout: default
nav_order: 3
---

# Workshop 02 - Signals to Speed

Dive into motor controllers and electromechanical motion. This hands-on track is for anyone curious about how robots move, how PWM controls speed, or what makes a servo tick.

This workshop explores:
- How microcontrollers can **control DC motors, servos, and more**
- Using **PWM** to vary speed and direction
- Concepts like **torque, back-EMF, and H-bridges**
- How to **wire and safely power** your circuit, as well as **program** simple movements.

The workshop builds on basic Arduino skills, but beginners can follow the guided steps.

## Complete it at home

- **Simulator route:** use Tinkercad Circuits for every core task at no cost
- **Physical route:** Arduino-compatible board, USB cable, SG90-style micro servo, `10 kΩ` potentiometer, breadboard, and jumper wires

The simulator route is recommended if you do not already own a servo. No bench power supply or specialist test equipment is required.

## Workshop route

### Preparation

- [Prepare at home](AtHome.md)
- [Introduction](Intro.md)

### Core tasks

1. [Task 0 - Check the Arduino](Task0.md)
2. [Task 1 - Move a servo](Task1.md)
3. [Task 2 - Organise movement with functions](Task2.md)
4. [Task 3 - Debug with Serial](Task3.md)
5. [Task 4 - Potentiometer control](Task4.md)

### Advanced tasks

6. [Advanced Task 1 - Modes, switches and fine control](ControlModes.md)
7. [Advanced Task 2 - Coordinated dual-servo motion](DualServo.md)
8. [Advanced Task 3 - Serial motion console](SerialConsole.md)

The [challenge route](LabStructure.md) contains shorter extension ideas.

{: .warning}
> A servo can draw more current than a microcontroller GPIO pin can supply. Never power a servo from a GPIO pin. If a physical servo causes resets or unstable movement, use a suitable separate `5 V` supply and connect the grounds.

![Potentiometer and servo circuit](../../assets/images/Workshop2-Image6.png)
