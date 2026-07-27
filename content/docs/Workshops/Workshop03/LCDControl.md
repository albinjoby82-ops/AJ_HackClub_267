---
title: Advanced Task 1 - Add an LCD Control Panel
layout: default
parent: Workshop 03 - Servos & Linkages
nav_order: 4
---

# Advanced Task 1 - Add an LCD Control Panel

Display both joint angles and create a small interface for choosing manual or automatic movement.

## Connect an I²C LCD

For a common Arduino Uno setup:

- `VCC` to `5V`
- `GND` to `GND`
- `SDA` to `A4`
- `SCL` to `A5`

Check your LCD module before wiring it. I²C addresses are commonly `0x27` or `0x3F`, but yours may differ.

Install a compatible `LiquidCrystal_I2C` library, then test:

```cpp
#include <Wire.h>
#include <LiquidCrystal_I2C.h>

LiquidCrystal_I2C lcd(0x27, 16, 2);

void setup() {
  lcd.init();
  lcd.backlight();
  lcd.print("Servo controller");
}

void loop() {}
```

## Display live values

Update the display only when a value changes, rather than clearing it every loop:

```cpp
void showAngles(int shoulderAngle, int elbowAngle) {
  lcd.setCursor(0, 0);
  lcd.print("Shoulder: ");
  lcd.print(shoulderAngle);
  lcd.print("   ");

  lcd.setCursor(0, 1);
  lcd.print("Elbow:    ");
  lcd.print(elbowAngle);
  lcd.print("   ");
}
```

## Add a menu

Use a push button to cycle through:

1. **Manual:** potentiometers control both joints.
2. **Sweep:** joints move through their safe ranges automatically.
3. **Replay:** the arm repeats recorded positions.

Represent the mode with an `enum` and use `millis()` so the interface stays responsive.

{: .challenge-title}
> Non-blocking control
>
> Remove every long `delay()` from the combined program. Continue reading buttons and refreshing the display while the servos move gradually towards their targets.
