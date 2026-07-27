---
title: Arduino Uno R3
layout: default
parent: Microcontrollers
nav_order: 1
---

# Arduino Uno R3

The Arduino Uno R3 is a development board based on the **ATmega328P** microcontroller. It is widely used in MakerLabs because it is robust, well documented, and easy to program over USB.

![Arduino Uno R3](../../assets/images/Wiki10_Microcontrollers-ArduinoUno.svg)

*Figure: Arduino Uno R3 board.*

## Key features

| Feature | Uno R3 |
| --- | --- |
| Logic voltage | `5 V` |
| Main microcontroller | ATmega328P |
| Clock | `16 MHz` |
| Digital I/O | 14 pins |
| PWM-capable pins | 6 |
| Analogue inputs | 6 |
| USB | Programming, serial communication, and power |

The board also provides power pins, an ICSP header, a reset button, a barrel-jack input, and an onboard LED connected to digital pin 13.

{: .warning-title}
> Protect the pins
>
> Do not connect a GPIO pin directly to a motor, relay, high-power LED, or another heavy load. Do not apply voltages outside the board's permitted range. Always use a current-limiting resistor with an external LED.

## Pin groups

- `0` and `1`: hardware serial RX and TX; avoid using them for ordinary wiring while uploading or using Serial Monitor
- `2–13`: digital input/output
- `3, 5, 6, 9, 10, 11`: PWM output using `analogWrite()`
- `A0–A5`: analogue input; they can also be used as digital pins
- `5V` and `3.3V`: regulated power outputs with limited available current
- `GND`: circuit reference
- `VIN`: external supply input path, not a general `5 V` input

Always verify the official pinout for the exact board revision.

## Connect and upload

1. Install or open the Arduino IDE.
2. Connect the Uno using a data-capable USB cable.
3. Select **Tools → Board → Arduino AVR Boards → Arduino Uno**.
4. Select the board's serial port under **Tools → Port**.
5. Open or write a sketch.
6. Click **Verify** to compile it.
7. Click **Upload**.

If uploading fails, close other programs using the serial port, check the cable, confirm the board and port, and press reset once before retrying.

## Example: blink the onboard LED

```cpp
const int LED_PIN = LED_BUILTIN;

void setup() {
  pinMode(LED_PIN, OUTPUT);
}

void loop() {
  digitalWrite(LED_PIN, HIGH);
  delay(500);
  digitalWrite(LED_PIN, LOW);
  delay(500);
}
```

## Example: read a button safely

Connect a push button between pin `2` and `GND`. The internal pull-up resistor keeps the input high while the button is open.

```cpp
const int BUTTON_PIN = 2;

void setup() {
  pinMode(BUTTON_PIN, INPUT_PULLUP);
  Serial.begin(9600);
}

void loop() {
  bool pressed = digitalRead(BUTTON_PIN) == LOW;
  Serial.println(pressed ? "pressed" : "released");
  delay(50);
}
```

With `INPUT_PULLUP`, a pressed button reads `LOW`. This inverted logic is normal.

## Example: read a potentiometer

Connect the potentiometer's outer terminals to `5V` and `GND`, and its centre terminal to `A0`.

```cpp
void setup() {
  Serial.begin(9600);
}

void loop() {
  int reading = analogRead(A0);
  float voltage = reading * (5.0 / 1023.0);
  Serial.println(voltage);
  delay(100);
}
```

## Example: PWM LED brightness

Connect an LED and series resistor to PWM-capable pin `9`.

```cpp
const int LED_PIN = 9;

void setup() {
  pinMode(LED_PIN, OUTPUT);
}

void loop() {
  for (int level = 0; level <= 255; level++) {
    analogWrite(LED_PIN, level);
    delay(5);
  }
}
```

`analogWrite()` produces PWM on the Uno; it does not generate a true analogue voltage.

## Powering the Uno

USB is the simplest power source during development. If using an external supply, follow Arduino's documented input requirements and avoid powering the board through multiple paths unless the arrangement is understood.

Connect all devices that exchange ordinary single-ended signals to a common ground. Check voltage compatibility before connecting `3.3 V` devices to the Uno's `5 V` logic.

## Common problems

### No serial port appears

Try another data-capable USB cable or port, reconnect the board, and check the operating system's device list.

### Upload fails

Check board selection, port selection, pins `0/1`, serial-port conflicts, and whether another sketch is continuously resetting the board.

### The circuit resets when a motor starts

The motor is drawing too much current or injecting electrical noise. Use a separate suitable supply, driver, flyback protection where required, decoupling, and a correctly planned common ground.

## Official documentation

- [Arduino Uno R3 documentation](https://docs.arduino.cc/hardware/uno-rev3/)
- [Arduino Uno R3 datasheet](https://docs.arduino.cc/resources/datasheets/A000066-datasheet.pdf)
