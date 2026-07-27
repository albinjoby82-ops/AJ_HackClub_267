---
title: Task 1 - Plot and Clean a Signal
layout: default
parent: Workshop 04 - Good Waves, Bad Vibes
nav_order: 1
---

# Task 1 - Plot and Clean a Signal

## 1. Wire the input

Place a potentiometer across the breadboard's centre gap. Connect one outside pin to `5V`, the other outside pin to `GND`, and the middle pin to `A0`.

If you have a photoresistor instead, make a voltage divider with the photoresistor and a `10 kΩ` resistor, then connect their meeting point to `A0`.

## 2. Plot the raw reading

Upload this sketch, then open **Tools > Serial Plotter** and turn the potentiometer slowly.

```cpp
void setup() {
  Serial.begin(115200);
}

void loop() {
  int raw = analogRead(A0);
  Serial.println(raw);
  delay(10);
}
```

The reading should stay between `0` and `1023` on an Arduino Uno. A slightly restless line is normal: real signals contain noise.

## 3. Smooth the signal

Replace `loop()` with a ten-sample moving average:

```cpp
void loop() {
  long total = 0;

  for (int i = 0; i < 10; i++) {
    total += analogRead(A0);
  }

  int smoothed = total / 10;
  Serial.println(smoothed);
  delay(10);
}
```

Compare the plots. Smoothing reduces noise, but it also makes sudden changes appear more slowly. That trade-off matters in every measurement system.

## 4. Generate a known wave

You can test the plotter without a sensor:

```cpp
void setup() {
  Serial.begin(115200);
}

void loop() {
  static float angle = 0;
  int sample = 512 + 400 * sin(angle);
  Serial.println(sample);
  angle += 0.08;
  delay(10);
}
```

Change the angle step or delay and predict what will happen before uploading again.

## Optional oscilloscope extension

In the electronics lab, connect an oscilloscope probe to a signal and its ground clip to circuit ground. Check whether the probe and the scope channel are both set to `1×` or both set to `10×`. Our Rohde & Schwarz HMO1002 probes are commonly left in `10×`; a mismatch makes the displayed voltage ten times too large or too small.

Measure peak voltage, period and frequency, then compare them with the Serial Plotter view.
