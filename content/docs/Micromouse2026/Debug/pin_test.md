---
title: Tool — Check motor control pins
layout: default
parent: Debug Kit
nav_order: 10
---

# Tool — Check motor control pins

[Debug kit setup and all steps](#/docs/Micromouse2026/Debug/index.md) · [Event pin map](#/docs/Micromouse2026/Hardware/ESP32C6.md)

{: .warning}
> Disconnect the motor from the driver **before uploading**. This pin test drives PWM fully on; it does not use the 170/255 motor limit.

## Connect

UNPLUG THE MOTOR FROM THE DRIVER FIRST. The test drives PWM fully HIGH, which would apply the whole 9V to a 6V motor. Meter on DC volts; black probe on GND, red probe on GPIO0 or GPIO2.

## Run and check

After blue startup: green = GPIO0/GPIO2 both 3.3V; yellow = 3.3V/0V; red = 0V/0V. Each stage lasts 2 s. No Serial output.

Use **ESP32C6 Dev Module**, **USB CDC On Boot: Enabled**, and **115200 baud / No Line Ending**. Open this sketch in its own Arduino sketch folder, upload, then press RESET with Serial Monitor open to see startup messages. Motor LED tests also work without Serial Monitor.

## Copy the code into Arduino IDE

1. In Arduino IDE, choose **File → New Sketch**.
2. Save it as <code>pin_test</code>. Arduino IDE creates a folder named <code>pin_test</code> containing <code>pin_test.ino</code>.
3. Expand **Show complete sketch** below and select **COPY**.
4. Replace everything in the Arduino editor with the copied code.
5. Save, choose **ESP32C6 Dev Module** and the correct port, then upload.

Keep the folder and sketch names identical. Arduino requires this structure:

```text
pin_test/
└── pin_test.ino
```

<details>
<summary>Show complete sketch — then select COPY</summary>

```cpp
// =====================================================================
// TOOL - Pin test: are GPIO0 and GPIO2 actually switching?
// =====================================================================
// !! UNPLUG THE MOTOR FROM THE DRIVER FIRST. This sets PWM fully on,
// !! which puts the whole 9V across a 6V motor.
//
// WIRING
//   Nothing extra. Measure GPIO0 and GPIO2 with a multimeter set to DC
//   volts, black probe on GND. Each should read 0V or 3.3V to match the
//   LED stage.
//
// WHAT YOU'LL SEE  (no Serial output - watch the LED, measure with a meter)
//   Multimeter on DC volts, black probe on GND, red probe on the pin:
//       LED        GPIO0    GPIO2
//       BLUE       -        -        2s at startup only
//       GREEN      3.3V     3.3V     2s
//       YELLOW     3.3V     0V       2s
//       RED        0V       0V       2s
//   ...repeats from GREEN.
//
//   What it tells you:
//       Readings match the table -> ESP32 pins are fine; the problem is the
//                                   driver, its power, or the wires to it
//       A pin stuck at 0V        -> damaged pin, or shorted to GND
//       No BLUE at startup       -> this sketch didn't upload; the old one
//                                   is still running
// =====================================================================

#include <Arduino.h>

constexpr uint8_t DIR1_PIN = 0;
constexpr uint8_t PWM1_PIN = 2;

#ifndef RGB_BUILTIN
#define RGB_BUILTIN 8
#endif

void setup() {
  pinMode(DIR1_PIN, OUTPUT);
  pinMode(PWM1_PIN, OUTPUT);   // plain output, deliberately not ledcAttach

  rgbLedWrite(RGB_BUILTIN, 0, 0, 32);
  delay(2000);
}

void loop() {
  digitalWrite(DIR1_PIN, HIGH);
  digitalWrite(PWM1_PIN, HIGH);
  rgbLedWrite(RGB_BUILTIN, 0, 32, 0);   // green = both pins high
  delay(2000);

  digitalWrite(PWM1_PIN, LOW);
  rgbLedWrite(RGB_BUILTIN, 32, 32, 0);  // yellow = DIR high, PWM low
  delay(2000);

  digitalWrite(DIR1_PIN, LOW);
  rgbLedWrite(RGB_BUILTIN, 32, 0, 0);   // red = both pins low
  delay(2000);
}
```

</details>

## Original wiring notes and expected output

These are the comments supplied at the top of this sketch, with comment markers removed. They are the reference for this test.

```text
TOOL - Pin test: are GPIO0 and GPIO2 actually switching?
!! UNPLUG THE MOTOR FROM THE DRIVER FIRST. This sets PWM fully on,
!! which puts the whole 9V across a 6V motor.

WIRING
  Nothing extra. Measure GPIO0 and GPIO2 with a multimeter set to DC
  volts, black probe on GND. Each should read 0V or 3.3V to match the
  LED stage.

WHAT YOU'LL SEE  (no Serial output - watch the LED, measure with a meter)
  Multimeter on DC volts, black probe on GND, red probe on the pin:
      LED        GPIO0    GPIO2
      BLUE       -        -        2s at startup only
      GREEN      3.3V     3.3V     2s
      YELLOW     3.3V     0V       2s
      RED        0V       0V       2s
  ...repeats from GREEN.

  What it tells you:
      Readings match the table -> ESP32 pins are fine; the problem is the
                                  driver, its power, or the wires to it
      A pin stuck at 0V        -> damaged pin, or shorted to GND
      No BLUE at startup       -> this sketch didn't upload; the old one
                                  is still running
```

## Continue

[Back to all steps and tools](#/docs/Micromouse2026/Debug/index.md).

If a step fails, switch off, disconnect the part you just added, and rerun the last passing step. Check the wiring above before moving on. [Extra diagnostic tools](#/docs/Micromouse2026/Debug/index.md).
