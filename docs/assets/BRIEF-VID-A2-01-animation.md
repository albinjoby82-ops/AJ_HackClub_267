# VID-A2-01: animated explainer, how the day works

**Used in** A2, and as a recruitment asset on the event page
**Purpose** Explain the six hour build sprint to someone who has never heard of
Micromouse, faster than A1 and A2 can
**Status** Brief written, not commissioned

Below is a copy-paste prompt for Claude Design. It contains only confirmed facts
from [EVENT_FACTS.md](../EVENT_FACTS.md). Unconfirmed items are marked so the
designer does not invent them. Update this brief when decisions land, do not edit
the generated output to add facts.

Depends on: S11 running order, S1 team size, S10 room.

---

## Prompt

Design a cartoon storyboard, twelve frames, explaining a student robotics
competition to people who have never heard of it. Playful and warm, not corporate.
Think a good explainer video, not a university brochure.

### The event

Dublin Micromouse Open 2026. Saturday 26 September 2026, UCD Village, University
College Dublin, hosted by UCD ElecSoc. Ireland's first national Micromouse
competition.

The one idea everything hangs on: **every team gets six hours and the same box of
parts, and builds a maze-solving robot from scratch on the day.** Nobody arrives
with a finished robot. A first year who has never soldered lines up against a
final year team on equal terms.

A micromouse is a small robot that solves a maze entirely on its own. No remote
control, no driver, no human input once the run starts. It explores the maze,
builds a map, works out the fastest route to the centre, then drives that route
flat out.

### The frames

1. **Hook.** A tiny robot alone at the edge of a maze it has never seen. Caption:
   "It has to figure this out by itself."
2. **The four beats.** Explore, Understand, Optimise, Race. Four small panels, the
   same mouse in each.
3. **Explore.** The mouse feeling its way down a corridor, little sensor cones
   pinging off the walls, hitting dead ends.
4. **Map.** The maze redrawn as a glowing grid in the mouse's head, half filled in.
5. **Plan.** A route lighting up from start to centre, other routes fading.
6. **Speed run.** The same mouse, same maze, now a blur. Confetti at the centre.
7. **Cut to the real event.** A room full of students at benches. Caption: "Now
   build one. Six hours. Go."
8. **The kit.** An identical box opened on every bench. Contents to draw: an ESP32
   microcontroller, encoded motors, a motor driver, an IMU, distance sensors, a
   battery management system, a buck converter, a battery pack. Draw them as
   friendly labelled components, not a technical exploded diagram.
9. **The day.** A horizontal ribbon: ARRIVE, BRIEFING, BUILD, TEST, MAP, RACE,
   PRIZES. Show BUILD, TEST and MAP looping back on each other, because they do.
   No clock times: they are not confirmed.
10. **Help is everywhere.** A 30 minute opening briefing covering the electronics,
    GitHub basics and maze-solving strategies. Committee members and postgraduate
    demonstrators on the floor all day. Practice mazes, full size and mini, open
    all day. One mini maze is built so the fastest route cuts the diagonals.
11. **Race day.** The competition maze, a judge with a stopwatch, teams watching.
    Caption: "Fastest verified run to the centre wins." Plus awards for design and
    reliability.
12. **Close.** Tagline "Build it. Code it. Race it." Date, venue, host. A
    reassuring line: "No experience needed. Just show up."

### Recurring characters

Two or three students who appear across frames so there is a story, not a
diagram. Deliberately mixed: someone visibly nervous in frame 7 who is grinning in
frame 11. Beginners are the target audience, so draw beginners.

The mouse itself is the mascot. Give it a consistent silhouette and a bit of
personality through posture and sensor angle, no face, no eyes. It is a robot,
not a character in a children's cartoon.

### Style

- Cartoon, clean vector, bold outlines, flat colour with minimal shading.
- Chunky and confident. Nothing delicate or wispy.
- Palette: near-black `#1F2D3D` for line and text, warm off-white `#F9FAFC`
  ground, `#EC3750` red as the single loud accent used sparingly, `#338EDA` blue
  for supporting elements, `#FF8C37` orange used once, for the winning moment.
  Deep teal and mint or cyan circuit accents are the host society's colours and
  are welcome in backgrounds.
- Maze walls read as real physical walls on a board, not as a screen grid.
- Every frame legible as a thumbnail. If a caption needs squinting, cut it.

### Copy rules

- Irish and British English. Organise, colour, centre.
- Never use em dashes.
- Captions are one short line. No paragraphs anywhere.
- Say "team", "kit", "speed run", "exploration run", "micromouse", "six hours".
- Never say "participants", "contestants", "hackers", "AI assistant".

### Do not invent

These are genuinely undecided. Leave them out rather than guessing:

- Any clock time, start time or finish time
- Team size, or the number of people drawn per bench beyond a vague small group
- Maze dimensions, cell count, wall measurements
- Number of runs, penalties, scoring formula
- Prize amounts, or any prize beyond "credits package for the winning team"
- The room, the building, or any interior that looks like a specific place
- Any sponsor logo other than a plain text credit to Anthropic as technical
  partner and the UCD School of Electrical and Electronic Engineering

### Deliverable

Twelve artboards, 16:9, laid out in reading order on one canvas, numbered, each
with its caption set as real text so it can be edited. Add a thirteenth artboard
holding the palette swatches and the mouse mascot turnaround, so the style can be
reused for posters and slides.
