---
title: Operational Amplifiers
layout: default
parent: 4. Components
nav_order: 13
---

# Operational Amplifiers

An operational amplifier (op-amp) amplifies the voltage difference between a non-inverting input (`+`) and an inverting input (`−`). Feedback around the op-amp determines the circuit behaviour.

## Ideal rule of thumb

With negative feedback and normal linear operation:

- Input current is approximately zero.
- The output moves so the two input voltages are approximately equal.

These approximations are useful, but real op-amps have limits.

## Common circuits

### Voltage follower

The output is connected to the inverting input, and the signal enters the non-inverting input. The voltage gain is approximately 1, but the circuit can buffer a high-impedance source.

### Non-inverting amplifier

```text
gain = 1 + (Rf / Rg)
```

### Inverting amplifier

```text
gain = -Rf / Rin
```

## Real-world limits

Check:

- Supply-voltage range
- Input common-mode range
- Output-voltage swing
- Output current
- Gain-bandwidth product
- Slew rate
- Input offset voltage
- Whether the op-amp is unity-gain stable

“Rail-to-rail” may apply to inputs, output, or both, and usually still has conditions.

## Breadboard placement

DIP op-amps must straddle the breadboard centre gap. Identify pin 1 and verify the exact datasheet; dual and single op-amps often use different pinouts.

Add local supply decoupling. For dual-supply circuits, understand what `+V`, `−V`, and ground mean before wiring.

{: .warning}
> An op-amp is not automatically a comparator. Some op-amps recover poorly from saturation, and many cannot tolerate arbitrary differential input voltage. Use a comparator when that is the intended function.

## Common problems

- Power pins omitted because they are not shown on a simplified schematic
- Inputs outside common-mode range
- Output asked to reach a supply rail it cannot reach
- Oscillation from layout, capacitive load, or missing decoupling
- Wrong feedback polarity
- Incorrect pinout
