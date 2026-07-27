---
title: Task 3 - Add Feedback and Scoring
layout: default
parent: Workshop 05 - Reaction Timer
nav_order: 3
---

# Task 3 - Add Feedback and Scoring

Add a piezo buzzer and keep useful statistics over several rounds.

Track:

- Current reaction time
- Best reaction time
- Number of valid rounds
- Number of false starts
- Running average

Use `unsigned long` for accumulated times. Avoid dividing until at least one valid round exists.

## Feedback design

- Short high tone: cue
- Low tone: false start
- Two tones: new personal best
- RGB colour or LED blink pattern: result category

{: .challenge-title}
> Persistent high score
>
> Store the best score in EEPROM and add a deliberate reset gesture. Avoid writing EEPROM on every loop because it has a limited write lifetime.
