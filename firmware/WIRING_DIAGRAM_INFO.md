# Micromouse Wiring Diagram Reference

This document contains all electrical connections for the Dublin Micromouse 2026. Use this to generate a complete wiring diagram showing sensor, motor, encoder, and power connections.

---

## ESP32-C6-DevKitC-1 Pin Assignments

### Communication Buses
| Function | GPIO | Type | Details |
|----------|------|------|---------|
| I2C SDA | 6 | Input/Output | Shared bus for all I2C devices (400 kHz clock) |
| I2C SCL | 7 | Input/Output | Shared bus for all I2C devices (400 kHz clock) |

### Left Motor Control
| Function | GPIO | Type | Details |
|----------|------|------|---------|
| Direction | 19 | Output | HIGH = forward, LOW = backward |
| PWM Speed | 18 | Output | 20 kHz, 8-bit (0-255), 0 = stop, 255 = max |

### Right Motor Control
| Function | GPIO | Type | Details |
|----------|------|------|---------|
| Direction | 21 | Output | HIGH = forward, LOW = backward |
| PWM Speed | 20 | Output | 20 kHz, 8-bit (0-255), 0 = stop, 255 = max |

### Left Encoder (Quadrature)
| Function | GPIO | Type | Details |
|----------|------|------|---------|
| Channel A | 0 | Input | Interrupt on CHANGE, pulled HIGH |
| Channel B | 1 | Input | Interrupt on CHANGE, pulled HIGH |
| Counts per rev | — | — | ~210 ticks (measure with motor_encoder_test) |

### Right Encoder (Quadrature)
| Function | GPIO | Type | Details |
|----------|------|------|---------|
| Channel A | 22 | Input | Interrupt on CHANGE, pulled HIGH |
| Channel B | 23 | Input | Interrupt on CHANGE, pulled HIGH |
| Counts per rev | — | — | ~210 ticks (measure with motor_encoder_test) |

### ToF Sensor Control Pins (Re-addressing)
| Sensor | XSHUT GPIO | I2C Address (default) | I2C Address (final) |
|--------|------------|----------------------|---------------------|
| LEFT | 2 | 0x29 | 0x30 |
| FRONT | 3 | 0x29 | 0x31 |
| RIGHT | 10 | 0x29 | 0x32 |

### Status LED
| Function | GPIO | Type | Details |
|----------|------|------|---------|
| Status LED | 11 | Output | HIGH = active (blink on error) |

### Pins to Avoid (ESP32-C6 Strapping Pins)
- GPIO 4, 5, 8, 9, 15: Do not use (strapping pins)
- GPIO 12, 13: Do not use (USB pins)

---

## I2C Device Addresses (Shared SDA=6, SCL=7, 400 kHz)

### VL53L0X Time-of-Flight Sensors
All three sensors ship at default address `0x29`. They are re-addressed at boot via their XSHUT pins:

| Sensor Position | XSHUT GPIO | Boot Sequence | Final I2C Address | Measurement Mode |
|-----------------|------------|---------------|--------------------|------------------|
| **LEFT** (90° left) | 2 | 1. Set XSHUT LOW (all OFF) → 2. Raise XSHUT HIGH (LEFT only) → Assign 0x30 | 0x30 | Continuous, 20 ms budget |
| **FRONT** (straight) | 3 | 3. Raise XSHUT HIGH (FRONT only) → Assign 0x31 | 0x31 | Continuous, 20 ms budget |
| **RIGHT** (90° right) | 10 | 4. Raise XSHUT HIGH (RIGHT only) → Assign 0x32 | 0x32 | Continuous, 20 ms budget |

**Boot order is critical:** Power cycle re-addresses all three sensors every startup.

### MPU-6050 6-Axis IMU
| Device | I2C Address | Function | Usage |
|--------|-------------|----------|-------|
| MPU-6050 | 0x68 | Gyro Z-axis (heading) + accelerometers | Closed-loop heading hold during turns and straight drive |

**No XSHUT pin:** Always at 0x68, powered from 3.3V rail.

---

## Motor Driver: DRI0044 Dual Motor Driver

