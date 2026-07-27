---
title: Variables and Data Types
layout: default
parent: 6. Programming
nav_order: 4
---

# Variables and Data Types

A variable has a type, name and value:

```cpp
int score = 0;
```

## Common Arduino types

| Type | Example | Use |
| --- | --- | --- |
| `bool` | `bool enabled = true;` | true/false state |
| `char` | `char command = 'R';` | one character |
| `int` | `int angle = 90;` | ordinary whole numbers |
| `long` | `long total = 100000;` | larger signed whole numbers |
| `unsigned long` | `unsigned long started = millis();` | time and non-negative counters |
| `float` | `float voltage = 3.3;` | decimal calculations |
| `String` | `String name = "robot";` | convenient text on Arduino |

`String` uses a capital `S`. A lowercase `string` is not the Arduino `String` type.

## Constants

Use `const` for values that should not change:

```cpp
const int buttonPin = 2;
const unsigned long sampleInterval = 100;
```

## Choosing a type

- Match the possible range of values.
- Use `unsigned long` for values returned by `millis()`.
- Remember that type sizes vary between board families.
- Avoid decimal arithmetic when whole-number maths is sufficient.

## Integer division

```cpp
float resultA = 5 / 2;     // 2.0: division happened as integers
float resultB = 5.0 / 2.0; // 2.5
```

## Modulus

`%` gives the remainder after integer division:

```cpp
bool isEven = count % 2 == 0;
```

It is useful for alternating states and wrapping counters.
