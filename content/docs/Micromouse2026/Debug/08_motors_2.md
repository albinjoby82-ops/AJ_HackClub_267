---
title: 08 — Test both motors
layout: default
parent: Debug Kit
nav_order: 8
---

# 08 — Test both motors

[Debug kit setup and all steps](#/docs/Micromouse2026/Debug/index.md) · [Event pin map](#/docs/Micromouse2026/Hardware/ESP32C6.md)

{: .warning}
> Lift the wheels before uploading: motor tests start automatically and repeat. Disconnect motor power before rewiring. Keep the supplied SPEED_MAX limit of 170/255 for the kit’s 9V motor supply.

## Connect

Keep step 7 wiring; add DIR2 → GPIO3 and PWM2 → GPIO10, then right motor → Motor B outputs. PWM2 is GPIO10. Keep both wheels off the table.

## Run and check

Green = both forward, blue = both backward, yellow = spin left, purple = spin right; each lasts 2 s with a red 1 s stop between.

Use **ESP32C6 Dev Module**, **USB CDC On Boot: Enabled**, and **115200 baud / No Line Ending**. Open this sketch in its own Arduino sketch folder, upload, then press RESET with Serial Monitor open to see startup messages. Motor LED tests also work without Serial Monitor.

## Copy the code into Arduino IDE

1. In Arduino IDE, choose **File → New Sketch**.
2. Save it as <code>08_motors_2</code>. Arduino IDE creates a folder named <code>08_motors_2</code> containing <code>08_motors_2.ino</code>.
3. Expand **Show complete sketch** below and select **COPY**.
4. Replace everything in the Arduino editor with the copied code.
5. Save, choose **ESP32C6 Dev Module** and the correct port, then upload.

Keep the folder and sketch names identical. Arduino requires this structure:

```text
08_motors_2/
└── 08_motors_2.ino
```

<details>
<summary>Show complete sketch — then select COPY</summary>

```cpp
// =====================================================================
// STEP 8 - Both motors: forward, backward, spin left, spin right
// =====================================================================
// WIRING  (= step 7 + Motor B)
//   Driver DIR1 -> ESP32 GPIO0     (already wired in step 7)
//   Driver PWM1 -> ESP32 GPIO2     (already wired in step 7)
//   Driver DIR2 -> ESP32 GPIO3     (new)
//   Driver PWM2 -> ESP32 GPIO10    (new - NOT GPIO5, that's a C6 strapping pin)
//   Driver GND  -> ESP32 GND  AND battery -
//   Driver VM   -> battery +
//   Driver VCC  -> ESP32 3V3   (only if your driver board has a VCC pin)
//   Left motor  -> driver Motor A outputs
//   Right motor -> driver Motor B outputs
//
// WHAT YOU'LL SEE  (hold the robot up, wheels in the air)
//   LED and wheels, repeating forever (RED 1s stop between each):
//       GREEN   2s   both wheels forward
//       BLUE    2s   both wheels backward
//       YELLOW  2s   spin LEFT:  left wheel back, right wheel forward
//       PURPLE  2s   spin RIGHT: left wheel forward, right wheel back
//   Serial Monitor (optional - the LED is enough):
//       FORWARD     left=+140 right=+140
//       stop        left=  +0 right=  +0
//       BACKWARD    left=-140 right=-140
//       stop        left=  +0 right=  +0
//       SPIN LEFT   left=-140 right=+140
//       stop        left=  +0 right=  +0
//       SPIN RIGHT  left=+140 right=-140
//       stop        left=  +0 right=  +0
//
// A wheel going the wrong way? Swap THAT motor's two wires.
// Left and right mixed up? Swap which motor goes to Motor A / Motor B.
// Motor A works but B doesn't? Check the DIR2 and PWM2 wires.
//
// Speed is capped at 170/255 = about 6V average from a 9V battery.
// =====================================================================

#include <Arduino.h>

constexpr uint8_t DIR1_PIN = 0;   // Motor A = left
constexpr uint8_t PWM1_PIN = 2;
constexpr uint8_t DIR2_PIN = 3;   // Motor B = right
constexpr uint8_t PWM2_PIN = 10;

constexpr uint32_t PWM_FREQ = 20000;
constexpr uint8_t  PWM_RES  = 8;

constexpr int16_t SPEED_MAX  = 170;
constexpr int16_t SPEED_TEST = 140;

#ifndef RGB_BUILTIN
#define RGB_BUILTIN 8
#endif

void setMotor(uint8_t dirPin, uint8_t pwmPin, int16_t speed) {
  speed = constrain(speed, -SPEED_MAX, SPEED_MAX);
  digitalWrite(dirPin, speed >= 0 ? HIGH : LOW);
  ledcWrite(pwmPin, abs(speed));
}

void drive(const char* label, int16_t left, int16_t right,
           uint8_t r, uint8_t g, uint8_t b, uint32_t ms) {
  rgbLedWrite(RGB_BUILTIN, r, g, b);
  setMotor(DIR1_PIN, PWM1_PIN, left);
  setMotor(DIR2_PIN, PWM2_PIN, right);
  Serial.printf("%-11s left=%+4d right=%+4d\n", label, left, right);
  delay(ms);
}

void setup() {
  Serial.begin(115200);

  pinMode(DIR1_PIN, OUTPUT);
  pinMode(DIR2_PIN, OUTPUT);
  digitalWrite(DIR1_PIN, LOW);
  digitalWrite(DIR2_PIN, LOW);
  ledcAttach(PWM1_PIN, PWM_FREQ, PWM_RES);
  ledcAttach(PWM2_PIN, PWM_FREQ, PWM_RES);
  ledcWrite(PWM1_PIN, 0);
  ledcWrite(PWM2_PIN, 0);

  Serial.println("\nSTEP 8: both motors");
  rgbLedWrite(RGB_BUILTIN, 32, 0, 0);
  delay(1500);
}

void loop() {
  const int16_t s = SPEED_TEST;
  drive("FORWARD",    s,  s,  0, 32,  0, 2000);
  drive("stop",       0,  0, 32,  0,  0, 1000);
  drive("BACKWARD",  -s, -s,  0,  0, 32, 2000);
  drive("stop",       0,  0, 32,  0,  0, 1000);
  drive("SPIN LEFT", -s,  s, 32, 32,  0, 2000);
  drive("stop",       0,  0, 32,  0,  0, 1000);
  drive("SPIN RIGHT", s, -s, 32,  0, 32, 2000);
  drive("stop",       0,  0, 32,  0,  0, 1000);
}
```

</details>

## Original wiring notes and expected output

These are the comments supplied at the top of this sketch, with comment markers removed. They are the reference for this test.

```text
STEP 8 - Both motors: forward, backward, spin left, spin right
WIRING  (= step 7 + Motor B)
  Driver DIR1 -> ESP32 GPIO0     (already wired in step 7)
  Driver PWM1 -> ESP32 GPIO2     (already wired in step 7)
  Driver DIR2 -> ESP32 GPIO3     (new)
  Driver PWM2 -> ESP32 GPIO10    (new - NOT GPIO5, that's a C6 strapping pin)
  Driver GND  -> ESP32 GND  AND battery -
  Driver VM   -> battery +
  Driver VCC  -> ESP32 3V3   (only if your driver board has a VCC pin)
  Left motor  -> driver Motor A outputs
  Right motor -> driver Motor B outputs

WHAT YOU'LL SEE  (hold the robot up, wheels in the air)
  LED and wheels, repeating forever (RED 1s stop between each):
      GREEN   2s   both wheels forward
      BLUE    2s   both wheels backward
      YELLOW  2s   spin LEFT:  left wheel back, right wheel forward
      PURPLE  2s   spin RIGHT: left wheel forward, right wheel back
  Serial Monitor (optional - the LED is enough):
      FORWARD     left=+140 right=+140
      stop        left=  +0 right=  +0
      BACKWARD    left=-140 right=-140
      stop        left=  +0 right=  +0
      SPIN LEFT   left=-140 right=+140
      stop        left=  +0 right=  +0
      SPIN RIGHT  left=+140 right=-140
      stop        left=  +0 right=  +0

A wheel going the wrong way? Swap THAT motor's two wires.
Left and right mixed up? Swap which motor goes to Motor A / Motor B.
Motor A works but B doesn't? Check the DIR2 and PWM2 wires.

Speed is capped at 170/255 = about 6V average from a 9V battery.
```

## Continue

Previous: [07 — Test the left motor](#/docs/Micromouse2026/Debug/07_motor_1.md). All eight checks complete. Use the extra tools below when a subsystem needs more diagnosis.

If a step fails, switch off, disconnect the part you just added, and rerun the last passing step. Check the wiring above before moving on. [Extra diagnostic tools](#/docs/Micromouse2026/Debug/index.md).
