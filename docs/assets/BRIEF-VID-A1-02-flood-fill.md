# VID-A1-02: flood fill search, animated

**Used in** A1, route planning section
**Purpose** Show how a micromouse actually searches a maze, honestly enough that a
competitor could implement it from watching
**Status** Brief written, not commissioned

This is an algorithm spec, not a mood brief. The animation is only convincing if
the algorithm underneath is real. Hand the whole thing to the animating agent.

---

## Prompt

Animate a micromouse solving an unknown maze with the flood fill algorithm.
Simulate the algorithm properly and render the simulation. Do not fake the motion
with a pre-drawn path.

### Why most versions of this look wrong

The mouse cannot see the maze. It knows only the walls it has personally sensed
from cells it has visited. Flood fill works by assuming every wall it has not yet
seen is **open**, planning the shortest route under that optimistic assumption,
driving it, and re-planning the moment a newly sensed wall proves the assumption
wrong.

That cycle, commit, get blocked, re-flood, turn around, is the entire character of
the algorithm. An animation where colour spreads once and the mouse drives a
perfect line to the centre is not flood fill and reads as fake. Show the mouse
being wrong, repeatedly, and recovering.

### State to hold

- `walls[cell][direction]` for north, east, south, west. Three values: `open`,
  `wall`, `unknown`. Everything starts `unknown` except the outer boundary, which
  is `wall`.
- `dist[cell]`, an integer per cell, recomputed by the flood.
- `visited[cell]`, boolean, for rendering only.
- Mouse `position` and `heading`.

### The flood

Recompute `dist` from scratch every time a new wall is discovered.

```
flood(targets):
    set every dist[cell] = infinity
    queue = targets            # the goal cells, or the start cell when returning
    for each t in targets: dist[t] = 0
    while queue not empty:
        cell = pop front of queue
        for each neighbour n of cell:
            if walls[cell][direction to n] is 'wall': skip     # unknown counts as open
            if dist[n] > dist[cell] + 1:
                dist[n] = dist[cell] + 1
                push n onto queue
```

This is breadth first search outward from the goal. Unknown walls are treated as
open, which is what makes the mouse optimistic.

### The search loop

```
flood(goalCells)
while mouse not in goalCells:
    sense()                    # read left, right and front walls at current cell
    if any wall newly discovered:
        flood(goalCells)       # re-plan
    candidates = neighbours reachable from current cell (no known wall between)
    next = candidate with the lowest dist
    prefer, on a tie: straight ahead, then the direction needing the smaller turn
    move to next
```

`sense()` sets three wall values only, for the cell the mouse currently occupies,
in the three directions it can see. It cannot see behind itself and it cannot see
into other cells. Walls are symmetric: setting a wall on one side of a boundary
sets it on the other.

After reaching the goal, run the same loop with `flood(startCell)` to drive back.
Only then is the speed run possible.

### Maze size

Use **8x8**, not 16x16. Distance numbers must be legible on screen and a real
16x16 search takes hundreds of moves. Place the goal as a 2x2 block at the centre
and the start in the bottom-left corner facing north.

Generate a maze with a proper generator so it has real dead ends and loops, then
verify the goal is reachable. Hand-drawn mazes tend to be too easy and the mouse
never gets blocked, which loses the whole point.

### Rendering

| Element | Treatment |
|---|---|
| Known wall | Solid, near-black, full weight |
| Unknown wall | Not drawn at all. The mouse does not know it exists |
| Cell distance number | Small, centred, only on cells with a finite distance |
| Visited cell | Very slightly tinted ground, so the explored region is readable |
| Current cell | Accent outline |
| Planned route | The chain of decreasing distances from the mouse to the goal, drawn as a thin line, redrawn every flood |
| Goal block | Persistent accent tint, 2x2 at the centre |
| Sensor reading | Three short cones from the mouse, flashing once per step |

### Motion

- One cell per step. The mouse translates between cell centres, it never cuts
  corners or moves diagonally during the search.
- Turning is a separate, visible beat. Rotate in place, then move. A mouse that
  slides sideways looks wrong to anyone who has seen a real one.
- Roughly 0.35 seconds per step, faster as the run goes on so the tail does not
  drag.
- **Hold on every re-flood.** Freeze the mouse for about 0.4 seconds while the
  numbers visibly recompute outward from the goal. This is the moment the audience
  understands what is happening, so give it room.
- When a newly sensed wall blocks the planned route, let the mouse start toward it
  and stop short before turning. That hesitation sells it.

### Beats to make sure survive

1. First flood, before any wall is known: distances form clean concentric rings
   around the centre, because the mouse believes the maze is empty.
2. First blocked route: the mouse heads confidently at the centre, meets a wall,
   re-floods, and the ring pattern buckles.
3. At least one dead end entered and reversed out of.
4. The moment the route flips to a completely different side of the maze after a
   re-flood.
5. Arrival at the goal, then the return leg back to the start, which surprises
   people who assume the run is over.

### Palette

Near-black `#1F2D3D` for walls and numbers, warm off-white `#F9FAFC` ground,
`#338EDA` blue for sensor cones and the planned route, `#EC3750` red for the mouse
and the current cell, `#FF8C37` orange used once, on arrival at the goal. Flat,
bold, no gradients or glow.

### Captions

One short line, lower third, changing with the phase: "It assumes every unseen
wall is open", "Blocked. Re-plan", "Dead end", "Reached the centre", "Now drive
back". Irish and British English. Never use em dashes.

### Deliverable

Looping animation, 16:9, and expose the maze seed and step duration as parameters
so the run can be re-rolled if a particular maze produces a boring search.
