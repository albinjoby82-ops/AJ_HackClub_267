---
title: Inductors
layout: default
parent: 4. Components
nav_order: 20
---

# Inductors

An inductor stores energy in a magnetic field and resists changes in current. Inductance is measured in henries (`H`).

Inductors appear in filters, switching regulators, radio circuits, motors, relays, and transformers.

## Important ratings

- Inductance
- Tolerance
- Saturation current
- RMS or heating current
- DC resistance
- Self-resonant frequency
- Core material

When an inductor saturates, its effective inductance falls and current can rise rapidly.

## Voltage when current changes

```text
V = L × (di/dt)
```

Interrupting current quickly can produce a large voltage. This is why relay coils, solenoids, and motors often need flyback or transient protection.

{: .warning}
> Do not assume a coil is harmless because its supply voltage is low. Stored magnetic energy can create damaging voltage spikes when switched.

## Common uses

- Power-supply filtering
- Buck and boost converters
- EMI suppression
- LC resonant circuits
- Energy storage
- Electromagnets

## Common problems

- Current exceeds saturation rating
- Winding resistance causes unexpected heating
- Wrong inductance or package
- Magnetic coupling affects nearby circuits
- Flyback path is missing
