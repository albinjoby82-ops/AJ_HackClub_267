---
title: Engineering Trade-offs
layout: default
parent: 7. Engineering Concepts
nav_order: 10
---

# Engineering Trade-offs

Engineering balances competing goals under constraints.

- Speed versus torque
- Strength versus mass
- Accuracy versus cost
- Battery life versus performance
- Simplicity versus flexibility
- Noise reduction versus response time

## Write testable requirements

```text
The device should run for at least 4 hours.
The enclosure should fit inside 120 × 80 × 40 mm.
The sensor should update at least 10 times per second.
```

“Make it good” cannot guide a decision.

## Prototype risky assumptions

Test whether:

- The motor has enough torque
- The sensor works at the required distance
- Parts fit with realistic tolerances
- Communication remains reliable

```text
define → build → measure → learn → improve
```

A failed prototype is useful when it answers a question and the result is recorded.
