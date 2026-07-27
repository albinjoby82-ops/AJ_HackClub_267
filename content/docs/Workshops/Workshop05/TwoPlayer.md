---
title: Advanced Task 1 - Build a Two-Player Game
layout: default
parent: Workshop 05 - Reaction Timer
nav_order: 4
---

# Advanced Task 1 - Build a Two-Player Game

Add a second button and two player LEDs.

## Rules

- Either player can false-start.
- The first valid press wins the round.
- Near-simultaneous presses must be resolved consistently.
- A player must release their button before the next round.
- First to five points wins the match.

Read both input states before deciding the winner. Record timestamps for both edges rather than allowing the order of two `if` statements to decide.

{: .challenge-title}
> Tournament mode
>
> Add player names over Serial, best-of-three matches and a tie threshold where presses within `3 ms` trigger a replay.
