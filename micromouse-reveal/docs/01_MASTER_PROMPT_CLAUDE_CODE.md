# MASTER COPY-PASTE PROMPT FOR CLAUDE CODE

You are a senior cinematic motion designer, creative director and Three.js engineer.

Build a polished, deterministic **42-48 second vertical reveal trailer** for **UCD ElecSoc's Micro-Mouse '26 event** using the supplied image and logo assets.

This is not a generic event recap, a slideshow, a corporate presentation or a template. It must feel like a high-energy launch trailer made specifically for students who build real things.

## Core narrative

ElecSoc spent the previous year building momentum through Robotics Club, MakerLabs, its first Makerthon and RoboExpo. The first half of the trailer should show that history as fast, tactile fragments of real people building, soldering, coding, testing and presenting.

At the midpoint, everything stops.

The trailer asks:

**WHAT'S NEXT?**

A micromouse powers on and launches through a real physical maze. The past year's energy has become the next challenge. The camera follows the mouse through sharp, fast, physically plausible turns. The camera then rises above the maze and reveals that the route has completed the circuit paths of the ElecSoc logo.

The final title lands:

**MICRO-MOUSE '26**

Tagline:

**BUILD IT. CODE IT. RACE IT.**

Secondary creative line:

**LAST YEAR, WE MADE CHAOS. THIS YEAR, WE MAKE SPEED.**

## Visual identity

Use the supplied ElecSoc logo without redrawing or modifying its geometry.

Base palette:
- Near-black and deep ElecSoc teal backgrounds
- White typography
- Mint/cyan circuit accents
- ElecSoc orange-red as the impact accent
- Very limited magenta or lime only when inherited from the supplied Makerthon material

Tone:
- Cinematic
- Energetic
- Tactile
- Young and slightly chaotic
- Technically credible
- Confident, not corporate
- Clean enough to feel premium

Do not use generic blue sci-fi HUD graphics. Do not make it look like an esports template.

## Exact timeline

### SCENE 1 - POWER ON / 0:00-0:03

Black screen.

A faint electrical hum begins. One relay click. Thin circuit traces illuminate one at a time in mint. The supplied ElecSoc logo is only partially visible, as if the system is booting.

Use close macro details:
- PCB trace
- solder joint
- servo horn
- wheel encoder
- filament texture

Text appears one word per impact:

**WE BUILT.**

Camera language: macro 35 mm, shallow depth of field, subtle handheld energy.

### SCENE 2 - ROBOTICS + MAKERLABS / 0:03-0:09

Build a rapid montage from:
- `assets/robotics/robotics_build_closeup.png`
- `assets/robotics/robotics_hands_on.png`
- `assets/robotics/robotics_workspace.png`
- `assets/makerlabs/makerlabs_group.jpeg`
- `assets/makerlabs/soldering_workshop_01.png`
- `assets/makerlabs/soldering_workshop_02.png`
- `assets/makerlabs/print_farm.png`

Use real image layers with 2.5D parallax, fast push-ins, snap zooms and circuit-shaped masks.

Text beats:

**WE WIRED.**  
**WE CODED.**  
**WE MADE IT MOVE.**

No image should remain static. Use restrained camera motion, depth separation and motion blur. Never stretch or crop faces awkwardly.

### SCENE 3 - MAKERTHON / 0:09-0:16

The beat drops.

Use:
- `assets/makerthon/makerthon_crowd_wide.jpeg`
- `assets/makerthon/makerthon_room.jpeg`
- `assets/makerthon/makerthon_team_working.jpeg`
- `assets/makerthon/makerthon_prizes_table.jpeg`
- `assets/makerthon/makerthon_winners.jpeg`
- `assets/designed_cards/makerthon_hero.png`
- `assets/designed_cards/makerthon_stats.png`

Treat the full designed cards as quick memory flashes, not long static posters.

Kinetic statistics hit in sequence:

**85+ SIGN-UPS**  
**€250 IN PRIZES**  
**100% CHAOS**

Use a fast three-beat typography sequence. On the word **CHAOS**, briefly allow cards and photographs to collide, rotate and settle, but keep all text readable.

