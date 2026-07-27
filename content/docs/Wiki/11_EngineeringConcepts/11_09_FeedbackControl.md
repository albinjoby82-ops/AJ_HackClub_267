---
title: Feedback and Control Systems
layout: default
parent: 7. Engineering Concepts
nav_order: 9
---

# Feedback and Control Systems

A control system tries to make an output behave as desired.

```text
target → controller → actuator → system → measured output
              ↑                         |
              └──────── feedback ───────┘
```

## Open-loop control

The controller sends a command without measuring the result—for example, running a motor for two seconds and assuming it moved far enough.

## Closed-loop control

A sensor measures the output and the controller uses the error:

```text
error = target - measured value
```

Examples include thermostats, line-following robots and servo position controllers.

## Proportional control

```cpp
float error = target - measured;
float command = kp * error;
```

A larger error creates a stronger correction. If `kp` is too small, response is weak; if too large, the system may oscillate.

Real systems must handle sensor noise, delay, actuator limits, backlash, friction and overshoot.
