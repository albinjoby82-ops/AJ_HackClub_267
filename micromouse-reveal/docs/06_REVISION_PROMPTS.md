# TARGETED REVISION PROMPTS

## A. The recap still feels like a slideshow

Keep the selected images and the entire timeline, but replace the recap transitions from 0:03-0:24.

Add genuine motion design:
- split foreground and background for 2.5D depth
- animate camera parallax
- use PCB-path masks
- match-cut circular objects, wheels and faces
- allow only 0.25-0.8 seconds per image
- make typography drive the cuts
- use speed ramps and hard impact cuts

Do not add new assets. Do not change the maze or final reveal.

## B. The maze walls are covering the mouse

Replace only the chase-camera rig and collision logic.

Requirements:
- camera stays centred in the corridor
- camera target remains the mouse chassis centre
- dynamically reduce camera offset near turns
- use raycasts from camera to mouse and from camera to nearby walls
- if a wall obstructs the mouse, move the camera inward and upward rather than clipping the wall
- mouse must retain at least 80% visible silhouette
- no wall-camera intersection
- do not make walls transparent as a workaround

## C. The turn is not cinematic enough

Keep maze geometry unchanged.

For the fastest 90-degree turn:
1. Ease camera 10% wider over 8 frames.
2. Mouse brakes hard.
3. Front sensor rays sweep the corner.
4. Differential wheels counter-rotate briefly.
5. Mouse snaps through the turn.
6. Add a tiny 2-4 cm equivalent rear slip.
7. Roll camera 4 degrees toward the outside of the turn.
8. Add a 6-frame speed ramp and restrained wheel scrub.
9. Re-centre immediately.

Do not turn the mouse into a drifting car.

## D. The logo reveal is unclear

Keep the maze run unchanged until the final turn.

Rebuild only the crane-up:
- extend the upward move by 0.8 seconds
- reduce maze-wall opacity in three staged bands
- keep the orange route fully visible
- align route against the actual supplied ElecSoc logo matte
- show the logo faintly at 20% opacity during alignment
- once aligned, pulse the two orange nodes
- then fade the maze completely
- hold the clean supplied logo for 0.5 seconds before the event title

## E. The animation is too busy

Do not slow the overall pace.

Reduce:
- glitch frequency by 60%
- simultaneous image count to a maximum of 3
- decorative particles by 80%
- camera shake by 50%
- colour accents to mint, orange and white

Increase:
- blank space around statistics
- readability time for the final title
- contrast between the loud recap and silent pivot

## F. The final reveal needs more hype

Keep title wording unchanged.

Add:
- 3-frame pre-impact blackout
- one sub-bass impact
- rapid logo pulse
- title scale from 132% to 100% over 8 frames
- a fine burst of circuit fragments that dissipates in under 0.5 seconds
- tagline 4 frames after title
- final hold of at least 2.2 seconds

Do not add flames, explosions or generic esports effects.
