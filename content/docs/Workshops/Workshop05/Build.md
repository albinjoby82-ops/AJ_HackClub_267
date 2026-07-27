---
title: Task 1 - Build the Reaction Timer
layout: default
parent: Workshop 05 - Reaction Timer
nav_order: 1
---

# Task 1 - Build the Reaction Timer

## Wire it

1. Connect an LED's long leg to digital pin `9` through a `220 Ω` to `330 Ω` resistor.
2. Connect the LED's short leg to `GND`.
3. Place the push button across the breadboard's centre gap.
4. Connect one side of the button to digital pin `2` and the opposite side to `GND`.

Using `INPUT_PULLUP` means you do not need a separate resistor for the button. The pin reads `HIGH` normally and `LOW` while pressed.

## Upload the game

```cpp
const int ledPin = 9;
const int buttonPin = 2;

void setup() {
  pinMode(ledPin, OUTPUT);
  pinMode(buttonPin, INPUT_PULLUP);
  Serial.begin(115200);
  randomSeed(analogRead(A0));
}

void loop() {
  Serial.println("Get ready...");
  digitalWrite(ledPin, LOW);
  delay(random(2000, 5001));

  unsigned long started = millis();
  digitalWrite(ledPin, HIGH);

  while (digitalRead(buttonPin) == HIGH) {
    // Wait for the player.
  }

  unsigned long reactionTime = millis() - started;
  digitalWrite(ledPin, LOW);

  Serial.print("Reaction time: ");
  Serial.print(reactionTime);
  Serial.println(" ms");
  delay(1500);
}
```

Open the Serial Monitor at `115200` baud and play several rounds.

## Improve it

- Detect and report an early button press.
- Keep the best score.
- Add a buzzer when the LED turns on.
- Add a second button for a two-player version.
