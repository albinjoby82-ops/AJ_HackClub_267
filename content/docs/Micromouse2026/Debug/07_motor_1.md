---
title: 07 — Test the left motor
layout: default
parent: Debug Kit
nav_order: 7
---

# 07 — Test the left motor

[Debug kit setup and all steps](#/docs/Micromouse2026/Debug/index.md) · [Event pin map](#/docs/Micromouse2026/Hardware/ESP32C6.md)

{: .warning}
> Lift the wheels before uploading: motor tests start automatically and repeat. Disconnect motor power before rewiring. Keep the supplied SPEED_MAX limit of 170/255 for the kit’s 9V motor supply.

## Connect

Driver DIR1 → GPIO0, PWM1 → GPIO2, VM → battery +. Join battery −, driver GND and ESP32 GND. Connect the left motor power pair to Motor A outputs. Driver VCC → 3V3 only if that pin exists; encoders are not needed.

## Run and check

After the red startup pause: green = forward 2 s, red = stop 1 s, blue = backward 2 s, red = stop 1 s; repeats.

Use **ESP32C6 Dev Module**, **USB CDC On Boot: Enabled**, and **115200 baud / No Line Ending**. Open this sketch in its own Arduino sketch folder, upload, then press RESET with Serial Monitor open to see startup messages. Motor LED tests also work without Serial Monitor.

## Download or copy the code

<a href="../../../../downloads/micromouse-debug-kit/07_motor_1/07_motor_1.ino" download="07_motor_1.ino">Download 07_motor_1.ino</a> · <a href="../../../../downloads/micromouse-debug-kit.zip" download>Download the complete kit ZIP</a>

For an individual download, put <code>07_motor_1.ino</code> inside a folder named <code>07_motor_1</code> (Arduino IDE can create it), or paste the complete code into a new sketch. Extract the ZIP first if using the full kit; each sketch already has its matching folder.

<details>
<summary>Show complete sketch — use COPY to copy all code</summary>

```cpp
// =====================================================================
// STEP 7 - One motor (Motor A): forward, stop, reverse, stop, repeat
// =====================================================================
// WIRING  (motor driver with ONE direction pin + ONE PWM pin per motor)
//   Driver DIR1  -> ESP32 GPIO0
//   Driver PWM1  -> ESP32 GPIO2
//   Driver GND   -> ESP32 GND  AND battery -   (all three joined!)
//   Driver VM    -> battery +
//   Driver VCC   -> ESP32 3V3   (only if your driver board has a VCC pin)
//   Motor's two power wires (M1/M2) -> driver's Motor A outputs
//   Encoder wires (C1, C2, encoder VCC/GND) are not needed for this test.
//
// WHAT YOU'LL SEE  (hold the wheel off the table)
//   LED and motor, repeating forever:
//       RED     1.5s  at startup only - motor off, get your hands clear
//       GREEN   2s    motor spins forward
//       RED     1s    stopped
//       BLUE    2s    motor spins backward
//       RED     1s    stopped
//   Serial Monitor (optional - the LED is enough):
//       FORWARD   speed=+140
//       stop      speed=+0
//       BACKWARD  speed=-140
//       stop      speed=+0
//   Spinning the "wrong" way on GREEN is fine - swap the two motor wires.
//
// IF THE LED CYCLES BUT THE MOTOR DOESN'T MOVE, THE CODE IS FINE. Check:
//   PWM1 wire actually connected  |  DIR1 wire connected
//   Driver GND joined to ESP32 GND  |  battery on VM and not flat
//   Driver STBY / EN / SLP pin (if it has one) tied HIGH to 3V3
//
// Speed is capped at 170/255 = about 6V average from a 9V battery, the
// N20 motors' rating. Don't raise SPEED_MAX.
// =====================================================================

#include <Arduino.h>

constexpr uint8_t DIR1_PIN = 0;
constexpr uint8_t PWM1_PIN = 2;

constexpr uint32_t PWM_FREQ = 20000;  // 20 kHz, above hearing
constexpr uint8_t  PWM_RES  = 8;      // duty 0..255

constexpr int16_t SPEED_MAX  = 170;
constexpr int16_t SPEED_TEST = 140;

#ifndef RGB_BUILTIN
#define RGB_BUILTIN 8
#endif

// Sign = direction, size = speed. Clamped so nothing can exceed SPEED_MAX.
void setMotor(int16_t speed) {
  speed = constrain(speed, -SPEED_MAX, SPEED_MAX);
  digitalWrite(DIR1_PIN, speed >= 0 ? HIGH : LOW);
  ledcWrite(PWM1_PIN, abs(speed));
}

void step(const char* label, int16_t speed, uint8_t r, uint8_t g, uint8_t b, uint32_t ms) {
  rgbLedWrite(RGB_BUILTIN, r, g, b);
  setMotor(speed);
  Serial.printf("%-9s speed=%+d\n", label, speed);
  delay(ms);
}

void setup() {
  Serial.begin(115200);

  pinMode(DIR1_PIN, OUTPUT);
  digitalWrite(DIR1_PIN, LOW);
  ledcAttach(PWM1_PIN, PWM_FREQ, PWM_RES);
  ledcWrite(PWM1_PIN, 0);  // motor off until we say so

  Serial.println("\nSTEP 7: one motor");
  rgbLedWrite(RGB_BUILTIN, 32, 0, 0);
  delay(1500);  // a moment to get your hands clear
}

void loop() {
  step("FORWARD",  SPEED_TEST, 0, 32, 0, 2000);
  step("stop",     0,          32, 0, 0, 1000);
  step("BACKWARD", -SPEED_TEST, 0, 0, 32, 2000);
  step("stop",     0,          32, 0, 0, 1000);
}
```

</details>

## Original wiring notes and expected output

These are the comments supplied at the top of this sketch, with comment markers removed. They are the reference for this test.

```text
STEP 7 - One motor (Motor A): forward, stop, reverse, stop, repeat
WIRING  (motor driver with ONE direction pin + ONE PWM pin per motor)
  Driver DIR1  -> ESP32 GPIO0
  Driver PWM1  -> ESP32 GPIO2
  Driver GND   -> ESP32 GND  AND battery -   (all three joined!)
  Driver VM    -> battery +
  Driver VCC   -> ESP32 3V3   (only if your driver board has a VCC pin)
  Motor's two power wires (M1/M2) -> driver's Motor A outputs
  Encoder wires (C1, C2, encoder VCC/GND) are not needed for this test.

WHAT YOU'LL SEE  (hold the wheel off the table)
  LED and motor, repeating forever:
      RED     1.5s  at startup only - motor off, get your hands clear
      GREEN   2s    motor spins forward
      RED     1s    stopped
      BLUE    2s    motor spins backward
      RED     1s    stopped
  Serial Monitor (optional - the LED is enough):
      FORWARD   speed=+140
      stop      speed=+0
      BACKWARD  speed=-140
      stop      speed=+0
  Spinning the "wrong" way on GREEN is fine - swap the two motor wires.

IF THE LED CYCLES BUT THE MOTOR DOESN'T MOVE, THE CODE IS FINE. Check:
  PWM1 wire actually connected  |  DIR1 wire connected
  Driver GND joined to ESP32 GND  |  battery on VM and not flat
  Driver STBY / EN / SLP pin (if it has one) tied HIGH to 3V3

Speed is capped at 170/255 = about 6V average from a 9V battery, the
N20 motors' rating. Don't raise SPEED_MAX.
```

## Continue

Previous: [06 — Test all sensors together](#/docs/Micromouse2026/Debug/06_tof_3_imu.md). Next: [08 — Test both motors](#/docs/Micromouse2026/Debug/08_motors_2.md).

If a step fails, switch off, disconnect the part you just added, and rerun the last passing step. Check the wiring above before moving on. [Extra diagnostic tools](#/docs/Micromouse2026/Debug/index.md).
