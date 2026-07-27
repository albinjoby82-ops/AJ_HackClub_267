---
title: Programming Basics
layout: default
parent: 6. Programming
nav_order: 3
---

# Programming Basics

## Digital output

```cpp
const int ledPin = 9;

void setup() {
  pinMode(ledPin, OUTPUT);
}

void loop() {
  digitalWrite(ledPin, HIGH);
}
```

`pinMode()` configures the pin. `digitalWrite()` then sets it HIGH or LOW.

## Digital input

```cpp
const int buttonPin = 2;

void setup() {
  pinMode(buttonPin, INPUT_PULLUP);
}

void loop() {
  bool pressed = digitalRead(buttonPin) == LOW;
}
```

With `INPUT_PULLUP`, connect the button between the pin and ground. The input is LOW when pressed.

## Analogue input

```cpp
int reading = analogRead(A0);
```

On a classic Arduino Uno, the result is normally `0–1023`. Other boards may use different ranges.

## PWM output

```cpp
analogWrite(9, 128);
```

On supported Uno pins, this produces PWM with roughly 50% duty cycle. It is not a true steady analogue voltage.

## Conditions

```cpp
if (reading > 700) {
  digitalWrite(ledPin, HIGH);
} else {
  digitalWrite(ledPin, LOW);
}
```

## Repetition

```cpp
for (int i = 0; i < 3; i++) {
  digitalWrite(ledPin, HIGH);
  delay(100);
  digitalWrite(ledPin, LOW);
  delay(100);
}
```

## Serial debugging

```cpp
void setup() {
  Serial.begin(115200);
}

void loop() {
  int reading = analogRead(A0);
  Serial.print("sensor=");
  Serial.println(reading);
  delay(100);
}
```

Use meaningful labels so the output remains understandable.
