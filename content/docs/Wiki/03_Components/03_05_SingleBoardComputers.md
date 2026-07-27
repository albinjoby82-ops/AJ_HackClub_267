---
title: Single-Board Computers
layout: default
parent: 4. Components
nav_order: 2
---

# Single-Board Computers

A single-board computer (SBC) is a complete computer built on one circuit board. Unlike a typical microcontroller, it normally boots an operating system, runs multiple programs, uses files and storage, and can support displays, networks, USB devices, and high-level applications.

Common examples include Raspberry Pi computers, BeagleBone boards, and similar Linux-capable platforms.

## In this section

- [Raspberry Pi](03_05_01_RaspberryPi.md) — setup, GPIO, Python examples, remote access, and safe shutdown

## SBC or microcontroller?

| Choose a microcontroller when… | Choose an SBC when… |
| --- | --- |
| Startup must be fast and predictable | You need Linux or desktop software |
| Timing must be tightly controlled | You need a web server, database, or camera stack |
| Power consumption must be low | You need significant memory or processing |
| The device performs one embedded task | The system runs several complex services |

An SBC and microcontroller can also work together: the SBC handles networking and user interfaces while the microcontroller handles real-time control.

## Typical setup

An SBC may require:

- A compatible regulated power supply
- microSD, eMMC, or other boot storage
- An operating-system image
- Display, keyboard, and mouse, or remote access
- Network configuration
- Cooling appropriate to the workload

## GPIO warning

{: .warning-title}
> GPIO voltage depends on the SBC
>
> Standard Raspberry Pi GPIO is `3.3 V` and is not `5 V` tolerant. Other SBCs have their own limits. Do not connect motors or other large loads directly to GPIO.

Header pin number and GPIO number are not the same thing. Check the pinout for the exact model and numbering scheme.

## Official documentation

- [Raspberry Pi getting-started guide](https://www.raspberrypi.com/documentation/computers/getting-started.html)
- [Raspberry Pi computer and GPIO documentation](https://www.raspberrypi.com/documentation/computers/raspberry-pi.html)