### Power Connections
| Pin | Voltage | Source | Purpose |
|-----|---------|--------|---------|
| VCC | 5 V | Buck converter or USB | Logic supply (gate drive) |
| VM | 2.5–12 V | Battery via fuse | Motor supply (commutation) |
| GND | Ground | Common with battery negative | Reference for all logic |

### Motor 1 (Left Wheel)
| Driver Pin | Source | Type | Function |
|------------|--------|------|----------|
| DIR1 | GPIO 19 | Output | Direction control (HIGH = forward) |
| PWM1 | GPIO 18 | Output | Speed control (0–255 PWM) |
| M1+ | Left motor positive | Motor | Left wheel forward connection |
| M1− | Left motor negative | Motor | Left wheel reverse connection |

### Motor 2 (Right Wheel)
| Driver Pin | Source | Type | Function |
|------------|--------|------|----------|
| DIR2 | GPIO 21 | Output | Direction control (HIGH = forward) |
| PWM2 | GPIO 20 | Output | Speed control (0–255 PWM) |
| M2+ | Right motor positive | Motor | Right wheel forward connection |
| M2− | Right motor negative | Motor | Right wheel reverse connection |

---

## Motors and Encoders: GA12-N20 (Two Units)

### Left Motor & Encoder
| Connection | Source | Destination | Voltage | Notes |
|-----------|--------|-------------|---------|-------|
| Motor Power+ | DRI0044 M1+ | Motor pin 1 | VM (battery) | From motor driver |
| Motor Power− | DRI0044 M1− | Motor pin 2 | VM (battery) | From motor driver |
| Encoder A | Motor encoder pin A | GPIO 0 | 3.3 V logic | Pulls HIGH, interrupt on CHANGE |
| Encoder B | Motor encoder pin B | GPIO 1 | 3.3 V logic | Pulls HIGH, interrupt on CHANGE |
| Encoder VCC | 3.3 V rail | Motor encoder VCC | 3.3 V | **Max 3.6 V** — do not exceed |
| Encoder GND | Common ground | Motor encoder GND | Ground | Shared with battery negative |

### Right Motor & Encoder
| Connection | Source | Destination | Voltage | Notes |
|-----------|--------|-------------|---------|-------|
| Motor Power+ | DRI0044 M2+ | Motor pin 1 | VM (battery) | From motor driver |
| Motor Power− | DRI0044 M2− | Motor pin 2 | VM (battery) | From motor driver |
| Encoder A | Motor encoder pin A | GPIO 22 | 3.3 V logic | Pulls HIGH, interrupt on CHANGE |
| Encoder B | Motor encoder pin B | GPIO 23 | 3.3 V logic | Pulls HIGH, interrupt on CHANGE |
| Encoder VCC | 3.3 V rail | Motor encoder VCC | 3.3 V | **Max 3.6 V** — do not exceed |
| Encoder GND | Common ground | Motor encoder GND | Ground | Shared with battery negative |

---

## VL53L0X Time-of-Flight Sensor Connections (× 3)

Each sensor has identical pinout; they are distinguished by their XSHUT GPIO.

### Power
| Pin | Connection | Voltage | Notes |
|-----|-----------|---------|-------|
| VCC | 3.3 V rail | 3.3 V | Shared with all other logic |
| GND | Common ground | Ground | Shared with battery negative |

### Communication (I2C)
| Pin | Connection | Voltage | Type |
|-----|-----------|---------|------|
| SDA | GPIO 6 | 3.3 V | Shared bus, pull-ups on board |
| SCL | GPIO 7 | 3.3 V | Shared bus, pull-ups on board |

### Control (Re-addressing)
| Pin | Connection | Voltage | Type | Details |
|-----|-----------|---------|------|---------|
| XSHUT | GPIO 2 (LEFT) / 3 (FRONT) / 10 (RIGHT) | 3.3 V | Output | LOW = OFF, HIGH = ON |

---

## MPU-6050 6-Axis IMU

### Power
| Pin | Connection | Voltage | Notes |
|-----|-----------|---------|-------|
| VCC | 3.3 V rail | 3.3 V | Shared with all other logic |
| GND | Common ground | Ground | Shared with battery negative |

