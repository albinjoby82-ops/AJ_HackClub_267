---
title: Advanced Task 1 - Modes, Switches and Fine Control
layout: default
parent: Workshop 02 - Signals to Speed
nav_order: 20
---

# Advanced Task 1 - Modes, Switches and Fine Control

Add a push button using `INPUT_PULLUP`. Each press changes how the potentiometer controls the servo:

- **Coarse mode:** full safe servo range
- **Fine mode:** a narrow range around the centre
- **Hold mode:** keep the last target angle

Use an `enum` to represent the mode, detect the button's transition from `HIGH` to `LOW`, and debounce it without a long delay.

```cpp
enum Mode { COARSE, FINE, HOLD };
Mode mode = COARSE;
```

{: .challenge-title}
> Make it usable
>
> Print the selected mode only when it changes. Add an LED whose colour communicates the active mode.
