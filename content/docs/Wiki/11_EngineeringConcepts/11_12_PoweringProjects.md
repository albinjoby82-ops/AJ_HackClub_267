---
title: Powering a Project
layout: default
parent: 7. Engineering Concepts
nav_order: 12
---

# Powering a Project

Power problems often appear as software bugs: resets, noisy sensors, weak motors and unreliable communication.

## Build a power budget

List each load and estimate normal and peak current:

| Load | Normal | Peak |
| --- | ---: | ---: |
| Controller | 60 mA | 100 mA |
| Servo | 150 mA | 900 mA |
| LEDs | 120 mA | 120 mA |

Choose a supply, regulator, connector and wire path that can handle the peak with margin.

## Common sources

- USB: convenient, but port and cable current are limited
- Bench supply: adjustable voltage and current limit
- Battery: portable, but voltage changes with charge
- Wall adapter: use an approved enclosed unit with the correct rating

## Regulators

- **Linear regulator:** simple and quiet, but loses `(Vin - Vout) × I` as heat
- **Buck converter:** efficiently reduces voltage
- **Boost converter:** increases voltage
- **Buck-boost converter:** can regulate above or below the battery voltage

## Ground and distribution

Separate supplies that exchange signals normally need a common reference ground. Route high motor current away from sensitive sensor returns, and use sufficiently short, thick power wiring.

## Decoupling

Place small ceramic capacitors near IC supply pins. Add suitable bulk capacitance near loads with rapidly changing current, such as servos or LED strips.

Capacitors help with brief changes; they do not fix an undersized supply.

## Battery runtime

```text
ideal hours ≈ battery capacity in Ah / average current in A
```

Real runtime is lower because of converter losses, peak loads, temperature and safe discharge limits.

{: .warning}
> Never connect two power outputs together unless the supplies are specifically designed for parallel operation.