### Communication (I2C)
| Pin | Connection | Voltage | Type |
|-----|-----------|---------|------|
| SDA | GPIO 6 | 3.3 V | Shared bus, pull-ups on board |
| SCL | GPIO 7 | 3.3 V | Shared bus, pull-ups on board |
| Address | — | — | Fixed at 0x68 (no XSHUT) |

### Internal Registers Used
| Register | Address | Function | Usage |
|----------|---------|----------|-------|
| PWR_MGMT_1 | 0x6B | Power control | Enable gyro (set to 0x00 at boot) |
| GYRO_ZOUT_H | 0x47 | Gyro Z-axis reading (MSB) | Read heading rate for closed-loop turns |

**Gyro sensitivity:** 131 LSB per °/s (see calibration constants below)

---

## Power Distribution

```
Battery (6-9V nominal) ─── Fuse ──┬─→ Motor supply (VM) ─→ DRI0044 motor outputs
                                   │
                                   └─→ Buck Converter (6V → 3.3V)
                                       │
                                       └─→ 3.3V Rail (all logic, sensors, encoders)
                                           ├─ ESP32-C6 (VCC & GND)
                                           ├─ MPU-6050 (VCC & GND)
                                           ├─ VL53L0X × 3 (VCC & GND)
                                           ├─ Encoder VCC (× 2)
                                           ├─ DRI0044 VCC (logic supply)
                                           └─ Ground rail (common with battery negative)
```

### Power Budget Estimate
| Component | Voltage | Typical Current | Notes |
|-----------|---------|-----------------|-------|
| ESP32-C6 | 3.3 V | 80 mA | Idle; WiFi/BLE would draw more |
| MPU-6050 | 3.3 V | 3.8 mA | Normal operation |
| VL53L0X × 3 | 3.3 V | ~12 mA | ~4 mA each at 20 ms measurement budget |
| Motor (each) | 6–9 V | 0–500 mA | Stalled; cruise ~100–200 mA |
| DRI0044 | 5 V / 6–9 V | 10 mA (logic) | Gate drive logic only; motor current flows through VM |
| **Total logic** | 3.3 V | ~95 mA | Excluding motors |
| **Both motors** (cruise) | 6–9 V | ~200–400 mA | Full load stall: ~1 A per motor |

**Recommendation:** Battery capacity ≥ 1000 mAh (1 Ah) for ~1 hour exploration runtime.

---

## Configuration Constants (Measured Per Build)

These values must be determined during bench testing before mapping.

### From `motor_encoder_test` Sketch
Run the interactive bench tool with wheels off the table:

| Constant | Initial Value | Determination Method | Purpose |
|----------|---------------|----------------------|---------|
| `L_DIR_SIGN` | +1 | Send 'd' (direction check); if left wheel spins backward, set to -1 | Ensure forward PWM drives wheel forward |
| `R_DIR_SIGN` | +1 | Send 'd' (direction check); if right wheel spins backward, set to -1 | Ensure forward PWM drives wheel forward |
| `ENC_TICKS_PER_REV` | 210.0 | Send 'o' (hand-measure); turn one wheel exactly once by hand; read count | Converts ticks to mm via `MM_PER_TICK = π × D / ENC_TICKS_PER_REV` |
| `WHEEL_DIAMETER_MM` | 32.0 | Measure wheel diameter with calipers (mm) | Used to calculate distance from encoder ticks |

### From `straight_test` Sketch (Corridor Tuning)
Run in a real maze corridor with walls ~180 mm apart:

