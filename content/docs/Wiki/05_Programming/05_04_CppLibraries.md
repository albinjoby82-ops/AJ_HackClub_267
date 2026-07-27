---
title: Functions and Libraries
layout: default
parent: 6. Programming
nav_order: 6
---

# Functions and Libraries

Functions give a useful name to a piece of behaviour and prevent repeated code.

## A function with no return value

```cpp
void setLed(bool on) {
  digitalWrite(9, on ? HIGH : LOW);
}
```

Call it with:

```cpp
setLed(true);
```

## A function that returns a value

```cpp
int readPercentage(int pin) {
  int raw = analogRead(pin);
  return map(raw, 0, 1023, 0, 100);
}
```

## Scope

A variable declared inside a function is normally available only inside that function. A global variable is available throughout the sketch, but excessive global state makes programs harder to understand.

## Libraries

A library contains reusable code for a device or task.

```cpp
#include <Servo.h>

Servo arm;

void setup() {
  arm.attach(9);
  arm.write(90);
}

void loop() {}
```

Install third-party libraries through Arduino IDE's Library Manager. Check that:

- The library supports your board
- Examples match your hardware
- Pin and voltage assumptions are correct
- You do not have conflicting libraries with the same header name

{: .warning}
> Servo pulse limits vary. Do not copy extreme pulse-width values without checking the servo and mechanism.

## Design challenge

Take a long `loop()` and extract functions named after intentions, such as `readControls()`, `updateMotor()` and `showStatus()`.
