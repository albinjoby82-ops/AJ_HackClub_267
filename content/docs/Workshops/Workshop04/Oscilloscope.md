---
title: Advanced Task 1 - Characterise a Signal with an Oscilloscope
layout: default
parent: Workshop 04 - Good Waves, Bad Vibes
nav_order: 4
---

# Advanced Task 1 - Characterise a Signal with an Oscilloscope

This optional lab task uses the Rohde & Schwarz HMO1002 series.

1. Connect the probe ground clip to circuit ground.
2. Connect the probe tip to the Arduino square-wave output.
3. Check the probe switch and channel setting. If the probe is set to `10×`, the oscilloscope channel must also be set to `10×`.
4. Set the vertical scale so the waveform fills several divisions.
5. Set the timebase so two or three periods are visible.
6. Trigger on a rising edge near the signal's midpoint.

Measure:

- Maximum and minimum voltage
- Peak-to-peak voltage
- Period and frequency
- Duty cycle
- Rise and fall time, if the signal and setup permit it

Compare the scope measurements with the values calculated in Task 2.

{: .warning}
> The probe's `10×` setting is not a zoom control. It attenuates the input by ten, and the scope compensates when configured correctly. A mismatched setting produces a tenfold voltage error.
