---
title: H4 - 3x VL53L0X Distance Sensors
layout: default
parent: Hardware
nav_order: 4
---

# H4 - 3x VL53L0X Distance Sensors

The debug kit adds left, front and right sensors one at a time. They share power and I2C; each needs its own XSHUT wire.

![Three VL53L0X sensors sharing SDA6 and SCL7, with XSHUT on GPIO18 GPIO19 GPIO20](../../assets/images/VL53L0X-3-sensor-wiring.svg)

## Exact wiring

Power the controller over USB. Connect every fitted ToF board as follows:

| Sensor pin | ESP32-C6 |
|---|---|
| VIN | 3V3 |
| GND | GND |
| SDA | GPIO6, shared |
| SCL | GPIO7, shared |
| GPIO1, if exposed | unused by these sketches; leave unconnected |

| Position | XSHUT | Address after initialization |
|---|---|---|
| Left (L) | GPIO18 | `0x30` |
| Front (F) | GPIO19 | `0x31` |
| Right (R) | GPIO20 | `0x29` |

Use boards with an accessible XSHUT pin. **Only connect the sensors listed in the current step.** An extra powered sensor with XSHUT unconnected wakes at `0x29` and can break the others. The IMU may stay connected: its `0x68` address does not clash.

## Startup addresses

All ToFs wake at `0x29`. The sketches hold the connected sensors in shutdown and enable them in order:

1. Hold their XSHUT pins LOW.
2. Enable left on GPIO18, initialize it and assign `0x30`.
3. Enable front on GPIO19, initialize it and assign `0x31`.
4. Enable right on GPIO20 and keep it at **`0x29`**.

Initialization repeats at startup. The final mapping is **L 0x30, F 0x31, R 0x29**.

## Library and test sequence

Install **VL53L0X by Pololu**, not `Adafruit_VL53L0X`. Use Arduino-ESP32 **3.0.0 or newer**, board **ESP32C6 Dev Module**, **USB CDC On Boot: Enabled**, and Serial Monitor at **115200 baud**. Open the monitor and press RESET after upload to see startup results.

| Sketch | Connect | Expected startup |
|---|---|---|
| [03_tof_1](#/docs/Micromouse2026/Debug/03_tof_1.md) | left only | L PASS; `1/1 sensors OK` |
| [04_tof_2](#/docs/Micromouse2026/Debug/04_tof_2.md) | left and front | L/F PASS; `2/2 sensors OK` |
| [05_tof_3](#/docs/Micromouse2026/Debug/05_tof_3.md) | left, front and right | L/F/R PASS; `3/3 sensors OK` |
| [06_tof_3_imu](#/docs/Micromouse2026/Debug/06_tof_3_imu.md) | all three plus IMU | all ToFs and IMU at `0x68` PASS |

Step 5 should begin:

```text
STEP 5: three ToF sensors
  ToF L  XSHUT=GPIO18  addr=0x30  PASS
  ToF F  XSHUT=GPIO19  addr=0x31  PASS
  ToF R  XSHUT=GPIO20  addr=0x29  PASS
3/3 sensors OK
```

Wave a hand before each sensor individually: only that column should change. `L:142 mm` is about 14 cm; moving closer reduces the value. **`---` means an out-of-range reading or a read timeout; `FAIL` means initialization failed.** Nothing in range is normal. If `---` persists with a nearby wall, check wiring and rerun the previous step.

In step 6, keep the robot still for the first second for gyro calibration. Distances should follow your hand and heading should change about 90 degrees per quarter turn. The IMU needs no additional library.

## Troubleshooting

| Symptom | Check |
|---|---|
| FAIL at startup and in every reading | VIN → 3V3, GND, SDA6, SCL7 and that sensor's XSHUT |
| Covering left changes F | XSHUT wires are swapped; restore L18/F19/R20 |
| Adding a sensor breaks a working one | remove powered sensors not listed in the step; check independent XSHUT wires |
| `---` with nothing in front | normal; try a nearby hand |
| Passed alone but fails in step 6 | disconnect the last addition and repeat the earlier passing test |
| Compile error involving the ToF API | confirm the library is VL53L0X by Pololu |

## What the scanner proves

[i2c_scan](#/docs/Micromouse2026/Debug/i2c_scan.md) uses SDA6/SCL7 and drives XSHUT18/19/20 HIGH together. It does **not** assign separate ToF addresses. With freshly powered sensors and the IMU connected, expect:

```text
idle SDA=1 SCL=1 (both should be 1)
Scanning...
  found 0x29
  found 0x68
2 device(s)
```

The scan repeats every three seconds. All three ToFs can appear as one `0x29` response here; that does not prove each works independently. Use steps 3–5 for that. Power-cycle sensors if they retained addresses from an earlier sketch and you need to reproduce startup addresses.

If idle lines are LOW, check loose wires, missing power, shorts to GND and pull-ups. If both idle HIGH but no devices respond, check swapped SDA/SCL. If one kind of device is missing, check its four power and I2C wires.

See the [controller pin map](#/docs/Micromouse2026/Hardware/ESP32C6.md) and [debug index](#/docs/Micromouse2026/Debug/index.md).