| Constant | Initial Value | Tuning Method | Purpose |
|----------|---------------|---------------|---------:|
| `GYRO_SIGN` | +1 | Rotate mouse counterclockwise; if gyroAngle goes negative, set to -1 | Ensure gyro angle increases counterclockwise |
| `KP_V` | 0.05 | Raise until wheel speed error responds quickly without buzzing | Proportional wheel speed PID gain |
| `KI_V` | 0.20 | Raise until steady-state speed error → 0 | Integral wheel speed PID gain |
| `FF_PWM_PER_TPS` | 70.0 / CRUISE_TPS | Set so PWM sits mid-range at cruise | Feed-forward to reduce PID work |
| `STEER_KP_HEAD` | 6.0 | Raise until straight line on open corridor, no drift | Heading proportional gain (tps per degree) |
| `STEER_KD_HEAD` | 0.8 | Tune to reduce oscillation on heading corrections | Heading rate damping |
| `STEER_KP_CENTER` | 1.5 | Tune with both side walls present; mouse should stay centered | Balance correction (tps per mm imbalance) |
| `STEER_KP_SIDE` | 2.0 | Tune with one wall present; mouse should hold ~70 mm setpoint | Single-wall centering (tps per mm offset) |
| `WALL_TRUST_MM` | 90 | Raise to ignore distant walls; lower to use distant walls | Distance threshold for wall centering |
| `SIDE_SETPOINT_MM` | 70 | Tune for comfortable corridor center | Desired distance from wall when one wall present |
| `FRONT_STOP_MM` | 65 | Raise to stop farther from front wall; lower for closer stop | Safety stop distance (collision avoidance) |
| `TARGET_MM_S` | 150.0 | Raise after tuning (start conservative) | Cruise speed in mm/s |

---

## Signal Summary: All Signals at a Glance

### ESP32-C6 Outputs (Drive External Hardware)
```
GPIO 18  → DRI0044 PWM1   (left motor speed, 20 kHz PWM)
GPIO 19  → DRI0044 DIR1   (left motor direction, HIGH=fwd)
GPIO 20  → DRI0044 PWM2   (right motor speed, 20 kHz PWM)
GPIO 21  → DRI0044 DIR2   (right motor direction, HIGH=fwd)
GPIO 2   → VL53L0X XSHUT  (LEFT sensor enable)
GPIO 3   → VL53L0X XSHUT  (FRONT sensor enable)
GPIO 10  → VL53L0X XSHUT  (RIGHT sensor enable)
GPIO 11  → Status LED      (HIGH=active)
GPIO 6   → I2C SDA         (shared bus)
GPIO 7   → I2C SCL         (shared bus)
```

### ESP32-C6 Inputs (Read Sensor Data)
```
GPIO 0   ← Left encoder A   (quadrature, interrupt on CHANGE)
GPIO 1   ← Left encoder B   (quadrature, interrupt on CHANGE)
GPIO 22  ← Right encoder A  (quadrature, interrupt on CHANGE)
GPIO 23  ← Right encoder B  (quadrature, interrupt on CHANGE)
GPIO 6   ← I2C SDA          (shared bus, tri-state open-drain)
GPIO 7   ← I2C SCL          (shared bus, tri-state open-drain)
```

### I2C Bus (Shared SDA=GPIO 6, SCL=GPIO 7)
```
Address 0x30  ← VL53L0X (LEFT sensor)   [Continuous ranging, 20 ms budge]
Address 0x31  ← VL53L0X (FRONT sensor)  [Continuous ranging, 20 ms budget]
Address 0x32  ← VL53L0X (RIGHT sensor)  [Continuous ranging, 20 ms budget]
Address 0x68  ← MPU-6050 IMU            [Gyro Z + accel, interrupt capable]
```

---

## Bench Testing & Validation Order

Before deploying to maze exploration:

1. **Flash `i2c_scanner`** — verify all 4 I2C devices are FOUND at correct addresses
2. **Flash `motor_encoder_test`** — determine L_DIR_SIGN, R_DIR_SIGN, ENC_TICKS_PER_REV
3. **Flash `straight_test`** — tune PID gains in a real corridor, verify reliability
4. **Flash `mouse_explore`** — walls off table first, verify sensor initialization
5. **Flash `mouse_map`** — full maze exploration with self-correcting odometry

Do not skip steps. Each layer must work before the next can be trusted.

---

## Design Notes

