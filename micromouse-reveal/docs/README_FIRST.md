# Micro-Mouse '26 Reveal Animation - Prompt Package

## What this package is

This is a complete creative and implementation package for a **42-48 second vertical launch trailer** for UCD ElecSoc's **Micro-Mouse '26** event.

The core idea is:

> **Last year, ElecSoc built the momentum. This year, that momentum enters the maze.**

The trailer should not feel like a slideshow or an ordinary recap. It begins as a kinetic memory of Robotics Club, MakerLabs, Makerthon and RoboExpo, then sharply pivots into a cinematic micromouse maze run. The route ultimately resolves into the ElecSoc circuit logo before the event title lands.

## Recommended workflow

1. Upload the entire `assets` folder to Claude Code.
2. Paste `01_MASTER_PROMPT_CLAUDE_CODE.md`.
3. Ask Claude to complete the structural pass before polishing.
4. Use `03_MAZE_SEQUENCE_LOCKED_PROMPT.md` if the maze geometry, walls or camera are weak.
5. Use the targeted prompts in `06_REVISION_PROMPTS.md` rather than asking for broad rewrites.
6. Add the confirmed date, time, venue and sign-up URL only when available. Do not let the model invent them.

## Recommended tool

Use **Claude Code** for the final animation because this concept needs deterministic timing, real asset handling, 3D camera control and export. A good implementation stack is:

- Vite
- Three.js
- GSAP
- HTML/CSS overlays
- Playwright or Puppeteer frame capture
- FFmpeg export

## Output target

- Aspect ratio: 9:16
- Resolution: 1080 x 1920
- Frame rate: 30 fps
- Duration: 42-48 seconds
- Format: H.264 MP4
- Primary platform: Instagram Reel
- The trailer must still communicate when viewed muted.

## Creative line

**LAST YEAR, WE MADE CHAOS.  
THIS YEAR, WE MAKE SPEED.**
