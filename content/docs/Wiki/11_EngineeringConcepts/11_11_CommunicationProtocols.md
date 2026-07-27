---
title: UART, I²C and SPI
layout: default
parent: 7. Engineering Concepts
nav_order: 11
---

# UART, I²C and SPI

These digital interfaces let controllers communicate with sensors, displays and other boards.

## UART

UART normally uses two signal wires:

- Controller TX → device RX
- Controller RX ← device TX
- Shared ground

Both ends must use the same baud rate and compatible logic voltage. UART does not provide a clock wire.

Common problems:

- TX connected to TX instead of RX
- Baud rates differ
- Missing common ground
- `5 V` signal connected to a `3.3 V`-only input
- Arduino Uno pins `0` and `1` conflict with USB Serial

## I²C

I²C uses:

- `SDA`: data
- `SCL`: clock
- Shared ground
- Pull-up resistors to the correct logic voltage

Many devices can share the bus if their addresses do not conflict.

```cpp
#include <Wire.h>

void setup() {
  Wire.begin();
}
```

Use an address-scanner sketch when a device is not found. Some modules already include pull-ups; too many parallel pull-ups can make the total resistance too low.

## SPI

SPI commonly uses:

- `SCK`: clock
- `COPI` or `MOSI`: controller to peripheral
- `CIPO` or `MISO`: peripheral to controller
- One chip-select line per device
- Shared ground

SPI is often faster than I²C but uses more wires. Devices must agree on clock speed, bit order and SPI mode.

## Choosing

| Interface | Strength | Limitation |
| --- | --- | --- |
| UART | Simple point-to-point debugging | Usually one device per port |
| I²C | Many addressed devices, two signals | Address conflicts and pull-ups |
| SPI | Fast and full duplex | More wires and chip-select lines |

{: .tip}
> Check both the protocol and the electrical levels. Correct bytes at the wrong voltage can still damage hardware.