- **All logic is 3.3 V.** The ESP32-C6 is 3.3 V only; level shifting is needed for any 5 V devices (e.g., if using a 5 V motor driver).
- **DRI0044 can accept 3.3 V logic.** Verify your specific unit's datasheet.
- **Pull-ups on I2C bus.** The VL53L0X carrier boards and ESP32 dev kit usually have built-in pull-ups on SDA/SCL. If using custom boards, confirm 4.7 kΩ pull-ups to 3.3 V are present.
- **Encoder connectors are delicate.** Keep encoder wiring short and shielded if possible to avoid noise on quadrature signals.
- **Motor current spikes at stall.** Use a 1–2 A fuse on the motor supply (VM) and a 20–30 mm track width on PCB if hand-soldering.
- **XSHUT pins must be GPIO outputs, not open-drain.** All three XSHUT pins are driven by the ESP32 as standard outputs to re-address the ToF sensors at boot.
- **Interrupt priority.** The encoder ISRs run at high priority; keep them short. They just increment/decrement counters; the control loop reads those counters every ~20 ms.

---

## Wiring Diagram Visual Summary

```
                              ┌─────────────────────┐
                              │   ESP32-C6-DevKit   │
                              │   (3.3V logic)      │
                              │                     │
                 ┌────────────┤ GPIO 6 (SDA)        │
                 │            │ GPIO 7 (SCL)        │
                 │            │ GPIO 0-1,22-23 (Enc)│
                 │            │ GPIO 18-21 (Motor)  │
                 │            │ GPIO 2,3,10 (XSHUT) │
                 │            └─────────────────────┘
                 │
    ┌────────────┴──────────────────────┐
    │        I2C Shared Bus              │
    │      (400 kHz, 3.3V)               │
    │                                    │
    ├──────────┬──────────┬──────────────┤
    │          │          │              │
   0x30       0x31       0x32           0x68
(LEFT ToF) (FRONT ToF) (RIGHT ToF)   (MPU-6050)
    │          │          │              │
  XSHUT       XSHUT      XSHUT          —
  GPIO2       GPIO3      GPIO10         —

Motor Control:
    GPIO 18/19  ──→  DRI0044  ←──  VM (battery 6-9V)
    GPIO 20/21  ──→  DRI0044         VCC (3.3V)
                         │
                    Motor outputs
                         │
    ┌────────────────────┼────────────────────┐
    │                    │                    │
   M1+                   M1−                 M2+      M2−
    │                    │                    │        │
  ┌─────────────────────────┐      ┌──────────────────────┐
  │  Left Motor GA12-N20    │      │ Right Motor GA12-N20 │
  │  + Hall Encoder (A/B)   │      │ + Hall Encoder (A/B) │
  │ Pin A → GPIO 0          │      │ Pin A → GPIO 22      │
  │ Pin B → GPIO 1          │      │ Pin B → GPIO 23      │
  │ VCC → 3.3V (max 3.6V)   │      │ VCC → 3.3V (max 3.6V)│
  └─────────────────────────┘      └──────────────────────┘

Power Rail (3.3V):
    ┌─ Buck Converter (6-9V → 3.3V) ─┬─ ESP32 VCC
                                     ├─ MPU VCC
                                     ├─ ToF VCC (×3)
                                     ├─ Encoder VCC (×2)
                                     └─ DRI0044 VCC

Ground (Common):
    ├─ Battery negative
    ├─ ESP32 GND
    ├─ MPU GND
    ├─ ToF GND (×3)
    ├─ Encoder GND (×2)
    ├─ DRI0044 GND
    └─ Motor shells (if conductive)
```

---

## Checklist Before Deployment

- [ ] I2C scanner finds all 4 devices at correct addresses
- [ ] Motor encoder test confirms L_DIR_SIGN and R_DIR_SIGN
- [ ] Motor encoder test confirms ENC_TICKS_PER_REV by hand-turn
- [ ] Straight test drives down open corridor without drifting
- [ ] Straight test holds center between walls (if corridor available)
- [ ] Front ToF stops mouse ~65 mm before wall
- [ ] All pins match the pinout table (no conflicts or off-by-one errors)
- [ ] Power budget estimate is within battery capacity
- [ ] Battery fuse is 1–2 A
- [ ] XSHUT pins are properly pulled down at boot (all sensors OFF until re-addressed)
- [ ] Encoder connectors are secure and wires are not crossing high-current motor wires

---

**End of Wiring Diagram Reference**

Use this document as the source of truth when building schematics, PCB layouts, or detailed wiring diagrams. Every measurement, address, and pin number above is taken directly from the working firmware code.
