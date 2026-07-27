---
title: Task 2 - Measure Period and Frequency
layout: default
parent: Workshop 04 - Good Waves, Bad Vibes
nav_order: 2
---

# Task 2 - Measure Period and Frequency

Generate a square wave on pin `9`, then measure it with Arduino timing.

```cpp
const int outputPin = 9;

void setup() {
  pinMode(outputPin, OUTPUT);
}

void loop() {
  digitalWrite(outputPin, HIGH);
  delay(5);
  digitalWrite(outputPin, LOW);
  delay(5);
}
```

The expected period is approximately `10 ms`, so the expected frequency is:

```text
frequency = 1 / period = 1 / 0.010 = 100 Hz
```

Connect pin `9` to pin `2` and share ground. Use `pulseIn()` to measure the HIGH and LOW times, then calculate period and frequency.

```cpp
unsigned long highTime = pulseIn(2, HIGH);
unsigned long lowTime = pulseIn(2, LOW);
float periodSeconds = (highTime + lowTime) / 1000000.0;
float frequency = 1.0 / periodSeconds;
```

{: .challenge-title}
> Find the limits
>
> Change the generated frequency and determine when `pulseIn()` or Serial output stops giving stable results. Explain why measurement tools have bandwidth and sampling limits.
