# Micro-Mouse '26 teaser — render report

Generated from `micromouse-teaser/` on 2026-07-28.

## V2 revision (current delivery)

**`output/micromouse-teaser-final-v2.mp4` — 1080×1920, 30 fps, 16.67 s
(500 frames), H.264 High/yuv420p, AAC 48 kHz stereo, fast-start.**
Measured −14.02 LUFS integrated, −2.27 dBTP. All 15 checks in
`tools/validate.mjs` pass. The V1 outputs remain untouched alongside it.

Structural changes from V1:

| Change | Detail |
| --- | --- |
| `SMALLER.` removed | Word, beat and audio impact deleted; gap closed, not paused. Copy list no longer contains the word |
| Impacts retimed | `FASTER.` 7.40–8.70 s, `SMARTER.` 10.50–11.70 s, each on its own synthesised hit |
| Teaser line trimmed | `THE MAZE IS WAITING.` now 3.20–5.20 s |
| Bridge removed | The orange question-mark/route-draw animation and the standalone logo screen are gone entirely |
| Chase extended | Runs through the robot's final head-on approach to source frame 416 — the last frame before the source's route line begins its step-draw (417) |
| Direct reveal cut | Hard cut at frame 380 (12.67 s) from the parked, headlight-lit robot straight to the complete card, on the strongest hit in the score; 3-frame orange accent flash (0.16 → 0) |
| One reveal only | Card is fully assembled from its first frame; whole-card settle of 6 frames (opacity 0.75→1, scale 1.025→1) |
| Card held | Motionless 3.33 s (frames 388–488; mean luma delta 4.2e-3/255), then a 0.40 s fade with the audio |

End-card design changes (palette, wording and the official logo bitmap are
unchanged):

- Logo 320 → 384 px wide (+20 %), still the exact official asset at its
  native 376:235 aspect.
- `MICRO-MOUSE ’26` 126 → 142 px (+12.7 %), the dominant element.
- Tagline 34 → 44 px, tracking reduced to 8 — phone-readable without zooming.
- `COMING SOON` 46 → 54 px in a lightened tint of the palette orange
  (`#F0824F`) with a soft same-hue glow for contrast.
- Vertical rhythm tightened (logo→title gap 160 → 90 px, title→tagline
  54 → 56 px, tagline→callout 240 → 130 px); block optically centred in the
  TikTok-safe area, everything inside the 96 px side margins and above the
  reserved bottom 300 px.

Audio: the score is re-synthesised on the revised cue sheet, not spliced, so
retiming cannot produce jumps, repeated beats or clipped transients. The pulse
now drives all the way into the cut, the riser leaves `SMARTER.` at 11.67 s,
the reveal hit lands exactly on the cut, and a sustained 55/41 Hz pair carries
the motionless card into the fade.

Verified per the revision checklist: no frame contains `SMALLER.` (full
every-5th-frame scan); the only word titles are `FASTER.` and `SMARTER.`; no
route animation or logo-only screen exists after the final robot shot; the cut
frames (379|380) were inspected directly, along with 0.5 s, 4.0 s, 7.8 s,
10.8 s, 12.7 s, 13.1 s and 15.5 s.

The cut lands at 12.67 s rather than the suggested ~12.9 s: the source's
route-line animation visibly begins at source frame 417, so honouring the
"remove the route animation" requirement takes the out-point three frames
earlier than the suggested timing. The brief's few-frames adjustment allowance
covers this.

---

# V1 report (previous delivery, retained)

## Deliverables

| File | Detail |
| --- | --- |
| `output/micromouse-teaser-final.mp4` | 1080×1920, 30 fps, 19.37 s, 11.0 MB |
| `output/micromouse-teaser-preview.mp4` | 540×960, 30 fps, 19.37 s, 3.7 MB |
| `output/micromouse-teaser-contact-sheet.png` | 12 evenly spaced frames, 4×3 |
| `output/validation.json` | Full ffprobe + loudness measurements |
| `output/source-inventory.json` | Media inventory from the prepare step |

## Final specification

- **Duration** 19.37 s (581 frames at 30 fps) — inside the 18–21 s target
- **Video** H.264, High profile, `yuv420p`, 4551 kb/s
- **Audio** AAC-LC, 48 000 Hz, stereo, 194 kb/s
- **Container** MP4 with `+faststart` (verified: `moov` precedes `mdat` in the
  top-level atom table)
- No watermark, no social-media interface, no letterboxing, no stretched geometry

All 15 automated checks in `tools/validate.mjs` pass.

## Source clips used

The clean animation was identified **by content**, not by filename: 478×850 at
30 fps and ~20.3 s. (Resolution alone was not sufficient — an unrelated phone
clip in the same folder shares the 478×850 frame size, and an earlier pass
picked it up by mistake.)

Primary source: `WhatsApp Video 2026-07-28 at 16.41.36.mp4`

| Teaser section | Source range | Treatment |
| --- | --- | --- |
| Cold open | 0.00–1.00 s | Brightness ramp 0.55→1.0, slow pull-in |
| Activation detail | 1.00–1.70 s | 1.50→1.62× push-in on the robot front |
| Wheel / route detail | 1.73–2.57 s | 2.08→2.20× crop, framed below the baked-in type |
| Activation wide | 2.57–3.83 s | 1.26→1.16× drift, one sensor sweep |
| Steady approach | 4.77–6.23 s | Full frame, 1.00→1.05× |
| Chase | 7.17–13.77 s | Full frame, unaltered |
| Bridge to reveal | 13.80–15.10 s | Full frame; the orange route line draws the circle |

Deliberately excluded from the render:

