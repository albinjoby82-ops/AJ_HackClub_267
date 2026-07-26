---
title: Multimeter (Rigol DM3058E)
layout: default
parent: 3. Electronics & Test Equipment
nav_order: 3
---

# Multimeter

A digital multimeter measures electrical quantities such as voltage, current, resistance, and continuity. It is one of the most useful tools for checking a circuit systematically instead of guessing.

MakerLabs uses the **Rigol DM3058E** bench multimeter. Handheld meters use the same measurement principles, but their controls, sockets, ranges, and safety ratings may differ.

{: .warning-title}
> Choose the function before connecting
>
> Voltage is measured **in parallel**. Current is measured **in series**. Resistance and continuity are measured only on a circuit that is switched off and safely discharged.
>
> Connecting a meter configured for current directly across a supply can create a short circuit, blow a fuse, damage equipment, or cause injury.

## Before every measurement

Use this quick check:

1. **Function:** What quantity are you measuring?
2. **Sockets:** Are the leads plugged into the correct inputs?
3. **Range:** Can the selected range safely include the expected value?
4. **Connection:** Should the meter be in parallel or in series?
5. **Circuit state:** Should power be on or off?

{: .tip}
> When the expected value is unknown, begin with a safely high range or use autoranging, then reduce the range if needed.

## Measuring DC voltage

Voltage is the potential difference between two points.

1. Put the black lead in the `LO` or common input.
2. Put the red lead in the voltage/resistance input.
3. Select DC voltage.
4. Connect the probes **in parallel** with the two points.
5. Read the value and sign.

A negative reading normally means the red probe is at a lower potential than the black probe.

Typical uses include checking a supply rail, battery, regulator output, or voltage across a component.

## Measuring AC voltage

Select AC voltage and connect the probes in parallel. Be clear whether the meter reports RMS voltage and whether the signal's frequency and shape are within the meter's specifications.

This Wiki is intended for low-voltage MakerLabs work. Do not measure mains or high-energy circuits unless you are trained, authorised, and using appropriately rated equipment and procedures.

## Measuring resistance

1. Switch the circuit off.
2. Disconnect external power sources.
3. Safely discharge capacitors.
4. Select resistance.
5. Measure across the component or network.

Components elsewhere in the circuit can create parallel paths and change the reading. Lift one component lead when an isolated value is required.

{: .warning}
> Never apply an external voltage while the meter is in resistance or continuity mode.

## Continuity testing

Continuity mode checks whether two points are connected by a sufficiently low resistance. Many meters beep when continuity is detected.

Use it to check:

- Wires and connectors
- Breadboard rows
- PCB tracks
- Switch contacts
- Suspected solder bridges
- Whether two points that should be separate are accidentally connected

A beep does not prove a connection can safely carry a large current, and no beep does not necessarily mean infinite resistance. Read the displayed value as well.

## Measuring current

To measure current, the meter must become part of the path:

1. Disable power.
2. Move the red lead to the correct current input if required.
3. Select DC or AC current and a suitable range.
4. Open the circuit at the measurement point.
5. Connect the meter **in series**.
6. Enable power and take the reading.
7. Disable power before disconnecting the meter.
8. Return the lead to the voltage input afterward.

{: .warning-title}
> Never “probe around” in current mode
>
> A current input has very low resistance. Placing it across a supply is effectively a short circuit. If you are unsure how to break the circuit and insert the meter in series, ask for help.

## Diode testing

Diode mode applies a small test current and displays the forward voltage.

1. Power the circuit off and discharge it.
2. Connect the red probe toward the diode's anode and black toward its cathode.
3. Read the forward voltage.
4. Reverse the probes and compare.

In-circuit components may affect the result. LEDs may glow faintly if the meter supplies enough test voltage.

## Common problems

### The display shows overload or an open circuit

The selected range may be too low, the probes may not be connected, the component may be open, or the measured resistance may exceed the range.

### Voltage reads zero

Check the function, sockets, reference point, circuit power, and whether both probes are contacting conductive points.

### Current reads zero

Check that the meter is actually in series, the correct current socket and range are selected, and the input fuse has not opened.

### Readings jump around

Improve probe contact, use a stable reference, reduce electrical noise, select a suitable range, and allow the reading to settle.

## Manufacturer documentation

- [Rigol DM3058/DM3058E User Guide](https://www.rigol.com/dam/global/downloads/brochures/en/user-manual/multimeters/DM3058_UserGuide_EN.pdf)
- [Local copy of the Rigol user guide](../../assets/pdfs/Wiki02_03_DM3058_UserGuide_EN.pdf)
