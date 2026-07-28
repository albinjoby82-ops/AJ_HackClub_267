# Micro-Mouse '26 — Reveal Trailer

Vertical launch trailer for UCD ElecSoc's Micro-Mouse '26.
**1080×1920 · 30fps · 45.00s · H.264 MP4**

Built from the brief in [`docs/`](docs/) (the supplied prompt package, kept
verbatim for reference).

## Running it

```bash
npm install
npm run dev
```

Open http://localhost:5183. The scrubber at the bottom steps through the whole
film; `?render=1` hides the UI and pins the stage at exact pixel size.

## Rendering the MP4

```bash
npm run render
```

The render command first regenerates the deterministic original soundtrack,
builds the app, captures frames straight into ffmpeg without writing PNGs, and
muxes AAC audio into `out/micromouse-26-reveal.mp4`. No dev server or system
ffmpeg install is needed.

## Reviewing

```bash
node tools/contact-sheet.mjs 24              # whole film, 24 frames
node tools/contact-sheet.mjs 12 27 38 4 340  # count, from, to, cols, thumbWidth
```

Writes `out/contact/index.html`.

## Structure

| Time | Scene | Module |
|---|---|---|
| 0:00–0:03 | Power on | `src/scenes/scene01PowerOn.js` |
| 0:03–0:09 | Robotics + MakerLabs | `src/scenes/scene02Robotics.js` |
| 0:09–0:16 | Makerthon | `src/scenes/scene03Makerthon.js` |
| 0:16–0:24 | RoboExpo | `src/scenes/scene04RoboExpo.js` |
| 0:24–0:27 | The pivot | `src/scenes/scene05Pivot.js` |
| 0:27–0:38 | Micromouse maze run | `src/scenes/scene06MazeRun.js` |
| 0:38–0:41.2 | Logo reveal (pre-rendered) | `src/scenes/scene07LogoVideo.js` |
| 0:41.2–0:45 | Event title | `src/scenes/scene08Title.js` |

All timings live in [`src/timing.js`](src/timing.js) — change pacing there, not
in the scene modules.

### How it stays deterministic

Nothing animates on its own. The GSAP master timeline is created paused, and
`window.__reveal.seek(t)` is the only way time moves — the preview transport
drives it from `requestAnimationFrame`, and the capture tool drives it one
frame at a time. The Three.js scene renders on demand inside that seek, the
maze uses a seeded PRNG, and the film grain is generated from a fixed seed.
Two runs produce identical frames.

## The logo reveal video

`public/video/logo-reveal.mp4` is the pre-rendered payoff, played rather than
rebuilt. Two things about the delivered file shape the edit:

- **It is 1280×720 landscape**, so it occupies a centre band of the 9:16 frame.
  `#video-backdrop` fills the surround and turns white in step with the video's
  own white wipe. A portrait re-render dropped at the same path is detected
  automatically and skips the surround; `LOGO_VIDEO.native` remains available
  as an explicit override.
- **Its first ~4.6s is its own maze sequence**, which would duplicate scene 6.
  Only the payoff is used — see `LOGO_VIDEO.in` / `.out` in `src/timing.js`.

The video already carries the ElecSoc logo lockup and `MICROMOUSE '26`, so
scene 8 holds that final frame and adds only the tagline, the event block and
COMING SOON on top of it.

## Soundtrack

`npm run audio` creates `public/audio/score.wav` from fixed synthesis and
seeded noise. It is an original 130 BPM score with relay/circuit details,
recap impacts, a near-silent 0:24 pivot, motor spool, maze drive and logo
stinger. Repeated generation is byte-identical.

## Outstanding

- **Event details are placeholders.** `[DATE]`, `[TIME]`, `[VENUE]` and
  `[SIGN-UP URL]` in
  `src/scenes/scene08Title.js`. Nothing is invented.
- **Fonts are system fallbacks** (Bahnschrift → Arial Narrow). Self-host a
  condensed face before final delivery or the render will differ off this
  machine.
