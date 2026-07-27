---
title: "Task 1: Drive, reverse, and steer"
layout: default
nav_order: 2
parent: Workshop 03 - Make an RC Car at Home!
---

# Task 1: Drive, reverse, and steer

Upload this sketch with the battery disconnected. After the upload finishes,
lift the car so the wheels are off the table, connect the battery, and test.

```cpp
const byte LEFT_A = 2;
const byte LEFT_B = 3;
const byte RIGHT_A = 4;
const byte RIGHT_B = 5;
const byte LEFT_SPEED = 9;
const byte RIGHT_SPEED = 10;

void motorPins(byte a, byte b, byte pwm) {
  // Start every control output in a known, stopped state.
  digitalWrite(a, LOW);
  digitalWrite(b, LOW);
  digitalWrite(pwm, LOW);
  pinMode(a, OUTPUT);
  pinMode(b, OUTPUT);
  pinMode(pwm, OUTPUT);
}

void setMotor(byte a, byte b, byte pwm, int speed) {
  speed = constrain(speed, -255, 255);
  if (speed > 0) {
    digitalWrite(a, HIGH);
    digitalWrite(b, LOW);
  } else if (speed < 0) {
    digitalWrite(a, LOW);
    digitalWrite(b, HIGH);
  } else {
    digitalWrite(a, LOW);
    digitalWrite(b, LOW);
  }
  analogWrite(pwm, abs(speed));
}

void drive(int left, int right) {
  setMotor(LEFT_A, LEFT_B, LEFT_SPEED, left);
  setMotor(RIGHT_A, RIGHT_B, RIGHT_SPEED, right);
}

void setup() {
  motorPins(LEFT_A, LEFT_B, LEFT_SPEED);
  motorPins(RIGHT_A, RIGHT_B, RIGHT_SPEED);
  drive(0, 0);
}

void loop() {
  drive(170, 170);    // forward
  delay(1500);
  drive(0, 0);        // stop
  delay(500);
  drive(-170, -170);  // reverse
  delay(1000);
  drive(0, 0);
  delay(500);
  drive(180, -180);   // spin in place
  delay(600);
  drive(0, 0);
  delay(1500);
}
```

## If a wheel spins the wrong way

Disconnect the battery and swap the two wires for that motor, or negate that
side's speed in `drive()`. Never change motor wires while powered.

## If the car turns instead of driving straight

Try a slightly lower PWM value on the faster side, for example
`drive(160, 145)`. Small motors are not perfectly matched, so calibration is
normal.
