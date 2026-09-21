---
title: Tool — Scan the I²C bus
layout: default
parent: Debug Kit
nav_order: 9
---

# Tool — Scan the I²C bus

[Debug kit setup and all steps](#/docs/Micromouse2026/Debug/index.md) · [Event pin map](#/docs/Micromouse2026/Hardware/ESP32C6.md)

## Connect

Sensors: 3V3/GND, SDA → GPIO6, SCL → GPIO7. Connected ToF XSHUT pins → GPIO18/19/20.

## Run and check

Idle SDA=1 SCL=1. With IMU and ToF connected, expect 0x68 and 0x29. This tool wakes all ToFs at their default address: one 0x29 entry does not prove all three work.

Use **ESP32C6 Dev Module**, **USB CDC On Boot: Enabled**, and **115200 baud / No Line Ending**. Open this sketch in its own Arduino sketch folder, upload, then press RESET with Serial Monitor open to see startup messages. Motor LED tests also work without Serial Monitor.

## Download or copy the code

<a href="../../../../downloads/micromouse-debug-kit/tools/i2c_scan/i2c_scan.ino" download="i2c_scan.ino">Download i2c_scan.ino</a> · <a href="../../../../downloads/micromouse-debug-kit.zip" download>Download the complete kit ZIP</a>

For an individual download, put <code>i2c_scan.ino</code> inside a folder named <code>i2c_scan</code> (Arduino IDE can create it), or paste the complete code into a new sketch. Extract the ZIP first if using the full kit; each sketch already has its matching folder.

<details>
<summary>Show complete sketch — use COPY to copy all code</summary>

```cpp
// =====================================================================
// TOOL - I2C scanner: what's actually connected?
// =====================================================================
// WIRING
//   Any I2C devices: SDA -> GPIO6, SCL -> GPIO7, VCC -> 3V3, GND -> GND
//   ToF XSHUT pins (if connected): GPIO18, GPIO19, GPIO20
//
// WHAT YOU'LL SEE
//   Serial Monitor with the IMU and ToF sensors all connected:
//       idle SDA=1 SCL=1 (both should be 1)
//
//       Scanning...
//         found 0x29
//         found 0x68
//       2 device(s)
//   (repeats every 3 seconds)
//   0x68 = the IMU (0x69 if its AD0 pin is HIGH)
//   0x29 = the ToF sensors. All three wake up at the same address in this
//          tool, so they show as ONE device. That's expected - steps 3-6
//          move them to separate addresses.
//
//   Problems:
//       idle SDA=0 SCL=0                -> a wire not connected, something
//                                          shorted to GND, or a board with
//                                          no power
//       idle 1/1 but "0 device(s)"      -> try swapping SDA and SCL
//       one device missing              -> check that board's 4 wires
// =====================================================================

#include <Arduino.h>
#include <Wire.h>

constexpr uint8_t I2C_SDA = 6;
constexpr uint8_t I2C_SCL = 7;
constexpr uint8_t XSHUT_PINS[] = {18, 19, 20};

void setup() {
  Serial.begin(115200);
  const uint32_t t0 = millis();
  while (!Serial && millis() - t0 < 2000) {}

  for (uint8_t p : XSHUT_PINS) {
    pinMode(p, OUTPUT);
    digitalWrite(p, HIGH);
  }
  delay(20);

  // Idle bus lines should sit HIGH. LOW means a missing pull-up or a short.
  pinMode(I2C_SDA, INPUT);
  pinMode(I2C_SCL, INPUT);
  Serial.printf("idle SDA=%d SCL=%d (both should be 1)\n",
                digitalRead(I2C_SDA), digitalRead(I2C_SCL));

  Wire.begin(I2C_SDA, I2C_SCL);
  Wire.setClock(100000);  // slow and forgiving while debugging wiring
}

void loop() {
  Serial.println("\nScanning...");
  uint8_t found = 0;
  for (uint8_t addr = 1; addr < 127; addr++) {
    Wire.beginTransmission(addr);
    if (Wire.endTransmission() == 0) {
      Serial.printf("  found 0x%02X\n", addr);
      found++;
    }
  }
  Serial.printf("%u device(s)\n", found);
  delay(3000);
}
```

</details>

## Original wiring notes and expected output

These are the comments supplied at the top of this sketch, with comment markers removed. They are the reference for this test.

```text
TOOL - I2C scanner: what's actually connected?
WIRING
  Any I2C devices: SDA -> GPIO6, SCL -> GPIO7, VCC -> 3V3, GND -> GND
  ToF XSHUT pins (if connected): GPIO18, GPIO19, GPIO20

WHAT YOU'LL SEE
  Serial Monitor with the IMU and ToF sensors all connected:
      idle SDA=1 SCL=1 (both should be 1)

      Scanning...
        found 0x29
        found 0x68
      2 device(s)
  (repeats every 3 seconds)
  0x68 = the IMU (0x69 if its AD0 pin is HIGH)
  0x29 = the ToF sensors. All three wake up at the same address in this
         tool, so they show as ONE device. That's expected - steps 3-6
         move them to separate addresses.

  Problems:
      idle SDA=0 SCL=0                -> a wire not connected, something
                                         shorted to GND, or a board with
                                         no power
      idle 1/1 but "0 device(s)"      -> try swapping SDA and SCL
      one device missing              -> check that board's 4 wires
```

## Continue

[Back to all steps and tools](#/docs/Micromouse2026/Debug/index.md).

If a step fails, switch off, disconnect the part you just added, and rerun the last passing step. Check the wiring above before moving on. [Extra diagnostic tools](#/docs/Micromouse2026/Debug/index.md).
