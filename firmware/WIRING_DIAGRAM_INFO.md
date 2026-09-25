# Micromouse Wiring — ESP32-C6

This matches the physical wiring and every sketch in `firmware/`. If you rewire,
change the pin constants at the top of **every** sketch to match.

All 3V3 pins are one net, all GND pins are one net. Encoder VCC max 3.6 V.

## ESP32-C6 pins

| GPIO | Connects to | Direction |
|------|-------------|-----------|
| 0  | DRI0044 DIR1 (left motor direction) | out |
| 2  | DRI0044 PWM1 (left motor speed, 20 kHz, 8-bit) | out |
| 3  | DRI0044 DIR2 (right motor direction) | out |
| 10 | DRI0044 PWM2 (right motor speed, 20 kHz, 8-bit) | out |
| 21 | Left encoder C1 (A) | in, pull-up, interrupt |
| 22 | Left encoder C2 (B) | in, pull-up |
| 11 | Right encoder C1 (A) | in, pull-up, interrupt |
| 23 | Right encoder C2 (B) | in, pull-up |
| 6  | I2C SDA (all 4 I2C devices) | bus, 400 kHz |
| 7  | I2C SCL (all 4 I2C devices) | bus, 400 kHz |
| 18 | VL53L0X Left XSHUT | out |
| 19 | VL53L0X Front XSHUT | out |
| 20 | VL53L0X Right XSHUT | out |

Do not use: GPIO 4, 5, 8, 9, 15 (boot strapping; 8 is also the onboard RGB LED)
and GPIO 12, 13 (USB). There is no separate status LED; state prints on Serial.

## I2C devices (SDA 6, SCL 7)

| Device | XSHUT | Address |
|--------|-------|---------|
| VL53L0X Left  | GPIO 18 | 0x30 (re-addressed from 0x29 at boot) |
| VL53L0X Front | GPIO 19 | 0x31 (re-addressed from 0x29 at boot) |
| VL53L0X Right | GPIO 20 | 0x32 (re-addressed from 0x29 at boot) |
| MPU-6050 IMU  | none    | 0x68 |

All four: VCC → 3V3, GND → GND.

## DRI0044 motor driver

| Driver pin | Connects to |
|------------|-------------|
| DIR1 / PWM1 | GPIO 0 / GPIO 2 |
| DIR2 / PWM2 | GPIO 3 / GPIO 10 |
| M1+ / M1− | Left motor M+ / M− |
| M2+ / M2− | Right motor M+ / M− |
| VM / GND | Motor battery (check the DRI0044 datasheet for its range) |

## GA12-N20 motors with encoders (×2)

| Encoder pin | Left motor | Right motor |
|-------------|-----------|-------------|
| C1 (A) | GPIO 21 | GPIO 11 |
| C2 (B) | GPIO 22 | GPIO 23 |
| VCC | 3V3 | 3V3 |
| GND | GND | GND |

## Numbers set in the code

| Constant | Value | How it was found |
|----------|-------|------------------|
| `WHEEL_DIAMETER_MM` | 44.0 | Measured |
| `ENC_TICKS_PER_REV` | 402.0 | Measured by hand turn: L 395, R 408, averaged |
| `L_DIR_SIGN` / `R_DIR_SIGN` | +1 | Check: `motor_encoder_test`, send `d` |
