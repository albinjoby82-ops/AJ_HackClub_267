# Handoff — Micro-Mouse '26 reveal trailer

Everything below is current as of commit `83acb6a` on branch
`micromouse-26-reveal` (pushed to `origin`).

---

## 1. What this is

A **45.00s vertical launch trailer** (1080×1920, 30fps, H.264) for UCD
ElecSoc's Micro-Mouse '26, built to the brief in [`docs/`](docs/) — the
supplied prompt package, kept verbatim so you can check work against it.

A rendered MP4 exists at `micromouse-reveal/out/micromouse-26-reveal.mp4`
(18.6 MB, gitignored — re-render with `npm run render`).

## 2. Where it lives

| | |
|---|---|
| Repo | `albinjoby82-ops/AJ_HackClub_267` |
| Branch | `micromouse-26-reveal` (off `origin/master`) |
| Checkout | `D:\dev\micromouse-26-reveal` — a **git worktree**, not a clone |
| Project dir | `D:\dev\micromouse-26-reveal\micromouse-reveal` |
| Main repo | `C:\Users\ASUS\My Drive\Hack Club` |

**The checkout is deliberately on D:.** C: is a 200GB system drive sitting at
~99% full, and it is also inside Google Drive, whose sync client holds file
handles that make `node_modules` operations fail. Playwright's browser cache is
pinned to `D:\dev\ms-playwright` via `tools/paths.mjs`. **Do not move this back
to C:** — renders will fail with `ENOSPC`.

Because it is a worktree, `git worktree list` from the main repo must show
`D:/dev/micromouse-26-reveal`. If that registration breaks, repair it with
`git worktree repair D:/dev/micromouse-26-reveal` — do **not** use
`git worktree move`, which cannot cross drives.

## 3. Getting running

```bash
cd D:/dev/micromouse-26-reveal/micromouse-reveal
npm install
npm run dev        # http://localhost:5183 — scrubber at the bottom plays it
```

```bash
npm run render     # vite build + render straight to out/micromouse-26-reveal.mp4 (~18 min)
```

Review a stretch of the film as a contact sheet:

```bash
node tools/contact-sheet.mjs 12 27 38 4 340
```

Arguments are `count from to cols thumbWidth`; writes `out/contact/index.html`.
This is the fastest way to judge pacing and framing — use it before and after
any timing change.

## 4. Architecture, and the one rule that matters

**Nothing animates on its own.** The GSAP master timeline is created paused and
`window.__reveal.seek(t)` is the only thing that moves time. The preview
transport drives it from `requestAnimationFrame`; the render tool drives it one
frame at a time. The Three.js scene renders on demand *inside* that seek, the
maze uses a seeded PRNG (`src/maze/maze.js`), and the film grain is generated
from a fixed seed (`grainDataUri` in `src/dom.js`).

Consequence: **two runs produce identical frames, and any frame can be rendered
without rendering the ones before it.** If you add anything driven by
`Date.now()`, `Math.random()`, or its own rAF loop, you break the render. Don't.

### Layout

```
src/
  timing.js          all scene start/duration — change pacing HERE, not in scenes
  assets.js          asset manifest + preload list
  dom.js             DOM builders (photo, impactWord, statBlock, …)
  style.css
  main.js            preload, builds scenes, master timeline, seek(), capture API
  maze/
    maze.js          seeded DFS maze + authored route, wall geometry
    path.js          arc-length parameterised path with rounded corners
    mouse.js         the micromouse model
  scenes/scene01…08  one module per scene
tools/
  paths.mjs          output + Playwright browser locations (import before playwright)
  static-server.mjs  in-process static server used by the renderer
  render.mjs         THE render pipeline
  contact-sheet.mjs  review aid
  capture.mjs        legacy frames-to-disk capture (see §7)
  export.mjs         legacy frames-to-MP4 encode (see §7)
```

