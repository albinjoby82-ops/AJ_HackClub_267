---
title: Task 1 - Build a Cardboard Servo Arm
layout: default
parent: Workshop 03 - Servos & Linkages
nav_order: 1
---

# Task 1 - Build a Cardboard Servo Arm

## 1. Test the servo

Connect the servo signal to pin `9`, power to a suitable `5 V` source, and ground to the common ground.

```cpp
#include <Servo.h>

Servo arm;

void setup() {
  arm.attach(9);
  arm.write(90);
}

void loop() {}
```

Upload the sketch before attaching the cardboard arm. The servo should move to its centre position.

## 2. Add the potentiometer

Connect the outer terminals to `5V` and `GND`, and the wiper to `A0`.

```cpp
#include <Servo.h>

Servo arm;

void setup() {
  arm.attach(9);
}

void loop() {
  int reading = analogRead(A0);
  int angle = map(reading, 0, 1023, 15, 165);
  arm.write(angle);
  delay(15);
}
```

The limited `15–165°` range leaves some margin at each end.

## 3. Make the mechanism

1. Cut a cardboard base about the size of a postcard.
2. Tape or tie the servo firmly to the base without covering its shaft.
3. Cut a narrow cardboard arm.
4. Attach the arm to the servo horn.
5. Add a pivoted second link with a paper fastener if desired.
6. Move the potentiometer slowly and watch for collisions.

## 4. Calibrate it

Reduce the software angle range if the linkage hits the base or binds. Record the safe minimum and maximum values.

{: .challenge-title}
> Add feedback
>
> Add a green LED when the arm is in its safe centre range and a red LED near either limit.
