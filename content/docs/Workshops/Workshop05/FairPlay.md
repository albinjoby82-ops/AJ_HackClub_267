---
title: Task 2 - Detect False Starts and Debounce Input
layout: default
parent: Workshop 05 - Reaction Timer
nav_order: 2
---

# Task 2 - Detect False Starts and Debounce Input

The first version cannot detect a player holding the button before the light appears. Replace the random blocking delay with a waiting state that continuously checks the input.

## Requirements

- Choose a random cue time using `millis()`.
- Report a false start if the button is pressed early.
- Require the button to be released before a new round.
- Accept a press only after it remains stable for at least `20 ms`.

Model the game with states:

```cpp
enum GameState { READY, WAITING, TIMING, RESULT };
```

{: .challenge-title}
> Remove every delay
>
> Keep the game responsive using state and timestamps only. The program should never become stuck waiting inside a loop.
