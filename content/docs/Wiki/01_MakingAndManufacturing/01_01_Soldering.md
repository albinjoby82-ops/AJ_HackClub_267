---
title: Soldering
layout: default
parent: 2. Fabrication & Assembly
nav_order: 1
---

# Soldering

Soldering joins electronic components by melting a filler metal called **solder** around the parts being connected. The solder flows over the metal surfaces and solidifies to form an electrical and mechanical connection.

The component leads and circuit board should get hot enough to melt the solder. You should not simply melt a blob onto the tip and wipe it onto a cold joint.

Solder comes in different alloys. Some solder contains lead, while common lead-free solder is usually based on tin with small amounts of other metals. Always identify the solder you are using and follow the workspace rules and its safety data sheet.

{: .warning-title }
> Safety first
>
> A soldering iron can exceed **300°C** and can cause serious burns or start a fire. Flux fumes can irritate the respiratory system, and solder or components may contain hazardous substances.
>
> Work under the required local fume extraction, keep the iron in its stand, tie back long hair, wear eye protection, and never solder a powered circuit. Ask a supervisor for help if you have not been trained.

## Watch: soldering demonstrated

If you learn better by watching, this EEVblog walkthrough covers the tools and shows real joints being made. Reading the steps below and watching a demonstration together is the fastest way to build good habits.

[EEVblog #180 — Soldering Tutorial Part 1: Tools](https://youtu.be/J5Sb21qbpEQ)

<iframe width="560" height="315" src="https://www.youtube.com/embed/J5Sb21qbpEQ" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

{: .tip}
> Continue with [Part 2: hand soldering](https://youtu.be/fYz5nIHH0iY) for through-hole technique, and [Part 3: surface mount](https://youtu.be/b9FC9fAlfQE) once you are comfortable with the basics.

## What you need

- A temperature-controlled soldering iron and stand
- The correct solder for the workspace
- Local fume extraction
- Eye protection
- A damp cellulose sponge or brass tip cleaner
- A heat-resistant work surface
- The circuit board and components
- Flush cutters
- Solder wick or a desoldering pump for corrections

{: .note}
> **Flux** removes surface oxides and helps molten solder flow. Most electronics solder contains a flux core, but additional electronics-grade flux can make difficult joints easier. Do not use plumbing flux on electronic circuits.

## Before you begin

1. Make sure the circuit is disconnected from every power source.
2. Check that the work area is clear of paper, loose wires, drinks, and flammable materials.
3. Position the fume extractor so fumes are drawn away from your face.
4. Put the iron in its stand and select a temperature suitable for the solder and components being used.
5. Check that the tip is clean, securely fitted, and lightly coated with solder.

## Tinning the tip

A thin coating of solder protects the tip from oxidation and improves heat transfer.

1. Clean the hot tip briefly with the approved tip cleaner.
2. Apply a small amount of fresh solder to the working surface of the tip.
3. The tip should look shiny and evenly coated, not covered by a large blob.

{: .tip}
> Clean and re-tin the tip whenever it becomes dull or stops transferring heat well. Do not scrape plated tips with a file or abrasive paper.

## Making a through-hole joint

1. Insert the component and secure it so it cannot move.
2. Touch the iron tip to both the component lead and the copper pad.
3. Wait briefly for both surfaces to heat.
4. Feed solder into the joint—not directly onto the iron tip.
5. Use only enough solder to cover the pad and form a smooth fillet around the lead.
6. Remove the solder first, then remove the iron.
7. Hold the joint still while it cools.
8. Trim the excess lead with flush cutters, directing the cut end away from people.

The exact heating time depends on the board, component, tip, solder, and temperature. If a joint is not flowing, stop and diagnose the cause rather than holding the iron on the component indefinitely.

## Inspecting the joint

A good through-hole joint should:

- Wet both the pad and component lead
- Form a smooth, concave fillet
- Use enough solder to cover the connection without forming a ball
- Contain no cracks, spikes, bridges, or loose movement
- Leave nearby pads and tracks undamaged

After the board has cooled, check continuity and inspect for accidental bridges before applying power.

## Common problems

### The solder forms a ball

The surfaces may be dirty, oxidised, or insufficiently heated. Clean the tip, add suitable flux if permitted, and heat both parts of the joint.

### The joint looks dull, rough, or cracked

The joint may have moved while cooling or may not have heated evenly. Apply flux and reflow it once, then keep it still.

### Two pads are joined accidentally

This is a **solder bridge**. Remove excess solder with solder wick or a desoldering pump, then inspect the tracks before powering the circuit.

### The solder will not melt

Check that the iron is switched on, at the correct temperature, and making good thermal contact. A small amount of fresh solder between the tip and joint can improve heat transfer.

{: .troubleshooting}
> If pads begin lifting, insulation melts, or a component becomes very hot, remove the iron and let everything cool. Repeated heating can permanently damage components and circuit boards.

## Desoldering

Desoldering is used to remove excess solder or replace a component.

1. Disconnect all power and allow charged components to discharge safely.
2. Add a small amount of fresh solder or flux to improve heat transfer.
3. Heat the joint.
4. Use solder wick or a desoldering pump to remove the molten solder.
5. Let the board cool before repeating.

Never pull a component out while the solder is solid; this can lift pads and tear tracks from the board.

## Finishing safely

1. Return the iron to its stand.
2. Clean and tin the tip.
3. Switch the iron and extraction equipment off as directed.
4. Allow the iron to cool where it cannot be touched accidentally.
5. Dispose of solder waste using the workspace's designated waste stream.
6. Clean the work surface and wash your hands before eating or drinking.

## Further reading

- [HSA guidance on chemical-agent risk assessment](https://hsa.ie/your_industry/chemicals/legislation_enforcement/chemical_agents_and_carcinogens/chemical_agents/risk_assessment/)
- [NIOSH information for workers handling lead](https://www.cdc.gov/niosh/lead/prevention/information-for-workers.html)
