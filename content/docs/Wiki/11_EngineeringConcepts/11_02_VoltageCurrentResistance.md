---
title: Voltage, Current and Resistance
layout: default
parent: 7. Engineering Concepts
nav_order: 1
---

# Voltage, Current and Resistance

- **Voltage** is electrical potential difference—the push available to move charge.
- **Current** is the rate of charge flow.
- **Resistance** opposes current.

For a resistor:

```text
V = I × R
```

## LED resistor example

For a red LED with approximately `2 V` across it on a `5 V` output, aiming for `10 mA`:

```text
R = (5 V - 2 V) / 0.010 A = 300 Ω
```

Choose a nearby standard value such as `330 Ω`.

## Series and parallel

- Components in **series** share the same current.
- Components in **parallel** share the same voltage.
- Series resistances add: `Rtotal = R1 + R2`.
- Two equal resistors in parallel have half the resistance of one.

A supply does not force its current-limit value through a circuit. The load draws current; the limit sets a maximum and may reduce voltage when reached.

{: .warning}
> Ohm's law directly describes resistors. Motors, LEDs, batteries and semiconductor devices are not fixed resistances.
