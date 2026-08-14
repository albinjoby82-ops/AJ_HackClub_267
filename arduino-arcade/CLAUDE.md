# CLAUDE.md - Arduino Arcade project rules

Permanent rules for anyone (human or agent) working in this repository.

## Architecture

1. **One shared Controller API.** Everything reads `app.controller`, which
   exposes `pot1`, `pot2` (0.0–1.0), `pot1_raw`, `pot2_raw` (0–1023),
   `button1..4`, `buttonN_pressed`, `buttonN_released`, `connected`, `kind`.
2. **Games must never import `serial` or open ports.** Only
   `arcade/serial_controller.py` touches PySerial. New backends subclass
   `Controller` and implement `_poll`.
3. **Keyboard mode must always work.** Every feature has to be reachable and
   testable with `python main.py --keyboard`. A change that only works with real
   hardware is not finished.
4. **Do not break Arduino packet compatibility.** The protocol is
   `POT1,POT2,B1,B2,B3,B4\n` at 115200 baud. Changing the field order or count
   means reflashing every board at the event - don't.
5. **Standard pinout is fixed:** D2–D5 buttons (INPUT_PULLUP, pressed = LOW),
   A0/A1 pot wipers. Documented in WIRING.md and on the Controller Test screen;
   change all three together or not at all.
6. **Games subclass `BaseGame`** (`arcade/game.py`) and implement `reset_game`,
   `update_play`, `draw_play`. The base class owns intro / countdown / pause /
   game-over / restart / high scores. Do not re-implement those per game.
7. **Register new games in `games/__init__.py` and in `GAME_CARDS`**
   (`arcade/scenes/launcher.py`).

## Runtime behaviour

8. **60 FPS target**, delta-time movement everywhere. No fixed per-frame
   constants; use `dt`.
9. **Every game returns cleanly to the launcher** (`quit_to_launcher`) and can
   restart without leaking state - `reset_game` must clear everything.
10. **Nothing may hard-crash on hardware trouble.** Missing Arduino, mid-game
    disconnect, malformed packets, no audio device, missing or corrupt settings,
    odd window sizes: all degrade gracefully with a visible message.
11. **Bounded work per frame.** Particle systems are capped; cache surfaces
    rather than rebuilding them; never open a serial port on the render thread.
12. **Audio is optional.** Always go through `app.audio`; it is a no-op when the
    mixer failed to initialise.

## Assets and content

13. **No copyrighted assets.** Graphics are Pygame primitives; sounds are
    synthesised into `assets/sounds/` by `arcade/audio.py`. Do not add binary
    art or downloaded fonts.
14. **Shared visual identity** lives in `arcade/ui.py` (palette, fonts, panels,
    bars, glow). Games pick an accent colour; they do not invent new UI widgets
    when a shared one exists.
15. Additive glow must be composited onto **opaque black** surfaces -
    `BLEND_ADD` ignores per-pixel alpha and will smear a solid rectangle
    otherwise. Use `ui.draw_text(glow=...)` / `ui.draw_glow_circle`.

## Quality gates

16. **Tests must stay green:** `python -m pytest -q`.
17. **Smoke test must stay green:** `python scripts/smoke_test.py` drives every
    screen and game headlessly. Run it after touching any game.
18. Use `scripts/capture.py` to eyeball rendering changes without a display.
19. No TODO placeholders, debug prints, or dead code in committed work.
20. Broad `except Exception` is only acceptable at hardware/OS boundaries
    (serial, mixer, file IO) and must record or surface the error.

## Event usability

21. This is built for a hackathon stall: quick to start, obvious to a first-time
    player, tolerant of cheap components and rough handling.
22. Every game's intro screen must show its controls as short animated hints,
    never a paragraph.
23. Keep **CONTROLLER TEST** accurate - it is the workshop's first-line wiring
    diagnostic.
24. **Windows is the primary target.** Avoid Windows-only APIs, but verify there.
