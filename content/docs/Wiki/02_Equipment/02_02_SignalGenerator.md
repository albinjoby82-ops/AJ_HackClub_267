---
title: Signal Generator (Rigol DG822 Pro)
layout: default
parent: 3. Electronics & Test Equipment
nav_order: 2
---

# Signal Generator

A signal generator produces controlled electrical waveforms for testing a circuit. Instead of waiting for a sensor, motor, or communication system to produce a signal, you can generate a repeatable input with a chosen shape, frequency, amplitude, and offset.

Hack Club uses the **Rigol DG822 Pro**, a two-channel function/arbitrary waveform generator. The exact menus may differ on other models, but the setup principles remain similar.

{: .warning-title}
> Check the electrical limits first
>
> Keep the channel output **off** while wiring. Confirm the circuit's allowed voltage, polarity, frequency, and input impedance before enabling it.
>
> The generator's BNC outer conductor may be connected to protective earth. Never clip it to a point that is not safe to earth, and never use this guide on mains-connected circuits.

## Watch: what a function generator does

If you have not used one before, this Afrotechmods video explains what a signal/function generator is and how the waveform, frequency, and amplitude controls behave.

[Function Generator Tutorial (Afrotechmods)](https://youtu.be/mLKPwWGBtIw)

<iframe width="560" height="315" src="https://www.youtube.com/embed/mLKPwWGBtIw" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

## Key settings

| Setting | Meaning |
| --- | --- |
| Waveform | The signal shape, such as sine, square, ramp, pulse, or noise |
| Frequency | How many cycles occur each second, measured in hertz |
| Amplitude | The size of the waveform |
| DC offset | Moves the waveform above or below 0 V |
| Phase | The relative position of one periodic signal compared with another |
| Duty cycle | For pulses or square waves, the percentage of each cycle spent high |
| Output load | Tells the generator how the connected load should affect the displayed amplitude |

## Amplitude and offset

Always work out the highest and lowest voltage before connecting the signal.

For a waveform expressed as peak-to-peak voltage:

```text
maximum voltage = offset + (Vpp / 2)
minimum voltage = offset - (Vpp / 2)
```

For example, a `4 Vpp` waveform with a `2.5 V` offset varies from `0.5 V` to `4.5 V`.

{: .warning}
> A waveform can exceed a microcontroller's input limits even when its displayed amplitude looks small. Check both extremes, not just the offset or peak-to-peak value.

## Output load matters

Signal generators are commonly designed around a `50 Ω` source and load system. The voltage delivered to a high-impedance circuit can differ from the front-panel value if the generator's load setting does not match the actual connection.

For most high-impedance oscilloscope or microcontroller inputs:

1. Use the generator's **High Z** load setting when appropriate.
2. Confirm the real voltage with an oscilloscope before connecting sensitive circuitry.
3. Never assume the display alone proves the voltage at the circuit.

## Basic setup procedure

1. Leave the selected channel output off.
2. Connect the BNC cable to the generator.
3. Choose the waveform.
4. Set the frequency.
5. Set the amplitude and DC offset.
6. Confirm the resulting minimum and maximum voltages.
7. Select the correct output-load setting.
8. Connect the signal and ground to the unpowered test circuit.
9. Connect an oscilloscope and verify the waveform if one is available.
10. Enable the generator output.
11. Disable the output before changing the circuit.

## Example: a microcontroller-style clock signal

To create a low-frequency test clock for a circuit that accepts `0–5 V`:

| Setting | Example value |
| --- | --- |
| Waveform | Square |
| Frequency | `10 Hz` |
| Amplitude | `5 Vpp` |
| Offset | `2.5 V` |
| Duty cycle | `50%` |

This should produce a waveform varying from approximately `0 V` to `5 V`, but you must verify the actual output and the receiving device's limits.

## Using two channels

The DG822 Pro provides two outputs. They can be useful for comparing signals, testing phase differences, or stimulating two parts of a circuit.

Before using both:

- Determine whether the channel grounds are internally common.
- Check the phase and frequency relationship.
- Calculate the voltage between every pair of connected points.
- Verify both channels on an oscilloscope.

## Common problems

### No waveform appears

Check that the correct channel output is enabled, the cable is connected, the oscilloscope trigger is suitable, and the circuit shares the intended reference.

### The measured amplitude is twice the expected value

The load setting may be `50 Ω` while the connected device is high impedance. Select the appropriate load setting and verify again.

### The waveform is clipped or distorted

The requested amplitude and offset may exceed the generator's output range, the load may be too heavy, or the circuit may be clamping the signal.

### The circuit resets or behaves unpredictably

Disable the output and check for negative voltage, excessive voltage, incompatible grounds, or a missing common reference.

## Manufacturer documentation

- [Rigol DG800 Pro Series Quick Guide](https://download.rigol.com/en/Manual/Waveform%20Generator/DG800%20Pro/DG800Pro_QuickGuide_EN.pdf)
- [Local copy of the Rigol quick guide](../../assets/pdfs/Wiki02_02_DG800Pro_QuickGuide_EN.pdf)
