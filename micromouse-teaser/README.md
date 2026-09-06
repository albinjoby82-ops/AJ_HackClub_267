# Micro-Mouse '26 — launch teaser

Vertical launch teaser for the UCD ElecSoc Micro-Mouse '26 competition, cut from
the supplied micromouse/maze animation and finished with original motion
graphics and an original score.

Final delivery: `output/micromouse-teaser-final.mp4` — 1080×1920, 30 fps,
19.37 s, H.264 High / AAC, fast-start. See
[`output/render-report.md`](output/render-report.md) for the full report.

## Build

```bash
npm install
npm run build:all
```

On a machine where the system temp drive is low on space, point `TEMP`/`TMP`
somewhere with room first — Chrome will refuse to fetch the video asset
otherwise.

Individual steps:

| Script | Does |
| --- | --- |
| `npm run prepare-media` | Finds the sources by content, upscales the primary to 1080×1920 (Lanczos), copies logo + font |
| `npm run audio` | Synthesises and loudness-normalises `public/score.wav` |
| `npm run render:preview` | 540×960 review copy |
| `npm run render:final` | 1080×1920 delivery |
| `npm run validate` | ffprobe + loudness + motionless-hold checks, writes the contact sheet |
| `npm run studio` | Remotion Studio, for scrubbing the timeline |

## Architecture

**`src/timeline.mjs` is the single source of truth.** Segment durations, source
in-points, crops, colours, copy, end-card beats and the audio cue sheet all live
there, and both the Remotion components and the Node tools import from it.
Cumulative start frames are derived, never hand-written — change a duration and
everything downstream follows.

```
src/
  timeline.mjs              config: timings, palette, copy, cue sheet
  Teaser.tsx                assembles the timeline into sequences
  fonts.ts                  embedded Bahnschrift (variable, wdth axis)
  components/
    PrimaryFootage.tsx      one cut of the source, with crop/push-in
    TeaserText.tsx          "THE MAZE IS WAITING."
    ImpactTitle.tsx         SMALLER. / FASTER. / SMARTER.
    MazeOverlay.tsx         cold-open pulse, sensor sweep, circuit lattice
    ElecSocEndCard.tsx      rebuilt end card + match-cut ring
    AudioBed.tsx            the score
tools/
  prepare-media.mjs         inventory, upscale, asset copy
  generate-audio.mjs        procedural score + loudness normalisation
  finalise.mjs              delivery mux (video copy, single AAC encode)
  validate.mjs              acceptance checks + contact sheet
```

## The Dublin cut

A second, separate composition — `DublinTeaser`, 1080×1920, 30 fps, 500 frames
(16.667 s) — for the Dublin Micromouse Open '26. It shares nothing with the
`Teaser` timeline above: two poster spotlight-reveals bracketing two sharp-turn
shots, over a supplied soundtrack.

```bash
npm run dublin:all
```

| Script | Does |
| --- | --- |
| `npm run dublin:prepare` | Stages the posters into `public/dublin` and cuts the turn clips 1:1 |
| `npm run dublin:retime` | Re-cuts the turn clips with the shipping retime — run after prepare, it overwrites them |
| `npm run dublin:render` | Renders `DublinTeaser` and muxes the supplied soundtrack (stream copy, never re-encoded) |
| `npm run dublin:validate` | Container/codec/frame-count acceptance checks |

**Supplied media is not in the repo.** `dublin-src/` and the `public/dublin/`
clips cut from it are gitignored, same as `public/primary-1080.mp4`. To build
you need:

```
dublin-src/
  source/current_mouse_animation.mp4     1080×1920 @ 30 fps — the ramp and
                                         frame maths assume exactly this
  audio/reference_music_trimmed.m4a      AAC-LC 44.1 kHz, already the exact
                                         production audio
  posters/01_something_is_learning_the_maze.png
  posters/02_micromouse_open_2026.png    2160×3840, downsampled by the renderer
```

`src/dublin/timeline.ts` is the source of truth: cut points, beat frames, the
two spotlight tracks and the poster geometry they were measured against.

## Two things worth knowing before editing

**The source animation has typography burned into it.** `SMALLER.` / `FASTER.` /
`SMARTER.` are rendered into the picture at 1.72–2.55 s, 3.85–4.75 s and
6.25–7.15 s, and there is a low-resolution end card from 15.4 s. The edit cuts
around all of it so those words can be re-set as live text. If you move a source
in-point, check it against those ranges.

**Crops are centre-based, not origin-based.** `PrimaryFootage` places the
`focus` point at the centre of the visible crop using `scale()` + `translate()`.
Using `transform-origin` instead pins the focus point in place, which shifts the
crop — that is what let the baked-in `SMALLER.` back into frame during an early
build.

Renders are deterministic: the score uses a seeded PRNG and the composition has
no wall-clock animation or unseeded randomness.

## CV tease (`CvTease`)

A third cut in the same campaign: 1080x1920, 30 fps, exactly 450 frames
(15.000 s). Unlike the other two it uses no source footage at all — every frame
is drawn, so it renders from a clean checkout with nothing but the fonts and the
ElecSoc logo.

```
npm run cv:all      # prepare assets -> score -> render -> validate
```

`src/cv/timeline.mjs` is the source of truth: scene boundaries, beat frames,
layout geometry, the route polyline and the exact copy. Two things derive from
it automatically and must not be hand-maintained:

- **Turn frames.** The route is drawn at constant speed, so `TURN_FRAMES` is
  just each vertex's distance fraction across the draw. The servo clicks in the
  score and the five skill labels both read that array, which is what keeps the
  clicks landing exactly on the 90-degree turns.
- **The audio cue sheet.** `AUDIO.cues` is expressed in seconds derived from the
  same frame numbers the picture uses.

**The logo backdrop is keyed, not redrawn.** `tools/prepare-cv.mjs` keys the
supplied file's flat rgb(0,39,50) backdrop to transparency so the mark sits on
near-black the way it does on the posters. The mark's own pixels are untouched,
and the unmodified file stays in `public/elecsoc-logo.png`.

**Absolutely positioned children need an explicit parent width.** The skill
column collapses to zero width otherwise, and every label wraps at each space.

`tools/validate-cv.mjs` checks the copy against an independent transcription of
the brief, rejects the forbidden event-name variants, measures the vertical safe
bands on the encoded pixels and confirms the final card is motionless.
