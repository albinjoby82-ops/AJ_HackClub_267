---
title: Signals, Frequency and Sampling
layout: default
parent: 7. Engineering Concepts
nav_order: 4
---

# Signals, Frequency and Sampling

A signal carries information through a changing voltage, current, light level, position or another measurable quantity.

- **Amplitude:** size of the signal
- **Period:** time for one cycle
- **Frequency:** cycles per second
- **Offset:** average level
- **Phase:** relative position within a cycle
- **Noise:** unwanted variation

```text
frequency = 1 / period
```

A `20 ms` period is `50 Hz`.

## Analogue and digital

An analogue signal varies continuously within a range. A digital signal uses defined states, usually interpreted as LOW and HIGH. Real digital signals still take time to rise and fall.

## Sampling

An analogue-to-digital converter measures at individual times. If sampling is too slow, fast changes can be missed or appear as a false lower frequency.

Sample much faster than the highest frequency you need to observe. The theoretical minimum of twice the signal frequency leaves little practical margin.

## Resolution

An Arduino Uno's 10-bit ADC represents its input range with `1024` possible codes. More bits give smaller steps, but do not automatically remove noise or improve accuracy.
