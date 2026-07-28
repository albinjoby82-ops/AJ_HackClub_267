---
title: 3D Printing
layout: default
parent: 2. Fabrication & Assembly
nav_order: 2
---

# 3D Printing

3D printing is an **additive manufacturing** process: an object is built layer by layer from a digital model. It is useful for prototypes, brackets, enclosures, gears, jigs, and custom parts that would be difficult to make by hand.

The two common processes described here are **FDM** printing and **resin** printing. They use different materials, preparation steps, and safety controls.

{: .warning-title }
> Use the correct workspace procedure
>
> 3D printers contain hot surfaces and moving mechanisms. Resin printers also use chemicals that require gloves, eye protection, ventilation, careful cleaning, and controlled waste disposal.
>
> Do not reach into a running printer. Do not handle uncured resin without the required training and protective equipment.

## From idea to printed part

Most prints follow the same basic workflow:

1. Create or download a 3D model.
2. Export it as a suitable mesh or manufacturing file, commonly STL or 3MF.
3. Open the model in a **slicer**.
4. Choose the printer, material, orientation, layer height, infill, walls, and supports.
5. Inspect the sliced preview for unsupported regions or unexpected gaps.
6. Send the generated printer instructions to the correct machine.
7. Prepare the printer and build surface.
8. Start the print and observe the first layers.
9. Remove the completed part safely.
10. Remove supports and perform any required post-processing.

{: .tip}
> The slicer's time and material estimates are useful, but they are not guarantees. Leave margin when planning a part for a deadline.

## FDM printing

**Fused deposition modelling (FDM)** feeds plastic filament into a heated nozzle. The printer deposits thin lines of softened plastic to build each layer.

Common materials include:

- **PLA** — easy to print and suitable for many prototypes
- **PETG** — tougher and more temperature-resistant than PLA, but can string
- **ABS or ASA** — useful for stronger or warmer environments, but usually require controlled ventilation and an enclosed printer
- **TPU** — flexible, but more difficult to feed and tune

Always use a material approved for the printer and workspace.

### Watch: how FDM printing works

New to FDM? This beginner's guide walks through what the machine is doing as it lays down each layer, which makes the slicer settings below much easier to picture.

[ANYONE Can Use FDM 3D Printers — The Beginner's Guide](https://youtu.be/Pz7GMZCCJLU)

<iframe width="560" height="315" src="https://www.youtube.com/embed/Pz7GMZCCJLU" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

### Important slicer settings

| Setting | What it changes |
| --- | --- |
| Layer height | Surface detail, print time, and the size of each vertical step |
| Walls or perimeters | Strength and stiffness around the outside of the part |
| Infill | Internal structure; more infill is not always the best way to add strength |
| Top and bottom layers | Thickness of the solid outer surfaces |
| Supports | Temporary material beneath overhangs |
| Brim | Extra material around the first layer to improve bed adhesion |
| Temperature | How the material melts and bonds |
| Print speed | Printing time, accuracy, and reliability |

### Orientation matters

FDM parts are usually weaker between layers than along a layer. Orient the part so important loads do not try to pull the layers apart.

Orientation also affects:

- The amount of support material
- Surface finish
- Dimensional accuracy
- Print duration
- Whether holes print cleanly

{: .think-title}
> Before slicing, ask:
>
> **Where will this part bend or break, and which direction should the layers run to resist that force?**

### Starting an FDM print

1. Confirm that the selected printer and nozzle match the slicer profile.
2. Check that the loaded filament matches the selected material.
3. Make sure the build plate is clean and correctly installed.
4. Inspect the nozzle area for loose plastic or obvious damage.
5. Start the print and watch the first layer.

The first layer should be continuous and attached to the bed. Stop the print if material is gathering around the nozzle, lines are not sticking, or the nozzle appears to scrape the build surface.

### Common FDM problems

#### The first layer will not stick

- Clean the build plate using the approved method.
- Confirm that the correct build surface and material profile are selected.
- Check first-layer calibration or bed levelling.
- Use a brim if the part has little contact area.

#### The corners lift

This is **warping**. Reduce drafts, use the correct bed temperature, add a brim, and reconsider the material or part orientation.

#### Fine strands appear between features

This is **stringing**. Wet filament, unsuitable temperature, or retraction settings may contribute.

#### Layers shift sideways

Stop the print. Check for a collision, loose belt, obstructed motion, or a part that has detached from the bed.

#### The finished part is weak

Check the layer orientation, wall count, print temperature, material condition, and whether the model contains very thin features.

## Resin 3D Printing

Resin printers selectively expose liquid photopolymer resin to light, hardening one layer at a time. They can produce very fine details and smooth surfaces, but require more careful handling and post-processing than FDM printers.

{: .warning-title}
> Uncured resin requires chemical controls
>
> Wear compatible nitrile or neoprene gloves, eye protection, and protective clothing as required by the resin's safety data sheet. Work in the designated ventilated area.
>
> Do not touch resin with bare skin. Do not wash liquid resin or contaminated solvent into a sink. Isopropyl alcohol is flammable and must be kept away from heat, sparks, and flames.

### Typical resin workflow

1. Inspect the model and orient it to manage supports, suction forces, and visible surfaces.
2. Add supports and inspect every layer in the slicer.
3. Confirm that the resin and print settings are compatible.
4. Prepare the printer while wearing the required protective equipment.
5. Print the part.
6. Allow excess resin to drain as directed.
7. Remove the part using the approved tools.
8. Wash it using the specified solvent and procedure.
9. Remove supports at the recommended stage.
10. Fully post-cure the part using the material manufacturer's settings.
11. Clean the workspace and dispose of contaminated materials correctly.

Liquid, partly cured, and solvent-dissolved resin may require disposal through a chemical waste stream. Follow the safety data sheet, manufacturer guidance, workspace procedure, and local waste rules.

## Designing parts for printing

- Avoid walls thinner than the printer and material can reproduce reliably.
- Add clearance between parts that need to fit or move.
- Use fillets around stressed internal corners.
- Design screw holes and inserts for the intended fastening method.
- Avoid unnecessary supports by changing orientation or using chamfers.
- Print a small test piece before committing to a large or expensive job.
- Record the material and settings when a print works well.

{: .extra}
> A model being printable does not mean it is suitable for its final use. Consider load, temperature, UV exposure, chemicals, electrical insulation, fire behaviour, and how failure could affect people.

## Before using a printed part

Inspect it for:

- Cracks, layer separation, or incomplete regions
- Loose support material
- Incorrect dimensions or poor fit
- Sharp edges
- Deformation around holes or fasteners

Do not use a printed part for safety-critical lifting, mains electrical protection, pressure containment, food contact, or other hazardous applications unless the material, design, manufacturing process, and inspection have been appropriately engineered and approved.

## Further reading

- [Formlabs resin safety guidance](https://formlabs.com/global/support/Safety-Formlabs-SLA-printers/)
- [Formlabs guidance for disposing of resin and used solvent](https://formlabs.com/support/How-can-I-dispose-of-resin-and-used-solvent/)
