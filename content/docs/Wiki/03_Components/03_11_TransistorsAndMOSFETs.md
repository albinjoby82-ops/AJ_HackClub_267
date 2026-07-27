---
title: Transistors and MOSFETs
layout: default
parent: 4. Components
nav_order: 11
---

# Transistors and MOSFETs

Transistors control current or voltage and are used for switching, amplification, and signal processing.

[BJT vs MOSFET — Transistor Basics Explained for Beginners](https://youtu.be/a0xoqozu29k)

<iframe width="560" height="315" src="https://www.youtube.com/embed/a0xoqozu29k" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

## BJTs

A bipolar junction transistor has **base**, **collector**, and **emitter** terminals. A small base current can control a larger collector current.

Use a base resistor when driving a BJT from a GPIO pin.

## MOSFETs

A MOSFET has **gate**, **drain**, and **source** terminals. Its gate is voltage-controlled and draws very little steady current, but it behaves like a capacitor while switching.

For low-side switching with an N-channel MOSFET:

- Load connects between positive supply and drain.
- Source connects to ground.
- GPIO drives the gate through an appropriate resistor.
- A pull-down resistor keeps the gate off during reset.
- Inductive loads require flyback protection.

{: .warning-title}
> Check the exact pinout
>
> Components in the same package can use different pin orders. Never assume `G-D-S` or `C-B-E`; find the exact datasheet.

## Choosing a MOSFET

Check:

- Drain-source voltage rating
- Continuous and pulsed current
- Power dissipation and thermal resistance
- On-resistance at the actual gate voltage
- Gate charge and switching speed
- Whether it is genuinely logic-level at `3.3 V` or `5 V`

The threshold voltage is not the voltage at which the MOSFET is fully on.

## Common mistakes

- Driving a high-current load directly from GPIO
- Omitting common ground
- No flyback diode on a coil
- Floating gate
- Using a MOSFET that needs `10 V` gate drive from a `3.3 V` controller
- Ignoring heat dissipation
