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
