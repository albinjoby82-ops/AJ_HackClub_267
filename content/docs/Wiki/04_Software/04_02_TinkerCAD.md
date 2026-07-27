---
title: Tinkercad Circuits
layout: default
parent: 5. Software
nav_order: 2
---

# Tinkercad Circuits

Tinkercad Circuits is a browser-based simulator for breadboards, Arduino boards and common components. It is useful for learning and testing an idea before physical parts are available.

This walkthrough shows how to place an Arduino, wire components, and run a simulation:

[Free Online Arduino Simulator — Tinkercad](https://youtu.be/i27L_wcXcp0)

<iframe width="560" height="315" src="https://www.youtube.com/embed/i27L_wcXcp0" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

## Create a circuit

1. Sign in to [Tinkercad](https://www.tinkercad.com/).
2. Open **Circuits** and create a new design.
3. Drag an Arduino Uno and breadboard into the workspace.
4. Add components and connect them by clicking their terminals.
5. Open **Code**, choose **Text**, then start the simulation.

## Good simulation habits

- Name the design and components clearly.
- Use consistent wire colours.
- Place resistors and components exactly as you would physically.
- Check common-anode versus common-cathode RGB LEDs.
- Stop the simulation before rewiring.
- Use the Serial Monitor to inspect values.

## What simulation does not prove

A simulation cannot fully model:

- Loose connections and damaged components
- USB cable and driver problems
- Real motor startup current
- Electrical noise and timing variation
- Heat, mechanical load or battery behaviour

Treat a successful simulation as evidence that the idea is plausible—not a guarantee that physical hardware will behave identically.

{: .tip}
> Share the design link with a helper when asking for support. It is much easier to diagnose a complete circuit than a cropped screenshot.
