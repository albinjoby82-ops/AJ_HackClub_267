---
title: Laser Cutting with xTool
layout: default
parent: 2. Fabrication & Assembly
nav_order: 3
---

# Laser Cutting with xTool

Build Club mainly uses xTool machines with xTool Creative Space (XCS). A laser cutter can cut vector outlines, score lines and engrave filled artwork.

The exact controls and supported materials depend on the xTool model, laser type and installed accessories. Follow the instructions beside the machine.

{: .warning-title}
> Training and supervision required
>
> A laser cutter can start a fire and produce harmful fumes. Use it only after induction, with extraction running, covers and interlocks working, and an approved material. Never leave a laser job unattended.

## Cut, score or engrave?

| Operation | What it does | Typical input |
| --- | --- | --- |
| Cut | Passes completely through along an outline | Vector path |
| Score | Marks an outline without cutting through | Vector path |
| Engrave | Removes material across an area | Bitmap or filled vector |

In XCS, only elements marked **Output** are processed. Check every layer before starting.

## Prepare the design

SVG is usually the best format for vector cutting.

- Use closed paths for cut outlines.
- Remove duplicate lines; otherwise the laser may process an edge twice.
- Convert text to paths if the receiving computer may not have the font.
- Join overlapping shapes where one continuous cut is intended.
- Keep engraving, scoring and cutting on clearly named layers.
- Keep the design inside the usable area.
- Add small test shapes when using a new material.

## Material approval

Use material with a known identity and an approved laser profile. Do not assume an unidentified plastic is safe.

Do not process PVC, vinyl, ABS or polycarbonate. xTool warns that these materials can produce harmful fumes, damage equipment or cut poorly. Do not use mirrored or highly reflective material unless the specific machine and procedure permit it.

For wood products, check the glue, coating and treatment—not only the visible surface.

## Set up the xTool

1. Inspect the machine, bed and extraction.
2. Remove scraps and residue from previous jobs.
3. Place the material flat and secure it without obstructing the tool path.
4. Select the correct machine and processing mode in XCS.
5. Select the known material or create a user-defined material.
6. Measure or enter material thickness.
7. Focus or run the machine's measurement process.
8. Assign **Engrave**, **Score** or **Cut** to each layer.
9. Start from the machine/material reference settings.
10. Frame or preview the job and confirm it stays on the material.

XCS settings commonly include power, speed and passes. Do not copy settings from a different machine merely because the material name matches.

## Test unfamiliar material

Use a small test grid or sample:

- Start with reference settings.
- Change one parameter at a time.
- Record machine, laser module, material, thickness, power, speed and passes.
- Choose the lowest energy that produces the required result cleanly.

## Processing order

Engrave before cutting so the material remains positioned. Cut internal holes before the outer profile where the layer order permits it.

## During the job

- Stay beside the machine and watch through the safe viewing area.
- Keep extraction and air assist running as required.
- Be ready to pause or stop.
- Stop for sustained flame, unusual smoke, lost extraction, moved material or an unexpected sound.
- Do not open covers or bypass an interlock during processing.

A flame that continues or grows is not normal. Stop the job and follow the room's fire procedure.

## Kerf and fitting parts

The laser removes a narrow width called the **kerf**. Its size varies with material, focus and settings.

For press-fit designs:

1. Cut a small slot test with several widths.
2. Test the fit.
3. Adjust the design for that material batch.
4. Record the successful allowance.

A nominal `3 mm` sheet may not actually measure exactly `3 mm`.

## After the job

1. Wait for smoke to clear as instructed.
2. Check that no material is glowing or hot.
3. Remove the work and loose scraps.
4. Clean residue using the approved method.
5. Leave extraction running for the required period.
6. Record useful settings.
7. Report flare-ups, extraction problems or damaged parts.

## xTool references

- [Cut settings in XCS](https://support.xtool.com/article/1885)
- [XCS workflow and processing settings](https://support.xtool.com/article/209)
- [Plastic material safety](https://support.xtool.com/article/870)
- [Fire-safety reminder](https://support.xtool.com/article/655)
