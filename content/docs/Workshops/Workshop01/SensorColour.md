---
title: Advanced Task 1 - Build a Sensor-Controlled Lamp
layout: default
parent: Workshop 01 - RGB Controllers
nav_order: 6
---

# Advanced Task 1 - Build a Sensor-Controlled Lamp

Add three `10 kΩ` potentiometers to `A0`, `A1` and `A2`. Treat them as physical red, green and blue controls.

```cpp
void loop() {
  int red = map(analogRead(A0), 0, 1023, 0, 255);
  int green = map(analogRead(A1), 0, 1023, 0, 255);
  int blue = map(analogRead(A2), 0, 1023, 0, 255);
  setColour(red, green, blue);
  delay(10);
}
```

## Advanced challenges

- Replace one potentiometer with a photoresistor voltage divider so the lamp reacts to room brightness.
- Smooth each input without making the controls feel delayed.
- Add a button that stores and recalls three favourite colours.
- Use `millis()` to fade between stored colours without blocking the controls.
