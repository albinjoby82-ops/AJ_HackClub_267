---
title: Advanced Task 3 - Serial Motion Console
layout: default
parent: Workshop 02 - Signals to Speed
nav_order: 22
---

# Advanced Task 3 - Serial Motion Console

Create a text interface that accepts commands:

```text
MOVE 45
SPEED 20
SWEEP
STOP
STATUS
```

Read one line at a time, split the command from its value and reject angles outside the measured safe range.

## Requirements

- Invalid commands must not move the servo.
- `STOP` must interrupt a sweep immediately.
- `STATUS` reports current angle, target and mode.
- Motion must remain non-blocking so Serial input is always responsive.

{: .challenge-title}
> Script a sequence
>
> Accept a list such as `SEQ 20,90,150,90` and replay it with controlled speed. Avoid dynamic `String` growth if you want the program to run reliably for long periods.
