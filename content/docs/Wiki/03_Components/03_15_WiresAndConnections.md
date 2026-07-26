---
title: Wires, Jumper Cables, and Connectors
layout: default
parent: 4. Components
nav_order: 15
---

# Wires, Jumper Cables, and Connectors

Wires carry power and signals between circuit nodes. Choosing the correct conductor and termination is part of the electrical design, not just tidying.

## Solid and stranded wire

- **Solid core:** holds its shape and works well in solderless breadboards
- **Stranded:** flexible and better for moving cables, but normally needs a suitable crimp, terminal, or prepared end

Do not insert loose stranded wire into a breadboard; stray strands can short adjacent rows.

## Jumper cables

- Male-to-male: breadboard to breadboard
- Male-to-female: header pin to breadboard
- Female-to-female: header to header

Dupont-style jumpers are convenient for prototypes but are not locking, polarised, or suitable for high current.

## Wire size

Wire gauge affects resistance, heating, flexibility, and connector compatibility. Choose it for the expected current, length, insulation, environment, and terminal.

{: .warning}
> A wire or connector that “fits” may still be electrically unsafe. Check current, voltage, temperature, insulation, polarity, and contact ratings.

## Colour conventions

Common conventions include:

- Red: positive supply
- Black: ground or return
- Other colours: signals

Colour is only a label. Verify both ends before applying power.

## Connector families

Common laboratory connectors include:

- Pin headers and Dupont jumpers
- JST wire-to-board connectors
- Screw terminals
- Banana plugs
- BNC connectors
- USB connectors
- Barrel power connectors

Never assume two connectors with the same shape use the same pinout or voltage.

## Signal integrity

At higher frequency, wires behave as transmission paths and antennas. Keep fast signal loops short, provide a nearby return path, use twisted pairs or shielding where appropriate, and avoid long breadboard jumpers for sensitive clocks or analogue signals.

## Inspection

- Tug-test crimped wires gently.
- Check for exposed copper and stray strands.
- Verify continuity end to end.
- Verify no short exists between adjacent contacts.
- Label both ends of multiwire cables.
- Replace loose, overheated, or damaged connectors.