Every scene module exports `build({ root, tl, t0, dur, … })`, creates its own
DOM inside its `.scene` element, and adds tweens to the shared timeline at
**absolute** positions (`t0 + offset`). Scenes 6 and 7 also return an object —
`{ update }` for the maze (called during seek) and `{ syncVideo }` for the video
(awaited during seek).

### Timeline

| Time | Scene | Module |
|---|---|---|
| 0:00–0:03 | Power on | `scene01PowerOn.js` |
| 0:03–0:09 | Robotics + MakerLabs | `scene02Robotics.js` |
| 0:09–0:16 | Makerthon | `scene03Makerthon.js` |
| 0:16–0:24 | RoboExpo | `scene04RoboExpo.js` |
| 0:24–0:27 | The pivot | `scene05Pivot.js` |
| 0:27–0:38 | Micromouse maze run | `scene06MazeRun.js` |
| 0:38–0:41.2 | Logo reveal (pre-rendered) | `scene07LogoVideo.js` |
| 0:41.2–0:45 | Event title | `scene08Title.js` |

## 5. The logo reveal video — read before touching the ending

`public/video/logo-reveal.mp4` was supplied finished and is **played, not
rebuilt**. Two properties of the delivered file shape the whole ending:

1. **It is 1280×720 landscape**, not 1080×1920. In a 9:16 frame it fills only a
   centre band (~32% of the height). `#video-backdrop` fills the surround and
   animates to white in step with the video's own white wipe, so the letterbox
   is invisible on the final card.
2. **Its first ~4.6s is its own maze/circuit sequence**, which would duplicate
   scene 6. Only the payoff (4.6s→7.8s) is used.

Both are controlled by `LOGO_VIDEO` in `src/timing.js`.

It already contains the ElecSoc logo lockup **and** `MICROMOUSE '26`, so scene 8
does not recreate them — it holds the video's final frame and lands only the
tagline, event block and COMING SOON on top.

**The user is producing a 1080×1920 re-render.** When it arrives: drop it at the
same path, set `LOGO_VIDEO.native = true`, re-check `in`/`out` against the new
file's timing, and re-render. `native: true` skips the letterbox surround. Scene
8's text sits in the lower third, which should still work, but check it against
whatever the vertical version puts there.

## 6. Non-obvious things that will bite you

These were all found by looking at rendered frames. They are fixed — this is so
you don't undo them.

- **Everything the timeline animates starts at `opacity: 0` in CSS**
  (`.photo, .object-shot, .stat, .impact, …`). GSAP only applies a tween once
  the playhead reaches it, so anything defaulting to `opacity: 1` is on screen
  from the moment its scene appears — every shot in a scene stacked at once.
  Add a new animated element? Give it `opacity: 0`.
- **The chase camera aims along the camera→mouse ray**, not down the corridor
  tangent (`updateCamera` in `scene06MazeRun.js`). A portrait frame has only
  ~43° of horizontal view, so aiming even 15° off puts the mouse at the edge.
  With tangent-based aiming the mouse left the frame entirely at every corner
  (measured `|ndc.x|` up to 1.38; it is now ≤0.13). `__reveal.debug().ndc`
  reports this — re-check it after any camera change.
- **Scene cuts are `tl.set`, not a 1-frame `tl.to`.** A fade starting *at* the
  cut leaves the scene's opening frame black.
- **Designed cards must never overlap the kinetic stats.** The cards have their
  own baked-in "85+ / €250 / 100%" text; overlapping produces doubled
  unreadable type. `CARD_FLASHES` timings sit in the gaps between `STATS`
  deliberately. `roboexpo_year_of_work.png` is unused for this reason.
- **`.object-shot img` uses `width`/`height`, not `max-*`.** The supplied
  cut-outs are smaller than the frame and `max-*` only ever shrinks — the hero
  objects rendered at about a quarter size.
- **Camera lag tightens through corners** (`lag = 1.15 - 0.45 * turn`) and the
  mouse starts `START_OFFSET` into the path so the camera has corridor behind
  it rather than sitting inside the mouse.
