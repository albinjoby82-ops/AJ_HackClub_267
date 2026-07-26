---
title: Oscilloscope (R&S HMO1002 Series)
layout: default
parent: 3. Electronics & Test Equipment
nav_order: 4
---

# Oscilloscope

An oscilloscope displays voltage changing over time. It lets you see signal shape, amplitude, frequency, timing, noise, glitches, and the relationship between multiple signals.

MakerLabs uses two-channel oscilloscopes from the **Rohde & Schwarz HMO1002 series**. This guide introduces the controls needed for ordinary low-voltage measurements; advanced functions are covered in the manufacturer manual.

{: .warning-title}
> The probe ground is not a floating wire
>
> On a conventional bench oscilloscope, the probe ground clip is normally connected to protective earth through the instrument. Connecting it to the wrong point can short part of the circuit through earth, damage equipment, or cause injury.
>
> For supervised MakerLabs work, connect probe ground only to the circuit's intended ground or reference node. Never use this guide to probe mains or another hazardous circuit.

## What the display represents

An oscilloscope graph normally uses:

- **Vertical axis:** voltage
- **Horizontal axis:** time
- **Trigger point:** the event used to position repeated captures consistently

The graticule divides the display into squares called divisions. The vertical scale is expressed in volts per division, while the horizontal scale is expressed in seconds per division.

## Main controls

| Control | What it changes |
| --- | --- |
| Channel 1 / Channel 2 | Enables and configures an input |
| Volts/div | Vertical scale for the selected channel |
| Vertical position | Moves a trace up or down without changing the signal |
| Time/div | Amount of time represented by each horizontal division |
| Horizontal position | Moves the captured time window |
| Trigger level | Voltage at which the chosen trigger event occurs |
| Trigger source | Channel or signal used for triggering |
| Run/Stop | Starts or freezes repeated acquisition |
| Single | Waits for one trigger event, captures it, and stops |
| Autoset | Attempts to choose usable scales and triggering automatically |

{: .note}
> Autoset is useful for finding an unknown repetitive signal, but it does not know the circuit's safe limits or what feature matters. Treat it as a starting point, not a substitute for understanding the settings.

## Understanding the probe

A passive probe has:

- A probe tip for the signal being measured
- A ground clip or ground spring for the reference node
- An attenuation setting, commonly `1×` or `10×`
- A compensation adjustment

{: .warning-title}
> Check the probe's 10× switch
>
> The probe has a physical `1× / 10×` switch. This is sometimes described informally as “10× zoom,” but it is actually **10× attenuation**: in the `10×` position, only one tenth of the signal reaches the oscilloscope input.
>
> The oscilloscope channel must also be configured for a `10×` probe so it can multiply the reading back to the correct value. If the physical probe switch and channel setting do not match, every displayed voltage will be **ten times too large or ten times too small**.

For most general measurements, a correctly configured `10×` probe loads the circuit less than a `1×` probe and usually supports a wider bandwidth.

The probe attenuation setting and oscilloscope channel setting must match. If the probe is set to `10×` but the channel is set to `1×`, displayed voltage measurements will be incorrect by a factor of ten.

## Compensating a passive probe

Passive probes should be compensated when first used, after a long break, or when moved between oscilloscopes or channels. The HMO1002 series provides a probe-compensation wizard and reference signal.

1. Set the probe to `10×`.
2. Connect it to the selected channel.
3. Connect the probe tip and ground to the oscilloscope's compensation output as shown on the instrument.
4. Set the channel's attenuation to `10×`.
5. Open the probe-compensation function or display the reference square wave.
6. Adjust the probe's compensation trimmer using the approved tool.

A correctly compensated square wave has a flat top with clean corners:

```text
correct             under-compensated     over-compensated
 ┌─────┐             ╭─────┐               ┌─────╮
 │     │            ╱      │               │      ╲
─┘     └─          ─┘      └─             ─┘      └─
```

{: .tip}
> If measurements look unexpectedly rounded, peaked, or distorted, verify probe compensation and attenuation before blaming the circuit.

## Basic measurement procedure

1. Understand the circuit and identify its ground reference.
2. Check the expected voltage range and frequency.
3. Check the probe's physical `1× / 10×` switch.
4. Set the oscilloscope channel to the same probe attenuation.
5. Connect the probe ground to the circuit ground.
6. Connect the probe tip to the signal.
7. Enable the channel.
8. Choose a safe volts/div setting.
9. Adjust time/div until useful cycles or events are visible.
10. Select the channel as the trigger source.
11. Set edge triggering and move the trigger level inside the waveform.
12. Refine the vertical and horizontal scales.

