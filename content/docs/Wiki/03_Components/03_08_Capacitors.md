---
title: Capacitors
layout: default
parent: 4. Components
nav_order: 8
---

# Capacitors

A capacitor stores energy in an electric field. Capacitance is measured in farads (`F`), with common values expressed in microfarads (`µF`), nanofarads (`nF`), or picofarads (`pF`).

## Common uses

- Decoupling power close to an IC
- Smoothing supply ripple
- Filtering noise or signals
- Timing circuits
- AC coupling
- Short-term energy storage

## Polarised and non-polarised

Ceramic and many film capacitors are non-polarised. Electrolytic and tantalum capacitors are usually polarised and must be installed with the correct orientation.

{: .warning-title}
> Check polarity and voltage
>
> Reversing a polarised capacitor or exceeding its voltage rating can cause leakage, overheating, rupture, or explosion. Disconnect power and discharge capacitors safely before handling a circuit.

## Decoupling

A common starting point is a `100 nF` ceramic capacitor close to each digital IC's supply pins, with larger bulk capacitance elsewhere on the rail when required by the design.

Keep the connection loop short. A capacitor placed far from the IC is less effective against fast current changes.

## RC timing

For a simple resistor-capacitor network:

```text
time constant τ = R × C
```

After one time constant during charging, the capacitor reaches about 63% of the final voltage.

## Common mistakes

- Confusing `µF`, `nF`, and `pF`
- Installing an electrolytic backwards
- Using a voltage rating too close to the operating voltage
- Assuming every capacitor behaves ideally at every frequency
- Measuring resistance without waiting for the capacitor to charge or discharge