- **`tools/paths.mjs` must be imported before `playwright`** — it sets
  `PLAYWRIGHT_BROWSERS_PATH`, which is read at first import. `render.mjs` uses
  `await import('playwright')` for exactly this reason.

## 7. Why rendering works the way it does

`npm run render` builds to `dist/`, serves it from an **in-process** HTTP server
(`tools/static-server.mjs`), and pipes screenshots straight into **ffmpeg's
stdin**. No frames touch the disk.

This is not incidental complexity — the two obvious approaches both failed:

- **Rendering against the Vite dev server** killed three separate runs
  (`ERR_CONNECTION_REFUSED` at frames 515, 250, …). The dev server died
  mid-render and took the run with it.
- **Writing frames to disk first** needs ~1.8GB of scratch for 1350 lossless
  1080×1920 PNGs. C: had under 1GB free and the run died with `ENOSPC`.

The static server supports **Range requests** because Chromium fetches the
reveal `.mp4` with them; without Range the video never loads and the tail
renders blank.

`tools/capture.mjs` + `tools/export.mjs` are the older frames-on-disk path,
kept for when you want individual frames (e.g. to inspect one, or to re-encode
without re-rendering). `capture.mjs` is resumable — it skips frames already
present. Only use it if you have the disk space.

**When running these from a shell, don't pipe through `tail`.** A pipeline
reports the *last* command's exit status, so `node tools/render.mjs | tail`
reports success on every crash. Redirect to a log and check `$?` instead.

## 8. Open work, highest value first

1. **Swap in the vertical logo reveal** (§5). Biggest single visual improvement
   remaining — the ending is currently a letterboxed band.
2. **Audio.** The brief (`docs/05_TEXT_AUDIO_AND_STYLE.md`) specifies a 125–140
   BPM electronic score with a tension break at 0:24 and a motor spool after
   0:27. No asset was supplied and none was invented. The cut is built to read
   muted. Adding audio means an `<audio>` element seeked alongside the timeline
   in `seek()`, plus `-i track.wav -c:a aac -shortest` in `render.mjs`.
3. **Event details.** `[DATE]`, `[TIME]`, `[VENUE]` in `scene08Title.js`.
   Do not invent these — `docs/07_EVENT_DETAILS_PLACEHOLDERS.md` is explicit.
4. **Self-host a condensed font.** Currently falls back through
   `Bahnschrift → Oswald → Arial Narrow` (`--font-impact` in `style.css`).
   Bahnschrift ships with Windows, so a render on another machine will differ.
5. **Wall memories are subtle.** The brief asks for monochrome photographic
   fragments on the maze walls; they are implemented (`memorySpecs` in
   `scene06MazeRun.js`) but barely read at current opacity.

## 9. Verification checklist

Before calling any change done, confirm against
`docs/01_MASTER_PROMPT_CLAUDE_CODE.md` §"Quality gates". The mechanical ones:

```bash
npm run build                                   # must exit 0
node tools/contact-sheet.mjs 24                 # eyeball the whole film
```

And in the browser console, to confirm the mouse never leaves frame:

```js
for (let t = 27; t <= 38; t += 0.25) {
  await window.__reveal.seek(t);
  const { ndc } = window.__reveal.debug();
  if (Math.abs(ndc.x) > 0.6) console.warn(t, ndc);
}
```

## 10. Untracked local state

`.claude/launch.json` **in the main repo** (`C:\Users\ASUS\My Drive\Hack Club`)
was given a `reveal` entry pointing at `D:/dev/micromouse-26-reveal/...`. That
edit is on the `wiki-hackclub-rebrand` branch's working tree and is **not
committed** — it is machine-specific. The committed copy in this worktree uses
a relative `micromouse-reveal` prefix and is portable.

One empty directory shell may remain at
`C:\Users\ASUS\My Drive\Hack Club\.claude\worktrees\micromouse-26-reveal`,
held by a Google Drive file handle. It contains no files. Delete it once Drive
releases it.