Keep the ground connection short when measuring fast signals. A long ground lead adds inductance and can introduce ringing or pick up noise.

## Triggering

Triggering makes a repetitive waveform appear stable by starting each displayed capture at a defined event.

For a simple waveform:

1. Select **edge trigger**.
2. Choose the measured channel as the source.
3. Choose a rising or falling edge.
4. Place the trigger level between the waveform's high and low values.

If the trace rolls, jumps, or will not stabilise, check the trigger source, level, edge direction, and mode.

### Auto, normal, and single acquisition

- **Auto:** continues updating even when no valid trigger is found.
- **Normal:** updates only when the trigger condition occurs.
- **Single:** captures one qualifying event and stops.

Use Single mode for one-off events such as startup behaviour, a button press, or an intermittent pulse.

## Coupling

Channel coupling changes what reaches the display:

- **DC coupling:** displays both the DC level and changing part of the signal.
- **AC coupling:** blocks the DC component so small variations can be viewed around zero.
- **Ground coupling:** disconnects the input signal internally and shows the channel's zero reference, where supported.

Use DC coupling by default. AC coupling is useful when a small ripple sits on a much larger DC voltage, but it changes low-frequency content and hides the true DC level.

## Measuring amplitude and frequency

You can estimate values from the grid:

```text
peak-to-peak voltage = vertical divisions × volts/div
period = horizontal divisions × time/div
frequency = 1 / period
```

The oscilloscope can also calculate automatic measurements. Before trusting them, make sure the waveform is visible, stable, not clipped, and measured over a suitable capture.

## Example: checking a signal-generator output

1. Configure the signal generator with its output disabled.
2. Connect generator ground and oscilloscope ground to the same intended reference.
3. Connect the generator output to Channel 1.
4. Set matching probe attenuation.
5. Enable the generator output.
6. Press Autoset if necessary, then refine volts/div and time/div manually.
7. Measure peak-to-peak voltage and frequency.
8. Compare the results with the generator settings.

If the measured amplitude is twice the expected value, check the signal generator's `50 Ω` versus `High Z` output-load setting.

## Comparing two signals

Use both channels to compare an input and output, or two digital signals:

1. Connect both probe grounds to the same circuit ground.
2. Connect each probe tip to its signal.
3. Enable both channels and set suitable vertical scales.
4. Trigger from the signal that provides the most stable reference.
5. Use cursors or automatic measurements to compare delay, phase, amplitude, or frequency.

{: .warning}
> The two probe ground clips are normally connected together through the oscilloscope. Attaching them to two different circuit nodes can short those nodes together.

## Common problems

### The screen shows a flat line

Check the selected channel, probe connection, ground reference, volts/div setting, coupling, circuit power, and whether the probe tip is contacting the intended node.

### The waveform will not stay still

Check the trigger source and edge, then move the trigger level inside the waveform. Normal trigger mode may help once the condition is set correctly.

### The waveform is clipped

Increase the vertical range, reposition the trace, check probe attenuation, and confirm the signal is within the oscilloscope's input limits.

### The measurement contains excessive ringing or noise

Shorten the probe ground connection, use the ground spring if appropriate, avoid large probe loops, check probe compensation, and reduce nearby interference.

### The displayed voltage is ten times too large or small

The probe and channel attenuation settings probably do not match.

### A one-off event disappears

Use Single acquisition and configure the trigger condition before causing the event.

## Before disconnecting

1. Stop or disable signal-generator outputs.
2. Disable power if the circuit will be changed.
3. Remove the probe tip.
4. Remove the ground clip.
5. Return probes without sharply bending their cables.
6. Report damaged insulation, broken hooks, loose BNC connectors, or bent probe tips.

## Manufacturer documentation

- [Rohde & Schwarz HMO1002 manuals and technical documentation](https://www.rohde-schwarz.com/manual/hmo1002/)
- [Rohde & Schwarz HMO1002/HMO1202 User Manual (PDF)](https://cdn.rohde-schwarz.com/pws/dl_downloads/dl_common_library/dl_manuals/gb_1/h/hmo1002_1202/HMO1002_1202_DigitalOscilloscope_UserManual_en_04.pdf)
