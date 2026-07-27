---
title: CAD for Fabrication
layout: default
parent: 2. Fabrication & Assembly
nav_order: 5
---

# CAD for Fabrication

Computer-aided design turns dimensions and constraints into parts that can be 3D printed, laser cut or machined.

## Start with intent

Identify:

- What the part locates, supports or protects
- Loads and likely failure directions
- Interfaces with boards, connectors and tools
- How it will be assembled and repaired
- Which process and material will make it

## Design with parameters

Use named dimensions for repeated or important values:

```text
material_thickness = 3.1 mm
pcb_width = 68.6 mm
clearance = 0.3 mm
```

If material changes, edit one parameter rather than many unrelated sketches.

## Tolerance and clearance

Manufactured parts are not exact. A `3 mm` sheet, hole or printed wall will vary.

- **Clearance fit:** intentional gap for easy assembly
- **Transition fit:** close fit with little movement
- **Interference fit:** parts press together

Create a small tolerance test before a large final part.

## For 3D printing

- Orient layers to resist the main load.
- Avoid unsupported overhangs where possible.
- Add fillets around stressed corners.
- Leave access for supports and fasteners.
- Use heat-set inserts only with appropriate wall thickness.

## For laser cutting

- Use closed vector paths.
- Account for kerf.
- Add dog-bone or relief features when square tabs must fit.
- Avoid tiny features that burn away.
- Keep engraving and cutting layers distinct.

## Enclosures

Check:

- Board and battery retention
- Connector and switch access
- Cable bend radius
- Ventilation and heat
- Antenna clearance
- Screwdriver access
- Finger clearance
- Assembly order

{: .tip}
> Import a model or outline of the real PCB instead of modelling it from memory.

## Release checklist

- Units are correct.
- Model is fully constrained where practical.
- No impossible internal assembly step exists.
- Export format matches the process.
- Critical dimensions are included in a drawing or notes.
- File name contains a useful revision.
