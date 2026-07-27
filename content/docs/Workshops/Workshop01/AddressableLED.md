---
title: Advanced Task 2 - Drive an Addressable LED Strip
layout: default
parent: Workshop 01 - RGB Controllers
nav_order: 7
---

# Advanced Task 2 - Drive an Addressable LED Strip

Addressable LEDs such as WS2812B modules contain a tiny controller in every pixel. One data wire can control many LEDs independently.

## Additional equipment

- A short WS2812B strip or ring
- `330 Ω` resistor in the data line
- `1000 µF` capacitor across the strip supply
- A suitable `5V` supply for more than a few pixels

Connect Arduino ground and LED-supply ground together. Do not power a long strip through an Arduino pin.

Using the Adafruit NeoPixel library:

```cpp
#include <Adafruit_NeoPixel.h>

const int dataPin = 6;
const int pixelCount = 8;
Adafruit_NeoPixel pixels(pixelCount, dataPin, NEO_GRB + NEO_KHZ800);

void setup() {
  pixels.begin();
  pixels.setBrightness(40);
}

void loop() {
  for (int i = 0; i < pixelCount; i++) {
    pixels.clear();
    pixels.setPixelColor(i, pixels.Color(255, 40, 0));
    pixels.show();
    delay(80);
  }
}
```

{: .challenge-title}
> Make an animation engine
>
> Replace `delay()` with `millis()`, layer two effects together and accept live colour or speed commands over Serial.
