---
title: Task 3 - Control Colour with Serial
layout: default
parent: Workshop 01 - RGB Controllers
nav_order: 5
---

# Task 3 - Control Colour with Serial

Control the lamp by sending `R`, `G`, `B`, `W` or `O` from the Serial Monitor.

```cpp
const int redPin = 3;
const int greenPin = 5;
const int bluePin = 6;

void setColour(int r, int g, int b) {
  analogWrite(redPin, r);
  analogWrite(greenPin, g);
  analogWrite(bluePin, b);
}

void setup() {
  Serial.begin(115200);
  pinMode(redPin, OUTPUT);
  pinMode(greenPin, OUTPUT);
  pinMode(bluePin, OUTPUT);
  Serial.println("Send R, G, B, W or O");
}

void loop() {
  if (!Serial.available()) return;

  char command = toupper(Serial.read());
  if (command == 'R') setColour(255, 0, 0);
  else if (command == 'G') setColour(0, 255, 0);
  else if (command == 'B') setColour(0, 0, 255);
  else if (command == 'W') setColour(255, 255, 255);
  else if (command == 'O') setColour(0, 0, 0);
  else Serial.println("Unknown command");
}
```

For a common-anode LED, invert the three values inside `setColour()`.

{: .challenge-title}
> Accept values
>
> Extend the program to accept commands such as `128,40,255`. Validate every value before applying it.