- **1.72–2.55 s, 3.85–4.75 s, 6.25–7.15 s** — the source render has its own
  `SMALLER.` / `FASTER.` / `SMARTER.` burned into the picture at 478 px wide.
  Cutting around them let those words be re-set as live text at full
  resolution. The 1.73–2.57 s range was reclaimed as the tight wheel detail,
  where a 2.08× crop sits entirely below the baked type.
- **15.4–20.3 s** — the source's own end card. Rebuilt from scratch rather than
  upscaled, so the title and tagline are vector-crisp at 1080×1920.

## End card

Rebuilt as live DOM/SVG plus the official logo bitmap at its native 376×235
aspect. Reveal order is logo → title → tagline → `COMING SOON`. The orange ring
that opens the card starts at the position and radius the route line left the
circle at, then contracts into the logo's emblem — a match cut on the circle.

Fully assembled at frame 70 of the segment and **held completely motionless for
2.60 s** (frames 487–565 absolute) before a 0.53 s fade to black.

Motionlessness was verified two ways: three losslessly rendered stills spanning
the hold are byte-identical (matching MD5), and the encoded file's mean
frame-to-frame luma delta across the hold is 3.0e-3 / 255. The isolated 27/255
peak is a single-pixel I-frame quantisation artefact in the dark gradient, not
movement.

## Logo

`micromouse-reveal/public/assets/logos/elesoc_logo.png` — the existing official
asset in this repository, used unmodified at its native aspect ratio. It matches
the logo in the source animation's end card, so nothing was redrawn,
reinterpreted or fabricated.

## Fonts

**Bahnschrift** (`C:/Windows/Fonts/bahnschrift.ttf`), the brief's first choice.
It is a variable font, so the condensed cut comes from the `wdth` axis at 75–78
rather than a separate file; weights 600–700.

The face is embedded from `public/fonts/` via the `FontFace` API and loaded
behind `delayRender()`, so the render does not depend on host font
installation. Fallback chain: Arial Narrow → Segoe UI → sans-serif.

All on-screen copy is live text — no typography is baked into a raster image.
Side margins are 96 px minimum (the teaser line's measured margins are ~214 px);
the bottom 300 px is reserved for platform overlays and carries no copy.

## Audio

Entirely original and synthesised from scratch by `tools/generate-audio.mjs` —
oscillators, filtered noise and envelopes, with a seeded PRNG so every run is
identical. No sampled, licensed or third-party audio. The source video's own
audio is muted, and the pacing reference's music was never touched.

Layers: low electrical ambience and mains hum → power-on swell → sensor ping
with two reflections → servo clicks → a rhythmic pulse that tightens from 0.50 s
to 0.24 s spacing across the chase → three distinct impacts (pitch-rising, one
per word) → a controlled riser and route-line whoosh → reveal hit → a final low
hit under `COMING SOON` with a long tail decaying to silence.

**Measured on the delivered file: -13.87 LUFS integrated, -2.15 dBTP.**

The WAV is normalised to a -2.5 dBTP ceiling rather than -1, because the AAC
encode overshoots sample peaks by roughly 1 dB. An earlier build normalised the
WAV straight to -1 dBTP and the finished MP4 measured **+0.0 dBTP** — over the
ceiling. The delivery step now copies Remotion's video stream untouched and
encodes the audio exactly once, straight from the 24-bit WAV, so the peak stays
predictable and the video suffers no second lossy generation.

## Confirmation: no reference footage used

`WhatsApp Video 2026-07-28 at 16.41.36 (1).mp4` (576×1090, TikTok hackathon
teaser with a robotic hand, visible TikTok watermark, `@` handle and search bar)
was used **only** to study pacing — long dark holds, sparse single-word beats,
and a late reveal.

Not one frame, crop, mask, trace or element of it appears in the render. It is
never copied into `public/`, and `tools/prepare-media.mjs` only ever writes the
478×850 primary to the bundle. A frame-by-frame visual scan of the finished
teaser (every 6th frame) confirms no watermark, interface, handle or robotic
hand anywhere.

## Limitations and notes

- **Source resolution.** The supplied animation is 478×850 — a WhatsApp-compressed
  copy. It is upscaled 2.26× with Lanczos plus mild unsharp (`5:5:0.45`). The
  content is flat-shaded 3D with large uniform areas, so it holds up well, but
  this is not a substitute for a native 1080×1920 render. **If the original
  project that produced this animation is available, re-exporting it at
  1080×1920 and re-running `npm run build:all` would visibly improve the
  footage.** No composition changes would be needed.
- The wheel detail at 1.73–2.57 s is the softest shot, being a 2.08× crop of an
  already-upscaled source (~4.7× effective). It is brief and deliberately dark.
- `CAN YOU OUTRUN THE MAZE?` was **not** used. The brief marks it optional and
  says to drop it if it would make the piece text-heavy; with the teaser line,
  three impact words and a four-element end card, a fifth text beat crowded the
  run-up to the reveal.
- Aspect ratio: 478×850 is 0.5624 against 1080×1920's 0.5625, a 0.03 %
  difference. A straight Lanczos resize therefore fills the frame with no crop
  and no padding, and the distortion is not measurable on screen.
- **Disk space:** the C: drive has ~330 MB free. Rendering had to be redirected
  to D: (`TEMP`/`TMP` and the render masters) because Chrome refused to fetch
  assets with C: that full. This is worth clearing — it will also affect Google
  Drive sync for this folder.

## Rebuilding

```bash
npm run build:all
```

Runs prepare-media → audio → preview → final → validate. On this machine set
`TEMP`/`TMP` to a path on D: first, per the disk-space note above.
