# Asset index

Every image, diagram and video in Section A, with a stable ID. Reference assets
by ID in prose so a swapped file does not orphan a caption.

- **Diagrams** that can be generated are generated. They live in `diagrams/` as
  SVG, or inline in the page as Mermaid.
- **Photographs and maps** need a human. Each has a brief below and a
  placeholder SVG committed at `images/<ID>.svg` so pages render without broken
  images. Replacing the placeholder means dropping in the real file and updating
  the one reference in the page.

| Status | Meaning |
|---|---|
| Done | Committed and in use |
| Needed | Placeholder in place, real asset outstanding |
| Blocked | Cannot be produced until a decision lands |

## Summary

| ID | Page | Type | Status |
|---|---|---|---|
| [DIA-A1-01](#dia-a1-01) | A1 | Mermaid, inline | Done |
| [DIA-A2-01](#dia-a2-01) | A2 | Mermaid, inline | Done |
| [DIA-A3-01](#dia-a3-01) | A3 | SVG | Done |
| [DIA-A3-02](#dia-a3-02) | A3 | Mermaid, inline | Done |
| [DIA-A6-01](#dia-a6-01) | A6 | Mermaid, inline | Done |
| [IMG-A1-01](#img-a1-01) | A1 | Photo | Needed |
| [IMG-A2-01](#img-a2-01) | A2 | Photo | Needed |
| [IMG-A3-01](#img-a3-01) | A3 | Photo, annotated | Blocked |
| [IMG-A3-02](#img-a3-02) | A3 | Technical drawing | Blocked |
| [IMG-A6-01](#img-a6-01) | A6 | Screenshot | Needed |
| [IMG-A8-01](#img-a8-01) | A8 | Map | Blocked |
| [IMG-A8-02](#img-a8-02) | A8 | Map | Needed |
| [VID-A1-01](#vid-a1-01) | A1 | Video embed | Needed |
| [VID-A2-01](#vid-a2-01) | A2 | Animated explainer | Needed |
| [VID-A1-02](#vid-a1-02) | A1 | Algorithm animation | Needed |

## Generated diagrams

### DIA-A1-01
**Title** Explore, understand, optimise, race loop
**Used in** A1
**Purpose** Show the whole sport as one cycle before any prose is read
**Type** Mermaid flowchart, inline
**Status** Done

### DIA-A2-01
**Title** Shape of the day
**Used in** A2
**Purpose** Arrive, briefing, build, test, map, race, prizes, with the iteration loops
**Type** Mermaid flowchart, inline
**Status** Done. Sequence only; clock times are pending decision S11

### DIA-A3-01
**Title** Maze layout concept
**Used in** A3, section 3.3
**File** `diagrams/DIA-A3-01-maze-layout.svg`
**Purpose** Show start cell, goal area and perimeter in one glance, with dimensions openly marked as undecided
**Type** SVG, generated
**Ratio** 16:9 approximately, scales to container
**Caption** Maze layout concept. Grid and cell dimensions are not yet decided, see clauses 3.3.1 to 3.3.4
**Status** Done. Regenerate when decisions B1 to B4 land, then it becomes the basis for IMG-A3-02

### DIA-A3-02
**Title** Run procedure flow
**Used in** A3, section 3.4
**Purpose** Placement, hands clear, signal, exploration, return, speed run, time recorded
**Type** Mermaid flowchart, inline
**Status** Done

### DIA-A6-01
**Title** Setup verification chain
**Used in** A6
**Purpose** Install, compile, connect, flash, serial output, ready. Lets a competitor see where they stopped
**Type** Mermaid flowchart, inline
**Status** Done

## Assets needed from a human

### IMG-A1-01
**Title** Competition micromouse hero photograph
**Used in** A1
**File** `images/IMG-A1-01.svg` (placeholder)
**Purpose** Immediately show what a micromouse actually looks like. Most readers have never seen one
**Type** Photograph
**Ratio** 16:9, minimum 1600 px wide
**Caption** A micromouse in a maze cell, sensors facing the walls
**Source requirement** A real micromouse in a real maze, sensors visible, sharp. If none of ours exists yet, licence one or shoot a prototype. Do not use a stock render
**Status** Needed

### IMG-A2-01
**Title** Build floor photograph
**Used in** A2
**File** `images/IMG-A2-01.svg` (placeholder)
**Purpose** Show that the build sprint is a room full of people, not a lab bench
**Type** Photograph
**Ratio** 16:9
**Caption** Teams building on the day
**Source requirement** ElecSoc Makerthon or RoboExpo archive is acceptable until the Open happens. Faces need consent, see decision S14
**Status** Needed. Not yet placed in A2; add it once a usable frame is chosen

### IMG-A3-01
**Title** Annotated competition maze photograph
**Used in** A3, section 3.3
**File** `images/IMG-A3-01.svg` (placeholder)
**Purpose** Remove all doubt about what the competition maze physically is
**Type** Photograph with callout annotations
**Ratio** 16:9
**Caption** Annotated photograph of the competition maze
**Source requirement** Photograph the built competition maze. Annotate start cell, goal area, wall and post
**Status** Blocked on the maze being built, and on decisions B1 to B4

### IMG-A3-02
**Title** Final dimensioned maze drawing
**Used in** A3, section 3.3
**File** `images/IMG-A3-02.svg` (placeholder)
**Purpose** The authoritative measurements teams design against
**Type** Technical drawing, SVG
**Ratio** Fits page width
**Caption** Final dimensioned maze drawing
**Source requirement** Produced from the confirmed measurements, not from convention. Must state units and tolerance
**Status** Blocked on decisions B1 to B4

### IMG-A6-01
**Title** Successful flash and serial output screenshot
**Used in** A6
**File** `images/IMG-A6-01.svg` (placeholder)
**Purpose** Show a competitor exactly what success looks like so they can compare
**Type** Screenshot
**Ratio** 16:10
**Caption** A successful upload, with the verification sketch printing to the serial monitor
**Source requirement** Take it on the actual kit board once decision S16 lands. Crop to the output pane, no personal paths visible
**Status** Needed. Not yet placed in A6

### IMG-A8-01
**Title** Route from the UCD Village entrance to the event room
**Used in** A8
**File** `images/IMG-A8-01.svg` (placeholder)
**Purpose** Get a competitor from the entrance to the door without asking anyone
**Type** Map, SVG
**Ratio** 4:3
**Caption** From the UCD Village entrance to the event room
**Source requirement** Needs decision S10, the exact room and building. Mark the step-free route separately from the shortest route. Must be legible in greyscale, with a north arrow and a scale bar. Confirm the base map licence before tracing anything
**Status** Blocked on decision S10

### IMG-A8-02
**Title** Campus arrival map
**Used in** A8
**File** `images/IMG-A8-02.svg` (placeholder)
**Purpose** Show bus stops, the cycle route and the walking route to UCD Village on one image
**Type** Map, SVG
**Ratio** 4:3
**Caption** Arriving at UCD Belfield
**Source requirement** Base map licence must be confirmed. Do not trace a copyrighted map. Keep it legible in greyscale
**Status** Needed

### VID-A2-01
**Title** Animated explainer, how the day works
**Used in** A2, and as a recruitment asset on the event page
**Purpose** Explain the six hour build sprint faster than A1 and A2 can
**Type** Cartoon storyboard, twelve frames, 16:9
**Brief** [BRIEF-VID-A2-01-animation.md](BRIEF-VID-A2-01-animation.md), contains a copy-paste design prompt
**Source requirement** Commissioned or generated. The brief lists what must not be invented
**Status** Needed. Brief written, not commissioned

### VID-A1-02
**Title** Flood fill search, animated
**Used in** A1, route planning section
**Purpose** Show how a micromouse actually searches, honestly enough to implement from
**Type** Simulated algorithm animation, 16:9, looping
**Brief** [BRIEF-VID-A1-02-flood-fill.md](BRIEF-VID-A1-02-flood-fill.md), full algorithm spec with pseudocode
**Source requirement** The algorithm must be simulated, not faked with a pre-drawn path. 8x8 maze so distance numbers stay legible
**Status** Needed. Brief written, not commissioned

## Map specification, IMG-A8-01 and IMG-A8-02

| Field | Value |
|---|---|
| Format | SVG, committed to the repository, no external font or image references |
| Colour | Legible in greyscale, since competitors print these. Do not encode meaning in colour alone |
| Text | Irish/British English, no em dashes, minimum effective 12px label size |
| Accessibility | Every marked feature named in text on the image, not only by icon. Alt text as written above |
| Orientation | North arrow on both |
| Scale | Scale bar in metres on both |
| Licence | [INFO REQUIRED: base map source and its licence. Do not trace a copyrighted map] |

**IMG-A8-01, route from the UCD Village entrance to the event room**

- Portrait, sized to be readable on a phone at arm's length.
- Show the UCD Village entrance used by competitors, labelled.
- Show the walking route as a single bold line with direction arrows.
- Show the event building and the event room, labelled with the room's real
  signage name.
- Mark, if they exist on the route: steps, ramps, lifts, doors that need a card.
- Mark the step-free alternative as a distinct, separately labelled line.
- Mark the registration desk position.
- Include walking time in minutes from entrance to room.
- [INFO REQUIRED: the room, the entrance and the step-free route, all of which
  this image cannot be drawn without.]

**IMG-A8-02, campus arrival map**

- Landscape, sized for a printed A4 page and for the site.
- Show the UCD Belfield campus outline and the N11 Stillorgan Road edge.
- Mark the campus entrances competitors will use, labelled.
- Mark the bus stops served by the verified routes, labelled with route numbers
  46a, 39a, 145 and 17.
- Mark Sydney Parade DART station off-map with a direction arrow and the
  walking route onto campus.
- Mark cycle parking near UCD Village.
- Mark visitor pay and display parking areas, without stating price or
  availability.
- Mark UCD Village prominently, as the destination.
- Do not mark the DART shuttle bus, as it does not run on Saturdays.

### VID-A1-01
**Title** Exploration run and speed run clip
**Used in** A1
**Purpose** Sixty seconds of footage explains the sport better than the whole page
**Type** Video embed, 60 to 90 seconds
**Ratio** 16:9
**Caption** An exploration run and a speed run, side by side
**Source requirement** Either licensed contest footage with permission, or our own. The embed location is already marked in A1 as an HTML comment
**Status** Needed

---

[Documentation home](../index.md) · [Competitor docs](../competitor/index.md) · [Decision queue](../audits/HUMAN_DECISIONS_REQUIRED.md)
