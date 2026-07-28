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

That runs `capture` (Playwright walks the timeline one frame at a time into
`out/frames/`) then `export` (ffmpeg encodes `out/micromouse-26-reveal.mp4`).
The dev server must already be running. ffmpeg comes from `ffmpeg-static`, so
no system install is needed.

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
  own white wipe. When a 1080×1920 re-render is dropped in at the same path,
  set `LOGO_VIDEO.native = true` in `src/timing.js` and the surround is skipped.
- **Its first ~4.6s is its own maze sequence**, which would duplicate scene 6.
  Only the payoff is used — see `LOGO_VIDEO.in` / `.out` in `src/timing.js`.

The video already carries the ElecSoc logo lockup and `MICROMOUSE '26`, so
scene 8 holds that final frame and adds only the tagline, the event block and
COMING SOON on top of it.

## Outstanding

- **No audio.** The brief specifies a layered score with a tension break at
  0:24 and a motor spool after 0:27; no audio asset was supplied and none is
  generated. The cut is built to work muted.
- **Event details are placeholders.** `[DATE]`, `[TIME]`, `[VENUE]` in
  `src/scenes/scene08Title.js`. Nothing is invented.
- **Fonts are system fallbacks** (Bahnschrift → Arial Narrow). Self-host a
  condensed face before final delivery or the render will differ off this
  machine.
