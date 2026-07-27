---
title: Debugging Arduino Projects
layout: default
parent: 6. Programming
nav_order: 8
---

# Debugging Arduino Projects

Debugging is the process of turning “it does not work” into one small, testable question.

## Use the three-layer check

### 1. Does it compile and upload?

- Read the first useful compiler error.
- Check board and port.
- Upload Blink to separate software problems from circuit problems.

### 2. Is the wiring correct?

- Turn power off.
- Compare every connection with the schematic.
- Check shared ground, polarity and component values.
- Check whether breadboard power rails are split.
- Place ICs across the centre gap.

### 3. Is the program doing what you think?

- Print inputs, states and calculated outputs.
- Test one subsystem at a time.
- Replace a sensor temporarily with a fixed test value.
- Reduce the program to the smallest failing example.

## Common compiler mistakes

```cpp
int ledPin = 13;            // semicolon
digitalWrite(ledPin, HIGH); // correct capitalisation
```

Check matching parentheses `()`, braces `{}` and quotation marks.

## Common logic mistakes

```cpp
if (buttonState == HIGH) {  // comparison, not assignment
}
```

Also check:

- A loop condition that never becomes false
- `setup()` versus repeatedly running `loop()`
- Integer division losing a decimal part
- A local variable hiding a global variable with the same name
- Blocking `delay()` preventing input checks

## Serial debugging

```cpp
Serial.print("state=");
Serial.print(state);
Serial.print(", sensor=");
Serial.println(sensorValue);
```

Match the baud rate and avoid printing so rapidly that useful behaviour is obscured.

## Hardware symptoms

- Random resets often suggest power or short-circuit problems.
- A floating input changes unpredictably; use a pull-up or pull-down.
- An LED needs a current-limiting resistor and correct polarity.
- Motors and servos should not be powered from GPIO.

{: .tip-title}
> Change one thing
>
> Write down the observation, make one controlled change and test again. Changing wiring and code simultaneously destroys useful evidence.
