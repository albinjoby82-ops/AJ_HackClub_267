---
title: Raspberry Pi
layout: default
parent: Single-Board Computers
nav_order: 1
---

# Raspberry Pi

A Raspberry Pi is a compact single-board computer that normally runs Linux. It can operate as a small desktop computer or as a **headless** system accessed remotely over a network.

Unlike an Arduino Uno or ESP32-C6, a Raspberry Pi boots an operating system, manages files and users, and runs many processes at once. It is suitable for web services, cameras, dashboards, data logging, automation, and projects needing more processing or memory than a microcontroller.

{: .warning-title}
> Raspberry Pi GPIO uses 3.3 V logic
>
> Do not apply `5 V` to a GPIO pin. Do not power motors, relays, solenoids, heaters, or other substantial loads directly from GPIO. Use suitable resistors, drivers, level shifting, and external supplies.

## What you need

- A Raspberry Pi model suitable for the project
- A compatible regulated power supply
- Suitable microSD or other supported boot storage
- A computer running Raspberry Pi Imager
- Network access where required
- A monitor, keyboard, and mouse for desktop setup, or remote-access configuration for headless setup

Use the power supply recommended for the exact Raspberry Pi model. An inadequate cable or supply can cause undervoltage, instability, storage corruption, or unexpected resets.

## Install Raspberry Pi OS

1. Install **Raspberry Pi Imager** on another computer.
2. Select the correct Raspberry Pi model.
3. Select Raspberry Pi OS.
4. Select the intended storage device carefully.
5. Configure hostname, username, password, locale, Wi-Fi, and SSH if required.
6. Write and verify the image.
7. Insert the storage into the unpowered Raspberry Pi.
8. Connect peripherals.
9. Apply power and complete initial setup.

{: .warning}
> Imaging erases the selected storage device. Check the device and capacity before confirming.

## Update the system

After first boot:

```bash
sudo apt update
sudo apt full-upgrade
```

Read prompts before accepting changes and reboot if required.

## Access it remotely

For a headless system, enable SSH during imaging or through Raspberry Pi configuration.

From another computer:

```bash
ssh username@hostname.local
```

Use the hostname and username configured during imaging. Do not expose SSH directly to the public internet without an appropriate security design.

## Understanding the GPIO header

The 40-pin header contains:

- Fixed `3.3 V` and `5 V` power pins
- Ground pins
- `3.3 V` GPIO pins
- Pins with alternate functions such as I²C, SPI, UART, and PWM

Header position, GPIO number, and software numbering can differ. Run:

```bash
pinout
```

to display the reference for the installed system, and confirm against the documentation for the exact model.

## Example: blink an LED

Connect `GPIO17` through a suitable series resistor and LED to ground.

```python
from gpiozero import LED
from time import sleep

led = LED(17)

while True:
    led.on()
    sleep(0.5)
    led.off()
    sleep(0.5)
```

Run it with:

```bash
python3 blink.py
```

Stop it with `Ctrl+C`.

## Example: read a button

Connect a button between `GPIO2` and ground:

```python
from gpiozero import Button

button = Button(2)

button.when_pressed = lambda: print("pressed")
button.when_released = lambda: print("released")

input("Press Enter to stop\n")
```

GPIO Zero configures a suitable pull-up for this pattern. Check whether the chosen pin has special bus connections or fixed pull resistors before using it.

## Connect an I²C sensor

Before wiring:

1. Confirm the sensor uses `3.3 V`-compatible power and logic.
2. Connect `SDA`, `SCL`, ground, and the correct supply.
3. Enable I²C through Raspberry Pi configuration.
4. Check whether the module already includes pull-up resistors.
5. Find the bus address using approved diagnostic tools.

Do not connect a `5 V` I²C pull-up directly to Raspberry Pi GPIO.

## Files, services, and startup

Because the Raspberry Pi runs an operating system, a project may need:

- A dedicated project directory
- A Python virtual environment
- Configuration stored separately from code
- Logging
- A systemd service for automatic startup
- Network and update planning

Avoid placing passwords or API keys directly in files committed to Git.

## Safe shutdown

Do not normally remove power while the operating system is writing to storage.

```bash
sudo shutdown -h now
```

Wait for shutdown to complete before disconnecting power.

## Common problems

### It does not boot

Check the power supply, storage image, card seating, display input, status LEDs, and whether the selected OS supports the model.

### It resets or shows undervoltage

Use a suitable power supply and cable, disconnect excessive USB or GPIO loads, and check connectors.

### SSH does not connect

Check that SSH was enabled, both devices are on the expected network, the hostname or IP address is correct, and the username matches.

### GPIO code does nothing

Check numbering, permissions, common ground, wiring, pin function, and whether another process is using the GPIO.

## Official documentation

- [Raspberry Pi getting-started guide](https://www.raspberrypi.com/documentation/computers/getting-started.html)
- [Raspberry Pi computer hardware and GPIO](https://www.raspberrypi.com/documentation/computers/raspberry-pi.html)
- [Raspberry Pi OS documentation](https://www.raspberrypi.com/documentation/computers/os.html)
