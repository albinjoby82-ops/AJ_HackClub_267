---
title: 01 — Check the onboard LED
layout: default
parent: Debug Kit
nav_order: 1
---

# 01 — Check the onboard LED

[Debug kit setup and all steps](#/docs/Micromouse2026/Debug/index.md) · [Event pin map](#/docs/Micromouse2026/Hardware/ESP32C6.md)

## Connect

USB only; no external wiring.

## Run and check

Solid red LED and an “alive” line every second.

Use **ESP32C6 Dev Module**, **USB CDC On Boot: Enabled**, and **115200 baud / No Line Ending**. Open this sketch in its own Arduino sketch folder, upload, then press RESET with Serial Monitor open to see startup messages. Motor LED tests also work without Serial Monitor.

## Download or copy the code

<a href="../../../../downloads/micromouse-debug-kit/01_led_red/01_led_red.ino" download="01_led_red.ino">Download 01_led_red.ino</a> · <a href="../../../../downloads/micromouse-debug-kit.zip" download>Download the complete kit ZIP</a>

For an individual download, put <code>01_led_red.ino</code> inside a folder named <code>01_led_red</code> (Arduino IDE can create it), or paste the complete code into a new sketch. Extract the ZIP first if using the full kit; each sketch already has its matching folder.

<details>
<summary>Show complete sketch — use COPY to copy all code</summary>

```cpp
// =====================================================================
// STEP 1 - Is the ESP32-C6 alive?  Turns the onboard LED red.
// =====================================================================
// WIRING
//   Nothing. Just plug the ESP32-C6 into your laptop over USB.
//   (The RGB LED is built into the board on GPIO8.)
//
// WHAT YOU'LL SEE
//   LED: solid RED.
//   Serial Monitor:
//       STEP 1: LED should be RED
//       alive
//       alive
//       alive          <- a new line every second
//
// ARDUINO IDE SETTINGS
//   Board: ESP32C6 Dev Module     Tools -> USB CDC On Boot: Enabled
//   Serial Monitor: 115200 baud
//
// IF IT FAILS
//   Upload error "no upload port" -> try another USB cable (many only
//     charge), then pick the port under Tools -> Port.
//   LED red but Serial blank -> USB CDC On Boot must be Enabled.
// =====================================================================

#include <Arduino.h>

#ifndef RGB_BUILTIN
#define RGB_BUILTIN 8
#endif

void setup() {
  Serial.begin(115200);
  const uint32_t t0 = millis();
  while (!Serial && millis() - t0 < 2000) {}

  rgbLedWrite(RGB_BUILTIN, 32, 0, 0);  // red, dimmed: 255 is blinding
  Serial.println("\nSTEP 1: LED should be RED");
}

void loop() {
  Serial.println("alive");
  delay(1000);
}
```

</details>

## Original wiring notes and expected output

These are the comments supplied at the top of this sketch, with comment markers removed. They are the reference for this test.

```text
STEP 1 - Is the ESP32-C6 alive?  Turns the onboard LED red.
WIRING
  Nothing. Just plug the ESP32-C6 into your laptop over USB.
  (The RGB LED is built into the board on GPIO8.)

WHAT YOU'LL SEE
  LED: solid RED.
  Serial Monitor:
      STEP 1: LED should be RED
      alive
      alive
      alive          <- a new line every second

ARDUINO IDE SETTINGS
  Board: ESP32C6 Dev Module     Tools -> USB CDC On Boot: Enabled
  Serial Monitor: 115200 baud

IF IT FAILS
  Upload error "no upload port" -> try another USB cable (many only
    charge), then pick the port under Tools -> Port.
  LED red but Serial blank -> USB CDC On Boot must be Enabled.
```

## Continue

Next: [02 — Test the IMU](#/docs/Micromouse2026/Debug/02_imu.md).

If a step fails, switch off, disconnect the part you just added, and rerun the last passing step. Check the wiring above before moving on. [Extra diagnostic tools](#/docs/Micromouse2026/Debug/index.md).
