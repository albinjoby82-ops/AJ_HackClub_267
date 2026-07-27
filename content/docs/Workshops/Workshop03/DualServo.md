---
title: Task 3 - Build a Two-Servo Linkage
layout: default
parent: Workshop 03 - Servos & Linkages
nav_order: 3
---

# Task 3 - Build a Two-Servo Linkage

Add a second servo to create a shoulder-and-elbow mechanism. Two joints create many more possible positions, but they also introduce collisions, power demands and control decisions.

## Build the mechanism

1. Secure the first servo to a wide cardboard base.
2. Attach a short, stiff cardboard link to its horn.
3. Mount the second servo near the end of that link.
4. Attach a lighter second link to the second servo.
5. Centre both servos at `90°` before fastening the horns.
6. Move each joint slowly and record its safe range.

Keep the links short and light. Support wires so they cannot pull on the moving arm.

## Control two joints

Connect a second potentiometer to `A1`, then upload:

```cpp
#include <Servo.h>

Servo shoulder;
Servo elbow;

void setup() {
  shoulder.attach(9);
  elbow.attach(10);
}

void loop() {
  int shoulderAngle = map(analogRead(A0), 0, 1023, 20, 160);
  int elbowAngle = map(analogRead(A1), 0, 1023, 25, 155);

  shoulder.write(shoulderAngle);
  elbow.write(elbowAngle);
  delay(15);
}
```

## Improve the movement

Directly following noisy controls can make a mechanism shake. Try:

- Averaging several analogue readings
- Ignoring changes smaller than two degrees
- Moving only one degree per loop towards the target
- Reducing the safe range to prevent collisions

{: .challenge-title}
> Record and replay
>
> Add a button that records five pairs of joint angles. Press another button to replay those positions smoothly instead of jumping directly between them.

{: .warning}
> Two physical servos can exceed the current available from an Arduino USB connection. Use a suitable external `5V` supply for the servos and join its ground to Arduino ground.