### SCENE 4 - ROBOEXPO / 0:16-0:24

Use:
- `assets/roboexpo/roboexpo_hero_crowd.jpeg`
- `assets/roboexpo/roboexpo_crowd_wide.png`
- `assets/roboexpo/roboexpo_officers_group.png`
- `assets/roboexpo/roboexpo_robot_track.png`
- `assets/roboexpo/roboexpo_analogue_drum_demo.png`
- `assets/roboexpo/roboexpo_sand_machine_demo.jpeg`
- `assets/roboexpo/roboexpo_jarvis_demo.jpeg`
- `assets/designed_cards/roboexpo_hero.png`
- `assets/designed_cards/roboexpo_stats.png`
- `assets/designed_cards/roboexpo_year_of_work.png`

Kinetic statistics:

**180+ ATTENDEES**  
**20+ PROJECTS**  
**A YEAR OF WORK. ONE ROOM.**

Now present the four featured projects as hero objects in rapid succession:
- `assets/robotics/robot_spider.png`
- `assets/robotics/analogue_drum_machine.png`
- `assets/robotics/sand_machine_cad_01.png`
- `assets/robotics/desktop_jarvis.png`

Each object receives approximately 0.65 seconds:
1. It enters with a precise mechanical movement.
2. A clean label flashes.
3. It is displaced by the next object on a bass hit.

Labels:
- ROBOT SPIDER
- ANALOGUE DRUM
- SAND MACHINE
- DESKTOP JARVIS

Do not invent new robots. Do not alter the supplied project images.

### SCENE 5 - THE PIVOT / 0:24-0:27

Hard cut to black.

All music stops except a low electrical room tone.

The words appear slowly:

**SO... WHAT'S NEXT?**

A pair of infrared sensor beams flicker on in darkness.

A compact micromouse wheel makes one tiny corrective movement.

Then a motor spool-up begins.

### SCENE 6 - MICROMOUSE MAZE RUN / 0:27-0:38

This is the hero sequence.

Create a credible two-wheel differential-drive micromouse:
- Compact square chassis
- Two driven wheels
- Small caster or skid support
- Visible front/diagonal infrared sensors
- Low centre of gravity
- ElecSoc mint and orange accents
- No sports-car body
- No oversized decorative parts

Maze requirements:
- It must be an actual connected maze with corridors, junctions, dead ends and 90-degree turns.
- Walls must be solid, thick and filled-in 3D geometry.
- Two walls must visibly define the corridor around the mouse.
- Walls should be approximately 1.5-2 times the mouse height.
- The corridor must be wide enough for the mouse and camera.
- Walls must never intersect, cover or clip through the mouse.
- The camera must never travel through walls.
- Openings must appear only where the maze genuinely branches.
- The mouse must react to the geometry rather than following an arbitrary animation curve.

Camera:
- Start 20-30 cm behind the mouse and slightly above chassis height.
- Use an 18-22 mm virtual lens.
- Camera stays close enough for speed but far enough to read the walls.
- On sharp turns, use a brief 3-5 degree camera roll and a controlled speed ramp.
- The mouse may show a tiny, physically plausible tyre slip during the fastest 90-degree turn.
- Do not make it drift like a sports car.
- Alternate between chase view, wheel-level side pass and one very brief overhead junction shot.
- Use subtle motion blur and wheel vibration.
- Keep the mouse visible throughout.

Integrate the previous year without interrupting the run:
- A few wall surfaces briefly illuminate with faint monochrome photographic memories from Makerthon and RoboExpo.
- These are reflections or projected fragments, not floating rectangles blocking the corridor.
- Keep them secondary to the maze.

Text appears as environmental typography for less than one second each:

**SMALLER.**  
**FASTER.**  
**SMARTER.**

### SCENE 7 - LOGO REVEAL / 0:38-0:42

The mouse exits the final turn.

The camera rapidly cranes upward into a clean top-down view.

The glowing route left by the mouse completes the circuit lines and orange nodes of the supplied ElecSoc logo.

The maze walls visually simplify into the logo's circuit geometry. Do not distort the actual logo. Use the supplied logo as the final alignment reference.

