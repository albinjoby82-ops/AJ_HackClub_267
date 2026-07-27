---
title: Logic and Comparisons
layout: default
parent: 6. Programming
nav_order: 5
---

# Logic and Comparisons

Comparisons produce `true` or `false`.

| Operator | Meaning |
| --- | --- |
| `==` | equal |
| `!=` | not equal |
| `<` | less than |
| `<=` | less than or equal |
| `>` | greater than |
| `>=` | greater than or equal |

```cpp
if (temperature >= 30) {
  fanOn = true;
}
```

{: .warning}
> `=` assigns a value. `==` compares two values.

## Combine conditions

| Operator | Meaning |
| --- | --- |
| `&&` | both conditions are true |
| `||` | either condition is true |
| `!` | invert true/false |

```cpp
if (enabled && temperature > 30) {
  startFan();
}
```

## `else if` and `else`

```cpp
if (reading > 800) {
  setColour(255, 0, 0);
} else if (reading > 400) {
  setColour(0, 255, 0);
} else {
  setColour(0, 0, 255);
}
```

Only the first matching branch runs.

## State with `enum`

```cpp
enum Mode { READY, RUNNING, FINISHED };
Mode mode = READY;

if (mode == READY && buttonPressed) {
  mode = RUNNING;
}
```

Named states are clearer than unexplained numbers such as `mode = 2`.
