---
title: Task 3 - Compare Filtering Methods
layout: default
parent: Workshop 04 - Good Waves, Bad Vibes
nav_order: 3
---

# Task 3 - Compare Filtering Methods

Compare three versions of the same analogue input in the Serial Plotter:

1. Raw reading
2. Ten-sample moving average
3. Exponential moving average

```cpp
float filtered = 0;

void setup() {
  Serial.begin(115200);
}

void loop() {
  int raw = analogRead(A0);

  long total = 0;
  for (int i = 0; i < 10; i++) total += analogRead(A0);
  int average = total / 10;

  filtered = 0.15 * raw + 0.85 * filtered;

  Serial.print("raw:");
  Serial.print(raw);
  Serial.print(",average:");
  Serial.print(average);
  Serial.print(",exponential:");
  Serial.println(filtered);
  delay(10);
}
```

Move the potentiometer slowly, then sharply. Compare noise reduction with response delay.

{: .challenge-title}
> Choose scientifically
>
> Record the resting variation and the response time of each method. Recommend one filter for a slow temperature sensor and another for a reaction-time button.
