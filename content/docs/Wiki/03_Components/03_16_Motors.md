---
title: Motors
layout: default
parent: 4. Components
nav_order: 16
---

# Motors

Motors convert electrical energy into mechanical motion. They often need more current than a microcontroller pin can provide and generate electrical noise.

{: .warning-title}
> Use a motor driver
>
> Do not connect a motor directly to GPIO. Use a suitable transistor, H-bridge, servo interface, stepper driver, or motor controller, together with appropriate power and protection.

## Brushed DC motors

A brushed DC motor rotates continuously when voltage is applied. Reversing polarity reverses direction. PWM can control average speed through a driver.

Use flyback protection and decoupling as required. Stall current can be many times higher than no-load current; size the driver and supply for it.

## Servos

Hobby servos contain a motor, gearbox, position sensor, and controller. They commonly receive a repeated control pulse indicating a requested position.

Power the servo from a suitable supply rather than GPIO. Join grounds between the controller and servo supply.

Not every servo is limited to exactly `0–180°`; range and pulse requirements vary.

## Stepper motors

A stepper moves in discrete steps using multiple windings. It requires a suitable driver that sequences and limits winding current.

Do not disconnect a stepper motor from an energised driver. Set the driver's current limit for the motor and provide cooling where required.

## Brushless motors

Brushless DC motors require electronic commutation, normally provided by an ESC or dedicated controller. Confirm phase connections, supply voltage, current capability, control method, and startup safety.

## Common problems

- Supply enters current limit during startup or stall
- Controller resets from voltage drop or noise
- Missing common ground
- Driver overheats
- Flyback protection omitted
- Mechanical load exceeds available torque
- Servo supply is too weak
- Stepper current limit is incorrect
