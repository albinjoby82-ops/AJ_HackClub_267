# LOCKED MAZE-SEQUENCE REPLACEMENT PROMPT

Use this prompt only when the rest of the animation is strong but the maze sequence needs replacement.

Replace **only the Micro-Mouse maze sequence and the transition into the ElecSoc logo**. Keep every other scene, image, timing choice, text style and audio cue pixel-identical.

The replacement sequence must run from approximately 0:27 to 0:42.

## Non-negotiable maze geometry

- Build a real connected maze from solid 3D wall meshes.
- Walls must be thick, filled and opaque, never line drawings or hollow outlines.
- Every corridor must visibly have a wall on both sides except at a genuine junction or opening.
- Wall height must be roughly 1.5-2 times the mouse height.
- Corridor width should be approximately 1.6-1.9 times the mouse body width.
- Add 90-degree bends, T-junctions, at least one dead-end visible in passing and one route-choice moment.
- Use collision-aware camera placement.
- No wall may intersect the micromouse.
- No wall may cover more than roughly 20% of the mouse silhouette in the chase shot.
- The camera may not pass through geometry.
- The mouse must follow the corridor centre with believable corrections.

## Micromouse behaviour

- Compact square differential-drive robot.
- Two powered wheels and a low body.
- Front and diagonal IR sensors visibly scan the walls.
- Accelerates on straights.
- Brakes immediately before a 90-degree turn.
- Rotates quickly around its wheel axis.
- Allows only a tiny controlled rear slip at the fastest turn.
- Re-centres in the new corridor.
- Do not animate it like a car.
- Do not use long drifting.
- Do not let it float or bank.

## Cinematic camera

Opening shot:
- 20-30 cm behind the mouse
- 8-12 cm above chassis
- 18-22 mm lens
- slight offset from centre
- walls are clearly visible on both sides

Turn behaviour:
- camera eases slightly wider before a turn
- 3-5 degree camera roll
- short speed ramp
- camera follows the rotation without cutting through the inside wall

Additional shots:
- one wheel-level side shot through a genuine opening
- one 0.5-second top-down junction shot
- return immediately to the chase camera

## Appearance

- Matte dark-teal walls
- slightly textured floor
- mint sensor rays
- orange-red route glow
- soft overhead pools of light
- realistic contact shadows
- restrained motion blur
- no fog thick enough to hide geometry
- no random neon city environment

## Logo reveal

The route trace must be planned from the beginning so it aligns with the supplied ElecSoc logo.

At the final corridor:
1. Mouse crosses the final node.
2. Camera cranes vertically upward without a cut.
3. Maze walls simplify and fade in controlled stages.
4. Route trace remains.
5. Route trace aligns exactly to the circuit paths and orange nodes of `assets/logos/elesoc_logo.png`.
6. The supplied logo crossfades in as the alignment reference.
7. A pulse travels through it.
8. Hold for the title impact.

Do not approximate or redesign the logo. The final frame must use the actual supplied logo asset.
