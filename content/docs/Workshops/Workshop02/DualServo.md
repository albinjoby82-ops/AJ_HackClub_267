---
title: Advanced Task 2 - Coordinated Dual-Servo Motion
layout: default
parent: Workshop 02 - Signals to Speed
nav_order: 21
---

# Advanced Task 2 - Coordinated Dual-Servo Motion

Connect a second servo and make both joints arrive at their targets together, even when one travels farther.

## Design requirement

Do not jump directly to the target. Store:

- Current angle for each servo
- Target angle for each servo
- Start time
- Movement duration

On every loop, calculate progress from `0.0` to `1.0` and interpolate both angles.

```cpp
float progress = constrain(
  (millis() - moveStarted) / float(moveDuration),
  0.0, 1.0
);

int angle = startAngle + (targetAngle - startAngle) * progress;
```

{: .challenge-title}
> Add easing
>
> Replace linear progress with a smoothstep curve: `p = p * p * (3 - 2 * p)`. Compare the mechanism's start and stop behaviour.

Use a suitable external `5V` servo supply and connect its ground to Arduino ground.
