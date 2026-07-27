---
title: Timing Without delay()
layout: default
parent: 6. Programming
nav_order: 7
---

# Timing Without `delay()`

`delay()` pauses the whole sketch. During that pause, the program cannot respond to buttons, update several effects or process Serial commands.

Use `millis()` to ask whether enough time has passed:

```cpp
const int ledPin = 13;
const unsigned long interval = 500;

unsigned long previousTime = 0;
bool ledOn = false;

void setup() {
  pinMode(ledPin, OUTPUT);
}

void loop() {
  unsigned long now = millis();

  if (now - previousTime >= interval) {
    previousTime = now;
    ledOn = !ledOn;
    digitalWrite(ledPin, ledOn);
  }

  // Buttons, sensors and Serial can still be checked here.
}
```

## Why subtract?

Use:

```cpp
now - previousTime >= interval
```

rather than comparing against `previousTime + interval`. Unsigned subtraction continues to work when the `millis()` counter eventually wraps around.

## Multiple timers

Give each activity its own previous time:

```cpp
unsigned long previousSensorTime = 0;
unsigned long previousLedTime = 0;
```

## State machines

For a sequence with several stages, combine a state and a timestamp:

```cpp
enum State { WAITING, ACTIVE, RESULT };
State state = WAITING;
unsigned long stateStarted = 0;
```

Change the state once, record when it began and let `loop()` keep running.

{: .challenge-title}
> Build two independent effects
>
> Blink one LED every `300 ms`, another every `700 ms`, and report a sensor every `100 ms` without using `delay()`.
