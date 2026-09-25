---
title: Debug Kit
layout: default
parent: Micromouse 2026 Resources
nav_order: 4
---

# Test your mouse, one part at a time

Start with USB and the onboard LED. Add the IMU, one distance sensor at a time, then the motors. Each page has copyable code, its original wiring comments, expected output and exact folder instructions. Fix a failing step before adding the next part.

[Start step 1](#/docs/Micromouse2026/Debug/01_led_red.md) · [Event wiring map](#/docs/Micromouse2026/Hardware/ESP32C6.md)

## Arduino setup

1. In Arduino IDE, add <code>https://espressif.github.io/arduino-esp32/package_esp32_index.json</code> under File → Preferences → Additional Board Manager URLs.
2. In Boards Manager, install **esp32 by Espressif Systems, version 3.0.0 or newer**, as specified by the supplied kit.
3. Select **ESP32C6 Dev Module** and the board’s port. Set **Tools → USB CDC On Boot → Enabled**.
4. Set Serial Monitor to **115200 baud**, **No Line Ending**.
5. For steps 3–6, install **VL53L0X by Pololu**. Do not substitute <code>Adafruit_VL53L0X</code>. The IMU sketches need no extra library.
6. Open the chosen check, create a new Arduino sketch with the name shown, expand its complete code and select **COPY**. Replace the new sketch with that code, save and upload it. Each guide shows the required folder structure.

Power the controller from USB for these tests. Sensors and encoder VCC use **3V3**. Motor-driver VM uses the motor battery, with battery −, driver GND and ESP32 GND joined. The motor tests assume **9V** and cap PWM at **170/255**; keep that cap. Read [battery and power](#/docs/Micromouse2026/Hardware/BuckConverter.md) before step 7.

## The eight checks

| Step | Connect / test | Pass looks like |
|---|---|---|
| [01 — Check the onboard LED](#/docs/Micromouse2026/Debug/01_led_red.md) | USB only; no external wiring. | Solid red LED and an “alive” line every second. |
| [02 — Test the IMU](#/docs/Micromouse2026/Debug/02_imu.md) | MPU-6050 / GY-521: VCC → 3V3, GND → GND, SDA → GPIO6, SCL → GPIO7. Leave XDA, XCL, AD0 and INT unconnected. Test the IMU alone on I²C first. | PASS, gyroZ near zero while still, and roughly 90° heading change for a quarter turn. Keep still during startup calibration. |
| [03 — Add the left distance sensor](#/docs/Micromouse2026/Debug/03_tof_1.md) | Left ToF: VIN → 3V3, GND → GND, SDA → GPIO6, SCL → GPIO7, XSHUT → GPIO18. The IMU can stay connected. Leave front and right ToF disconnected. | 1/1 sensors OK; L at 0x30. The distance changes as your hand moves. |
| [04 — Add the front distance sensor](#/docs/Micromouse2026/Debug/04_tof_2.md) | Keep the left sensor. Add front ToF to the shared 3V3/GND/GPIO6 SDA/GPIO7 SCL connections, with its XSHUT → GPIO19. Leave right ToF disconnected. | 2/2 sensors OK; L at 0x30 and F at 0x31. Cover each sensor in turn and check the matching column changes. |
| [05 — Add the right distance sensor](#/docs/Micromouse2026/Debug/05_tof_3.md) | Keep left and front. Add right ToF to the shared power and I²C connections, with its XSHUT → GPIO20. | 3/3 sensors OK; L at 0x30, F at 0x31, R at 0x29. The right sensor keeps the default address. |
| [06 — Test all sensors together](#/docs/Micromouse2026/Debug/06_tof_3_imu.md) | Use the wiring from steps 2–5. All four boards share 3V3/GND, SDA GPIO6 and SCL GPIO7. ToF XSHUT: left GPIO18, front GPIO19, right GPIO20. IMU XDA/XCL/AD0/INT stay unconnected. | Three ToF PASS messages plus IMU PASS; distance and heading values share one line. Keep still for gyro calibration. |
| [07 — Test the left motor](#/docs/Micromouse2026/Debug/07_motor_1.md) | Driver DIR1 → GPIO0, PWM1 → GPIO2, VM → battery +. Join battery −, driver GND and ESP32 GND. Connect the left motor power pair to Motor A outputs. Driver VCC → 3V3 only if that pin exists; encoders are not needed. | After the red startup pause: green = forward 2 s, red = stop 1 s, blue = backward 2 s, red = stop 1 s; repeats. |
| [08 — Test both motors](#/docs/Micromouse2026/Debug/08_motors_2.md) | Keep step 7 wiring; add DIR2 → GPIO3 and PWM2 → GPIO10, then right motor → Motor B outputs. PWM2 is GPIO10. Keep both wheels off the table. | Green = both forward, blue = both backward, yellow = spin left, purple = spin right; each lasts 2 s with a red 1 s stop between. |

Only connect the ToF sensors listed for the step you are running. An extra powered sensor with XSHUT unconnected wakes at <code>0x29</code> and can clash. Once added in step 2, the IMU can stay connected during the ToF steps.

When you rerun an earlier ToF step on an assembled mouse, disconnect power from ToF boards that step does not control. Step 3 controls only left; step 4 controls left and front.

## Extra tools

| Tool | When to use it |
|---|---|
| [Tool — Scan the I²C bus](#/docs/Micromouse2026/Debug/i2c_scan.md) | Idle SDA=1 SCL=1. With IMU and ToF connected, expect 0x68 and 0x29. This tool wakes all ToFs at their default address: one 0x29 entry does not prove all three work. |
| [Tool — Check motor control pins](#/docs/Micromouse2026/Debug/pin_test.md) | After blue startup: green = GPIO0/GPIO2 both 3.3V; yellow = 3.3V/0V; red = 0V/0V. Each stage lasts 2 s. No Serial output. |
| [Tool — Sweep motor power](#/docs/Micromouse2026/Debug/motor_sweep.md) | Blue startup, then a green forward ramp and a red backward ramp. Power rises to 170/255, holds, then stops. No Serial output. |
| [Tool — Test the Motor A encoder](#/docs/Micromouse2026/Debug/encoder_test.md) | Counts change while the motor runs at PWM 85. Serial commands: s = stop, g = go, z = zero count. Green = running; red = stopped. |
| [Tool — Live IMU visualizer](#/docs/Micromouse2026/Debug/imu_visualizer.md) | A 3D board, heading, tilt and graphs follow your board. Keep still for calibration; the page can zero heading and recalibrate. |

{: .warning}
> **Pin test: unplug the motor before uploading.** It drives PWM fully HIGH and would apply the whole 9V to a 6V motor. All moving-motor tests must run with the wheels raised.

## If something fails

| Symptom | First check |
|---|---|
| No upload port | Use a USB data cable, choose the COM port; if needed hold BOOT, tap RESET, then release BOOT and upload. |
| Red LED but Serial is blank | Enable USB CDC On Boot, upload again, use 115200 baud, open the monitor and press RESET. |
| Old behavior after copying a sketch | Confirm the intended code is in the active Arduino tab, save, then upload it. Copying alone does not flash the board. |
| No I²C devices | Check power, ground and GPIO6/7. Run the I²C scan; step 2 can also detect swapped SDA/SCL. Use MPU SDA/SCL, leave XDA/XCL/AD0/INT unconnected. |
| One ToF column fails or the wrong column changes | Check that sensor’s XSHUT wire: left 18, front 19, right 20. Recheck the last passing step with extra ToFs disconnected. |
| Motors stay still while LED cycles | Check PWM and DIR wires, common ground, battery on VM and battery charge. If present, VCC needs 3V3 and STBY/EN/SLP must be HIGH. |
| Motor hums without turning | Use motor sweep; check battery sag and a jammed wheel or gearbox. Do not raise SPEED_MAX. |
| Encoder stays at zero while turning | Check encoder 3V3/GND and C1 GPIO21, C2 GPIO22. Use the encoder test. |

## Source of these instructions

The embedded sketches and visualizer code are copied unchanged from the event’s <code>micromouse-debug-kit</code>. Wiring and expected results come from their top-of-file comments. Each page includes those original comments and the complete sketch, so you can compare the instructions directly with what you upload.
