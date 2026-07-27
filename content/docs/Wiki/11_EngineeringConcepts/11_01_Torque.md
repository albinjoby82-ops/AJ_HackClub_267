---
title: Torque
layout: default
parent: 7. Engineering Concepts
nav_order: 5
---

# Torque

Torque describes the turning effect of a force.

```text
torque = force × perpendicular distance from the pivot
τ = F × r
```

If a `2 N` force acts `0.1 m` from a pivot, the torque is `0.2 N·m`. The same force creates more torque when applied farther from the pivot.

## Why it matters

- A servo must provide enough torque to hold an arm.
- A motor needs more torque to accelerate a heavy wheel.
- Long robot arms multiply the torque required at the base.
- Gears can trade speed for torque.

## Servo ratings

Small servos are often rated in `kg·cm`.

```text
1 kg·cm ≈ 0.098 N·m
```

A `2 kg·cm` servo does not safely lift a `2 kg` mass in every mechanism. The rating is normally a stall or maximum figure at a specified voltage, and real designs need margin.

- **Holding torque:** keeps a stationary load in place.
- **Running torque:** available while moving.
- **Stall torque:** maximum torque at zero speed; remaining stalled can overheat a motor or servo.

{: .tip}
> Reduce the load, shorten the arm, add counterbalance or change gearing before simply choosing a larger motor.
