---
title: Hardware
layout: default
parent: Micromouse 2026 Resources
nav_order: 2
---

# Build your hardware

Use the event kit’s pin assignments and get each part working in order. The wiring and expected behavior here follow the comments at the top of the supplied debug sketches.

[Start the eight debug checks](#/docs/Micromouse2026/Debug/index.md) · [Download all sketches and the visualizer](../../../../downloads/micromouse-debug-kit.zip)

![Event GPIO assignments for sensors, motor driver and Motor A encoder](../../assets/images/micromouse-event-pin-map.svg)

<nav class="hardware-directory" aria-label="Hardware guides">
<a href="#/docs/Micromouse2026/Hardware/ESP32C6.md"><span class="guide-code">H1</span><strong>ESP32-C6 controller →</strong><span class="guide-description">Exact event pin map, Arduino setup and the first LED check.</span></a>
<a href="#/docs/Micromouse2026/Hardware/DRI0044.md"><span class="guide-code">H2</span><strong>Motor driver →</strong><span class="guide-description">Connect the DRI0044 and test each wheel’s direction and speed.</span></a>
<a href="#/docs/Micromouse2026/Hardware/SEN0142.md"><span class="guide-code">H3</span><strong>MPU-6050 / GY-521 IMU →</strong><span class="guide-description">Four wires on GPIO6/7; leave XDA, XCL, AD0 and INT unconnected.</span></a>
<a href="#/docs/Micromouse2026/Hardware/VL53L0X.md"><span class="guide-code">H4</span><strong>Distance sensors →</strong><span class="guide-description">XSHUT on GPIO18/19/20; left 0x30, front 0x31, right 0x29.</span></a>
<a href="#/docs/Micromouse2026/Hardware/BuckConverter.md"><span class="guide-code">H5</span><strong>Battery & power →</strong><span class="guide-description">USB for the controller, battery for motors, shared ground and the PWM limit.</span></a>
</nav>

[H6 — N20 motors and Motor A encoder](#/docs/Micromouse2026/Hardware/GA12N20.md): C1 GPIO21, C2 GPIO22 and encoder VCC on 3V3.

## Before you connect anything

Switch off power before changing wires. Keep the event pin map beside you and check each connection against the sketch you will upload. Start with USB only; leave motor power disconnected until the motor checks. Raise the wheels for motor tests, and unplug the motor entirely before running the pin test.
