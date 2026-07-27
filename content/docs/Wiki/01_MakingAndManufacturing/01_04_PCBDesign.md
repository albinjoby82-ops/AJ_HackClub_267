---
title: PCB Design with KiCad
layout: default
parent: 2. Fabrication & Assembly
nav_order: 4
---

# PCB Design with KiCad

A printed circuit board turns a tested circuit into a repeatable assembly. KiCad is a free, open-source tool for schematics and PCB layout.

## Workflow

```text
requirements → schematic → footprints → layout → checks → manufacturing files
```

## 1. Draw the schematic

- Use named power symbols and net labels.
- Add connector labels and test points.
- Include decoupling capacitors beside every relevant IC supply.
- Include programming and debugging connections.
- Mark voltage levels and expected current.
- Give components useful reference designators and values.

Run the electrical rules checker, then review every warning rather than dismissing all of them.

## 2. Assign footprints

The schematic symbol describes electrical function. The footprint describes physical pads.

Check:

- Package name and dimensions
- Pin numbering
- Connector orientation
- Hole and pad sizes
- Component height
- Availability of the exact part

Print the board at 1:1 scale and place real components on the page when possible.

## 3. Define the board

- Draw a closed board outline.
- Add mounting holes early.
- Place connectors and controls based on the enclosure.
- Keep antenna areas clear.
- Leave space for tools, cables and fingers.

## 4. Place and route

Place related components together. Keep decoupling capacitors close to supply pins. Use wider tracks for higher current and a sensible ground plane.

Avoid right-at-the-edge pads, unnecessary vias and traces beneath areas that must remain clear.

## 5. Check it

- Run design-rule checks.
- Inspect unconnected nets.
- Review polarity and pin 1.
- Check connector pinout from both sides.
- Inspect the 3D view.
- Have another person review the schematic and board.

## 6. Generate manufacturing files

A board manufacturer normally needs:

- Gerber layers
- Drill files
- Board outline
- Fabrication notes

Assembly services may also need a bill of materials and component-position file.

Open the generated files in a separate Gerber viewer before ordering.

{: .warning}
> Do not place an order until every connector, footprint, polarity mark and board dimension has been independently checked.

## First power-up

1. Inspect the unpowered board.
2. Check resistance between power and ground.
3. Use a current-limited supply.
4. Verify supply rails before fitting expensive modules.
5. Test one subsystem at a time.
