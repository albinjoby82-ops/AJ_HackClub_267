# GAME_DESIGN - Arduino Arcade

Why each game is built the way it is, and the numbers you would tune first.

## Design brief

A student walks up to a stall, sees a breadboard with two knobs and four
buttons, and must be *playing* within ten seconds without an instructor. Each
session is 2–5 minutes. The hardware is cheap and slightly noisy. Therefore:

* **Absolute analog mapping.** Knob position maps directly to a position on
  screen (lane, orbit angle, channel, paddle). Nothing is velocity-controlled,
  so there is no "where am I?" moment when a player takes over mid-session.
* **Light smoothing only.** Exponential smoothing at ~0.45 in
  `Controller.update` plus a small filter in the firmware. Enough to kill ADC
  jitter, little enough that steering still feels physical.
* **Dead zones at both ends** (3% by default) so a cheap pot can still reach a
  solid 0.0 and 1.0.
* **Buttons are always meaningful.** Every game uses all four; none of them are
  decorative.
* **No fail states that need explaining.** Crashes, hull damage, meltdown, and a
  score to 7 - all legible at a glance.

## Shared systems

`BaseGame` owns the state machine (`INTRO → COUNTDOWN → PLAYING ⇄ PAUSED →
GAME_OVER`), the pause menu, the game-over card, high-score submission, particle
and floating-text systems, and screen shake. A game file therefore contains only
its own rules and rendering - roughly 400 lines each rather than 900.

Pause is reachable without a keyboard (hold B3 + press B4, or B1/B2 on the pause
menu with pot 1 scrolling it), which matters when the laptop is out of reach.

---

## NEON DRIFT

**Fantasy:** OutRun at night.

Pseudo-3D road: for each screen row, `depth = (y - horizon) / (height - horizon)`
gives a linear taper for road width and `d = 1/depth - 1` gives world distance.
Curvature bends the row centre by the *difference* between the curve ahead and
the curve at the camera, scaled by `(1 - depth)` - far rows bend, the player's
row never does. The resulting per-frame row table is also used to project
traffic, so cars always sit exactly on the tarmac.

* Pot 1 → target lane position, reached with a spring (`grip` 7.5, or 3.4 while
  drifting, which is what makes B2 feel like a handbrake).
* Pot 2 → target speed; boost overrides it and drains the boost meter.
* Curvature pushes the car sideways proportionally to speed - fast corners
  genuinely fight you.
* Near-miss scoring is the hook: passing within a small margin raises the combo
  to x8 and refills boost, so the optimal line is the dangerous one.
* Three crashes end the run. Damage pips, not an abstract health bar.

Tuning knobs: `MAX_SPEED`, `BOOST_SPEED`, `ROAD_SCREEN_FRAC`, `CURVE_STRENGTH`,
spawn weights in `_spawn`.

---

## ORBITAL DEFENDER

**Fantasy:** you *are* the gun turret, and both knobs are physically attached
to it.

Pot 1 is an absolute angle around the orbit ring: a full knob sweep is a full
lap. Pot 2 swings the aim ±103° around the outward radial. Two on-screen dials
in the corner mirror the real knobs so the mapping is unmistakable.

* B1 fires (0.14 s cadence, with recoil pulling the turret inward slightly).
* B2 raises a shield ring on the orbit - it burns enemies that touch it and
  absorbs station damage, but drains fast, so it is a decision not a default.
* B3 fires a limited homing missile with an area blast; B4 is a screen-clearing
  EMP. Charges are refilled by clearing waves and killing heavy drones, which
  rewards aggression.
* Waves scale count, speed and HP; every fourth wave adds a heavy drone with a
  health bar.
* Combo multiplier from consecutive kills within 2.2 s.

Tuning knobs: `_spawn_enemy` speeds, `SHIELD_DRAIN`/`SHIELD_REGEN`,
`FIRE_INTERVAL`, wave sizing in `_start_wave`.

---

## REACTOR SYNC

**Fantasy:** the panic of a control room. This is the game that exists to prove
analog input beats a gamepad.

Two channels each have a value (your knob) and a moving target with a tolerance
window that shrinks with difficulty. Staying inside scores continuously and
regenerates stability; drifting outside drains stability and raises heat. The
waveform display makes the match visceral: the ghost wave is the target
frequency, the bright wave is yours, and they lock into phase when you are right.

* B1/B3 lock a channel (only when it is already in sync - a skill check, not a
  free pass), with a cooldown.
* B2 vents heat, B4 discharges accumulated core charge for a payout scaled by
  how full it was.
* Alarms name a button and a deadline. Right button = big score + stability;
  wrong button = penalty. This is what turns the game into slapping the board.
* Random events keep it unstable: REVERSED (controls flip for 6 s), SURGE,
  PRESSURE, SHRINK (tolerance halves), OVERHEAT.
* The whole screen deteriorates as stability falls: colour shifts red, the core
  pulses faster, screen shake, and scanline tearing above 35% instability.

Tuning knobs: `Channel.update_target` zone formula, alarm `duration`, event
timers in `_trigger_event`, `difficulty` ramp (`survived / 150`).

---

## TWIN PONG

**Fantasy:** two people fighting over one breadboard.

Deliberately the simplest rules in the set, because it is the social game.
Pot 1 and pot 2 are the two paddles, so it needs no explanation at all.

* Ball speed grows 7% per paddle hit up to a cap; contact point sets the angle.
* B1/B3 are a short-cooldown **blast** that shoves nearby balls back at speed -
  a genuine skill move and a great panic button.
* B2/B4 serve immediately instead of waiting out the countdown.
* Power-ups spawn as hexagons in mid-court and are triggered by hitting them
  with the ball, so they are always earned by play: multi-ball, giant paddle,
  shrink rival, slow motion, speed ball, curve ball, shield, reverse rival.
* Fairness: debuffs on a player are cleared when they lose a point, so a
  power-up cannot snowball a match. Spare balls in multi-ball leave the court
  without conceding - only the last ball scores.
* First to 7. No high score is stored; the result is the scoreline.

Tuning knobs: `WIN_SCORE`, `BASE_SPEED`/`MAX_SPEED`, `PADDLE_H_RATIO`,
`BLAST_COOLDOWN`, `POWERUP_TYPES`.

---

## Decisions worth knowing

* **Calibration is stored, not repeated.** It is offered automatically on the
  first real-hardware run and from Settings afterwards.
* **The keyboard backend ignores stored calibration** - keyboard axes already
  cover the full range, and applying a pot's recorded range would clip them.
* **Twin Pong does not track a high score** (`tracks_high_score = False`);
  a versus result is not comparable between sessions.
* **Event Mode timeout is 75 s** - long enough that a thoughtful player is not
  interrupted, short enough that an abandoned game frees the stall.
* **Screen shake is capped** and decays fast; it is used for crashes, big hits
  and EMPs only.
