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

---

## Alternative prompt: timed motion piece

Use this instead of the storyboard prompt when the target tool builds animation
from timed sections rather than artboards. Same facts, same do-not-invent list.

Build a 30 second looping animation, 1920x1080, explaining the Dublin Micromouse
Open 2026 to someone who has never heard of Micromouse. Cartoon-ish and warm, not
corporate abstract motion. The subject is a real event, so every beat must carry
information.

**Subject.** A micromouse is a small robot that solves a maze entirely on its own.
No remote control, no driver, no human input once the run starts. It explores,
maps the maze, plans the fastest route to the centre, then drives it flat out.

At the Dublin Micromouse Open, every team gets six hours and an identical box of
parts, and builds the robot from scratch on the day. Nobody arrives with a
finished robot. Saturday 26 September 2026, UCD Village, University College
Dublin, hosted by UCD ElecSoc.

**Sections.**

1. **Drop in, 3s.** An empty 16x16 maze grid draws itself in, walls settling into
   place. A small robot fades in at the bottom-left cell. Caption: "It has never
   seen this maze."
2. **Explore, 6s.** The robot drives cell to cell, sensor cones pulsing left,
   right and ahead. Walls it detects light up and stay lit. It hits a dead end,
   reverses, tries another branch. Trail dims behind it. Caption: "Explore."
3. **Map, 4s.** The camera lifts. The discovered walls resolve into a clean
   overhead map. Unvisited cells stay dark. Caption: "Map."
4. **Plan, 3s.** Flood fill: numbers or colour spread outward from the centre cell
   across the map, then one route ignites from start to centre and everything else
   dims. Caption: "Plan."
5. **Speed run, 4s.** The robot runs that route at speed, motion blur, tight
   corners. It hits the centre. Brief flash of the accent colour. Caption:
   "Race."
6. **Hard cut to the build, 5s.** The maze shrinks away. An identical parts box
   opens: ESP32 microcontroller, encoded motors, motor driver, IMU, distance
   sensors, battery management system, buck converter, battery pack. Components
   fly into place and assemble into the robot from section 1. Caption: "Now build
   one."
7. **The day, 3s.** A horizontal ribbon fills left to right: ARRIVE, BRIEFING,
   BUILD, TEST, MAP, RACE, PRIZES. BUILD, TEST and MAP visibly loop back on each
   other. A six hour counter runs alongside it. No clock times.
8. **Close, 2s.** Title lands: Dublin Micromouse Open 2026. Below it: Saturday 26
   September 2026, UCD Village, UCD. Tagline: "Build it. Code it. Race it." Then
   one line, smaller: "No experience needed."

Loop back to section 1 cleanly.

**Motion.** The robot is the through-line and should never cut. It persists across
sections 1 to 6 and glides between them. Easing should feel mechanical but eager,
quick starts and settled stops, like a small motor. Nothing floats or drifts.

**Style.** Flat vector cartoon, bold outlines, minimal shading. Maze walls read as
physical walls on a board, not a screen grid. Legible at thumbnail size.

**Palette.** Near-black `#1F2D3D` line and text, warm off-white `#F9FAFC` ground,
`#EC3750` red as the single loud accent, `#338EDA` blue for sensor cones and the
planned route, `#FF8C37` orange used exactly once, when the robot reaches the
centre.

**Type.** One confident geometric sans. Captions are one short line, lower third,
no paragraphs anywhere.

**Copy rules.** Irish and British English. Never use em dashes. Say "team", "kit",
"speed run", "exploration run", "micromouse", "six hours".

**Do not invent.** Undecided, so leave out rather than guess: any clock time, team
size or number of people shown, real maze dimensions or cell measurements, number
of runs, penalties, scoring, prize amounts, the room or any specific interior, and
any sponsor logo. A plain text credit to Anthropic as technical partner and the
UCD School of Electrical and Electronic Engineering is fine. The 16x16 grid in
section 1 is a visual convention only and must not be labelled with dimensions.
