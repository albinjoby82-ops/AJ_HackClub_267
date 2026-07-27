---
title: Task 2 - Add RGB Status Feedback
layout: default
parent: Workshop 03 - Servos & Linkages
nav_order: 2
---

# Task 2 - Add RGB Status Feedback

Add an RGB LED that shows where the arm is in its range:

- Blue near the minimum angle
- Green through the safe centre
- Red near the maximum angle

## Wire the LED

Connect the RGB LED as you did in Workshop 01. Use one resistor for each colour channel and PWM-capable pins `3`, `5` and `6`.

The example below assumes a **common-cathode** RGB LED. For common-anode LEDs, invert each output by writing `255 - value`.

## Add a colour function

```cpp
const int redPin = 3;
const int greenPin = 5;
const int bluePin = 6;

void setColour(int red, int green, int blue) {
  analogWrite(redPin, red);
  analogWrite(greenPin, green);
  analogWrite(bluePin, blue);
}
```

Call `setColour()` after calculating the servo angle:

```cpp
if (angle < 45) {
  setColour(0, 0, 255);
} else if (angle > 135) {
  setColour(255, 0, 0);
} else {
  setColour(0, 255, 0);
}
```

## Make the transition smooth

Replace the three fixed colour regions with a gradient. Map angles from `0–90°` between blue and green, then map `90–180°` between green and red.

{: .challenge-title}
> Create a warning system
>
> Make the LED flash red if the requested angle is outside your linkage's measured safe range. Keep the servo inside the safe range using `constrain()`.
