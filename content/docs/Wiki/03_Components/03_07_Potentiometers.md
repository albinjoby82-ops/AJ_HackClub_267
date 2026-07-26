---
title: Potentiometers
layout: default
parent: 4. Components
nav_order: 7
---

# Potentiometers

A potentiometer is a manually adjustable resistor with three terminals: two ends of a resistive track and a movable **wiper**.

## As a voltage divider

Connect the outer terminals to supply and ground, then read the centre wiper:

```text
VCC ──/\/\/\/\/── GND
          ↑
        wiper
```

The wiper voltage moves between approximately ground and the supply voltage as the shaft turns.

For an Arduino Uno, connect the wiper to an analogue input. For a `3.3 V` microcontroller, connect the track to `3.3 V`, not `5 V`.

## Example

```cpp
const int POT_PIN = A0;

void setup() {
  Serial.begin(9600);
}

void loop() {
  int value = analogRead(POT_PIN);
  Serial.println(value);
  delay(50);
}
```

## As a variable resistor

Using the wiper and one outer terminal produces a variable resistance. Some circuits connect the unused outer terminal to the wiper so brief wiper contact loss does not leave an open circuit.

{: .warning}
> Potentiometers have resistance and power ratings. They are signal controls, not suitable speed controls for motors or high-power loads.

## Common mistakes

- Confusing the wiper with an outer terminal
- Connecting a `5 V` divider to a `3.3 V` input
- Leaving the wiper electrically floating
- Expecting a linear response from a logarithmic audio-taper part
- Exceeding the track's power rating