A clean electrical pulse travels through the completed logo.

One frame of silence.

Then the logo locks into place.

### SCENE 8 - EVENT TITLE / 0:42-0:47

The ElecSoc logo scales back slightly.

Title impacts forward:

**MICRO-MOUSE '26**

Tagline underneath:

**BUILD IT. CODE IT. RACE IT.**

Then:

**COMING SOON**

Reserve a clean region for future date, venue and sign-up details. Use explicit placeholders in code:
- `[DATE]`
- `[TIME]`
- `[VENUE]`
- `[SIGN-UP URL]`

Do not invent event information.

## Typography

Use one condensed, strong sans-serif for impact text and one clean sans-serif for supporting information.

Typography must be:
- Large
- High contrast
- Legible on a phone
- Kept within vertical-video safe zones
- Animated with scale, tracking and mask reveals rather than excessive spinning

Do not imitate the exact typography of unrelated brands.

## Editing language

Use:
- Speed ramps
- Match cuts based on circles, wheels and circuit nodes
- Mechanical wipes
- PCB trace masks
- Short shutter-like cuts
- Controlled glitch only at transitions
- Parallax on raw photographs
- Dynamic but readable kinetic type
- A strong silence before the maze run
- A clear final title hold of at least 2.2 seconds

Avoid:
- Slow slideshow dissolves
- Random stock footage
- AI-generated faces
- Warped photographs
- Excessive lens flares
- Endless camera shake
- Transparent wireframe maze walls
- Generic neon-blue HUD graphics
- Cheesy 3D text spins
- Walls clipping through the mouse
- Long explanatory paragraphs on screen

## Sound design

Create a layered original or royalty-free electronic score with:
- Relay click
- Servo chirps
- Soldering/electrical textures
- Keyboard and tool hits used rhythmically
- Crowd energy under Makerthon and RoboExpo
- Bass impacts for statistics
- Complete near-silence before the maze
- Motor spool, wheel scrub and sensor ticks during the run
- Rising electrical tone during the top-down reveal
- Heavy but clean logo impact
- Short circuit-complete stinger

The video must still work with audio muted.

## Implementation requirements

Build the animation as a deterministic web timeline suitable for frame-perfect recording.

Preferred architecture:
- Vite
- Three.js for the maze, micromouse and 3D camera
- GSAP timeline for all timing
- HTML/CSS overlays for typography
- Asset preload screen
- A debug timeline scrubber that can be disabled for export
- A `?render=1` mode that:
  - fixes resolution to 1080 x 1920
  - disables UI
  - removes non-deterministic timing
  - begins only after all assets are loaded
- Playwright or Puppeteer frame capture
- FFmpeg export to H.264 MP4 at 30 fps

Organise code by scene:
- `scene01PowerOn`
- `scene02Robotics`
- `scene03Makerthon`
- `scene04RoboExpo`
- `scene05Pivot`
- `scene06MazeRun`
- `scene07LogoReveal`
- `scene08Title`

Create a central timing configuration so durations can be adjusted without rewriting scene logic.

Use supplied assets only for historical imagery. Do not fetch external images.

## Quality gates before calling the work complete

1. The recap section feels kinetic rather than like a slideshow.
2. Makerthon's 85+ sign-ups, €250 prizes and 100% chaos are readable.
3. RoboExpo's 180+ attendees and 20+ projects are readable.
4. All four featured robotics projects appear clearly.
5. The transition to the maze is a dramatic tonal reset.
6. The maze has solid, thick walls on both sides of the mouse.
7. The mouse is never hidden by or clipped into a wall.
8. The maze contains real turns and branches.
9. The chase camera feels cinematic but physically possible.
10. The route resolves cleanly into the ElecSoc logo.
11. The final title remains readable for at least 2.2 seconds.
12. No date, venue or sign-up details are invented.
13. No supplied faces or logos are distorted.
14. The entire animation is coherent at 1080 x 1920.
15. The final MP4 plays correctly in Instagram's vertical format.

Start by creating the full scene structure and timing with assets in their correct locations. Then implement the maze. Then polish transitions and sound. Do not spend time on minor visual effects before the complete narrative works end to end.
