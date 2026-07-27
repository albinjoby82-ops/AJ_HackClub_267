---
title: Voltage Regulators
layout: default
parent: 4. Components
nav_order: 19
---

# Voltage Regulators

A voltage regulator converts an input supply into a controlled output voltage.

## Linear regulators

Linear regulators are simple and can be low noise, but the voltage difference is dissipated as heat:

```text
Ploss ≈ (Vin - Vout) × Iout
```

For `12 V` to `5 V` at `0.2 A`, the regulator dissipates about:

```text
(12 - 5) × 0.2 = 1.4 W
```

That may require significant thermal management.

## Switching regulators

Buck, boost, and buck-boost converters transfer energy through switching components and inductors. They can be more efficient but introduce switching noise and require careful layout.

## Before use

- Check input range and absolute maximum voltage.
- Check output voltage and tolerance.
- Check available current under real cooling conditions.
- Check dropout voltage for linear regulators.
- Fit the required input/output capacitors.
- Confirm pinout and module adjustment.
- Measure the output before connecting sensitive electronics.

{: .warning}
> Adjustable modules may arrive set to an unexpected voltage. Power and measure the module by itself, then switch off before connecting the load.

## Common problems

- Input voltage is too low for regulation
- Regulator overheats
- Required capacitors are missing or unsuitable
- Output adjustment is incorrect
- Converter current rating is quoted without realistic cooling
- Noise affects analogue or radio circuits
