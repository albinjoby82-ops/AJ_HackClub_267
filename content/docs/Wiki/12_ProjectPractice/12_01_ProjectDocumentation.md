---
title: Planning and Documenting a Project
layout: default
parent: 8. Project Practice
nav_order: 1
---

# Planning and Documenting a Project

Good documentation lets a future club member reproduce the project without guessing.

## Before building

Write:

- One-sentence problem statement
- User and use environment
- Must-have requirements
- Useful extras
- Constraints such as budget, size and deadline
- Main risks and untested assumptions

## Draw a block diagram

```text
controls → microcontroller → motor driver → motor
                ↓
             display
```

Show power separately when several voltages or supplies are used.

## Bill of materials

| Qty | Part | Exact value/model | Source | Notes |
| ---: | --- | --- | --- | --- |
| 1 | Controller | ESP32-C6 DevKit | Club stock | 3.3 V logic |
| 2 | Resistor | 330 Ω, 0.25 W | Parts drawer | LED current limit |

“One sensor” is not enough information when many modules look alike.

## README structure

1. What the project does
2. Photo or diagram
3. Parts and tools
4. Wiring
5. Software setup
6. How to build and run it
7. Tests performed
8. Known limitations
9. Safety notes
10. Credits and licence

## Record decisions

Explain why a choice was made:

```text
Used a separate 5 V servo supply because USB power caused resets.
```

This is more useful than only recording the final wiring.

## Test plan

| Test | Method | Expected result | Result |
| --- | --- | --- | --- |
| Power rail | Measure at controller | 4.8–5.2 V | |
| Button | Press 20 times | One event per press | |
| Runtime | Run from full battery | At least 4 h | |

## Version and ownership

- Keep source files, not only exported images or binaries.
- Use Git for text, code and compatible design files.
- Name large CAD exports with clear revisions.
- Credit images, teaching material and contributors.
- Choose a licence when sharing a reusable project.

{: .tip}
> Update documentation while the reason is still fresh, not the night before handover.
