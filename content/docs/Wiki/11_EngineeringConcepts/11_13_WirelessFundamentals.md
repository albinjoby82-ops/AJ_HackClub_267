---
title: Wireless Fundamentals
layout: default
parent: 7. Engineering Concepts
nav_order: 13
---

# Wireless Fundamentals

Wireless systems replace a cable with radio waves, but still need a protocol, antenna, power budget and security plan.

## Wi-Fi

Useful for local networks, web services and higher data rates. It usually consumes more power than Bluetooth Low Energy.

- SSID identifies a network.
- RSSI estimates received signal strength; values closer to zero are stronger.
- Channels share radio spectrum and may interfere.
- A strong signal does not guarantee internet access or low latency.

## Bluetooth Low Energy

BLE is designed for short messages and low-power devices.

- A peripheral advertises services.
- A central device connects and reads or writes characteristics.
- Service and characteristic UUIDs describe the interface.

## Antennas

- Keep the antenna area clear of metal, batteries and ground planes unless the board design says otherwise.
- Orientation and enclosure material affect range.
- Do not cover a PCB antenna with wiring.
- Use only antenna connectors and types supported by the radio.

## Design for failure

Wireless links drop. A safe project should:

- Detect timeout or disconnection
- Return actuators to a safe state
- Retry with limits
- Avoid depending on one packet
- Continue local control where possible

## Privacy and security

- Connect only to networks you own or may use.
- Keep passwords and API keys out of source control.
- Avoid collecting unnecessary network identifiers.
- Authenticate control commands.
- Do not expose a development web server directly to the public internet.

{: .tip}
> Test range in the real enclosure and location. A successful desk test does not represent walls, people, interference and battery operation.
