---
title: C3 - Working with AI Agents on Hardware
layout: default
parent: Software
nav_order: 3
---

# C3 - Working with AI Agents on Hardware

AI coding agents can help you write firmware, inspect logs and test ideas faster. They become useful hardware teammates only when you give them evidence from the physical system.

In this guide you will learn how to:

- give an agent enough hardware context to make safe suggestions;
- turn a vague hardware fault into a repeatable debug loop;
- verify library APIs, board pins and electrical assumptions;
- use Git checkpoints and small changes to protect working code; and
- coordinate agent-assisted work across a team.

{: .warning}
> An AI agent cannot see a loose wire, measure a voltage or know that a component is hot. Power off before rewiring. Check voltage levels, polarity and current limits against the real datasheet.

## 1. Start with the most important rule

A software agent can inspect files and reason about text. Your robot also depends on facts outside those files:

- which board revision is on the bench;
- which pins are physically connected;
- whether grounds are shared;
- the exact sensor and breakout-board versions;
- supply voltage and logic voltage;
- what the LEDs, motors and sensors actually do; and
- what appeared in the serial monitor.

If the agent does not receive those facts, it fills the gaps with assumptions. A confident answer can still be wrong for your hardware.

### Build a hardware context pack

Keep the following information in the repository, preferably under a `docs/` folder:

1. a pinout card for your exact board and robot;
2. links or copies of component datasheets;
3. the library name and version used by the project;
4. a short wiring table;
5. known-good test results; and
6. the commands needed to build, flash and open the serial monitor.

A small wiring table is often more useful than a long description:

| Signal | Controller pin | Device pin | Notes |
|---|---:|---|---|
| I2C SDA | GPIO 6 | SDA | 3.3 V logic |
| I2C SCL | GPIO 7 | SCL | 3.3 V logic |
| Left XSHUT | GPIO 18 | XSHUT | Address 0x30 |
| Front XSHUT | GPIO 19 | XSHUT | Address 0x31 |
| Right XSHUT | GPIO 20 | XSHUT | Address 0x29 |
| Ground | GND | GND | Common ground required |

These are the event debug kit’s pin assignments. Give the agent the [event wiring map](#/docs/Micromouse2026/Hardware/ESP32C6.md) and the exact [debug sketch](#/docs/Micromouse2026/Debug/index.md) you are running. The comments at the top of that sketch are the wiring reference. GPIO21/22 belong to the Motor A encoder, not the sensor bus.

### Use a context-first prompt

```text
You are helping with an ESP32 Micromouse.

Read these files first:
- docs/pinout.md
- docs/sensors/VL53L0X-datasheet.pdf
- platformio.ini
- src/sensors.cpp

Hardware facts:
- Board: [exact board and revision]
- Sensor library: [name and version]
- SDA/SCL pins: [verified pins]
- XSHUT pins: [verified pins]
- Supply and logic voltage: [verified voltage]

Problem:
[Describe what you expected and what actually happened.]

Do not rewrite the whole subsystem.
First list the evidence you need, then propose one small test.
```

## 2. Use an evidence-driven debug loop

Do not ask the agent to guess until something works. Use the same short loop every time:

1. **Observe** the real behaviour.
2. **Add logging** around one assumption.
3. **Run** the code on the physical robot.
4. **Paste the real output** back to the agent.
5. **Change one thing**.
6. **Retest** and record the result.

For example:

```cpp
Serial.printf(
    "left_mm=%u right_mm=%u\n",
    leftDistanceMm,
    rightDistanceMm
);
```

A useful report includes the actual output:

```text
Expected: both sensors report a distance every 50 ms.
Actual: left sensor works; right sensor times out.

Serial output:
I2C scan: 0x29
left init: OK
left new address: 0x30
right init: TIMEOUT
```

This is much better evidence than saying "the sensor does not work."

## 3. Worked example: add one distance sensor

Use the supplied [step 3: left ToF](#/docs/Micromouse2026/Debug/03_tof_1.md), then [step 4: left + front](#/docs/Micromouse2026/Debug/04_tof_2.md). Each page includes the complete sketch and expected output.

For step 4, wire both sensors to 3V3, GND, SDA GPIO6 and SCL GPIO7. Left XSHUT is GPIO18 and front XSHUT is GPIO19. Leave the right ToF disconnected for this test. The IMU may stay connected.

The supplied code uses **VL53L0X by Pololu** and this startup sequence:

1. Hold left and front XSHUT LOW.
2. Wake left, initialize it at 0x29, and move it to 0x30.
3. Wake front, initialize it at 0x29, and move it to 0x31.
4. Confirm both PASS and that covering each sensor changes its own reading.

Step 5 adds right XSHUT on GPIO20. Right wakes last and **keeps 0x29**. Do not ask an agent to change that to 0x32 when using the supplied sketches.

A useful follow-up includes the exact failing step:

```text
I am running 04_tof_2 unchanged with VL53L0X by Pololu.
SDA=GPIO6, SCL=GPIO7, left XSHUT=GPIO18, front XSHUT=GPIO19.
Only left and front ToF sensors are powered; both use 3V3 and common GND.
Left at 0x30 passes, but front fails when GPIO19 goes high.
The full startup output and a checked wiring table are below.

Read the sketch's header comments first. Check only the initialization
sequence and wiring evidence. Do not change the pin map, addresses,
motor control or maze logic. Suggest one observation that distinguishes
a wiring problem from a library or initialization problem.
```

## 4. Recognise common agent failure modes

### Hallucinated library APIs

Different libraries expose different method names. An agent may suggest a function that exists in another library or an older release.

Before accepting code, check:

- the exact dependency in `platformio.ini` or `library.properties`;
- the installed version;
- the library's examples; and
- the function declaration in its header file.

### Outdated ESP32 pin references

"ESP32" describes a family of boards. Pin availability and boot behaviour vary between modules and revisions. Do not trust a generic pin diagram when your exact board has its own schematic.

Confirm that each selected pin:

- is physically broken out;
- is not reserved by flash, PSRAM or another onboard device;
- is safe during boot; and
- supports the required input, output or bus function.

### Treating a hardware fault as a software fault

Repeated code changes will not repair:

- a missing common ground;
- reversed power connections;
- a loose jumper;
- an unpowered sensor;
- a damaged component; or
- a logic-level mismatch.

If a minimal test fails, stop changing application code and inspect the circuit.

### Replacing a working subsystem

Large rewrites hide the cause of a fault and make rollback difficult. Ask the agent to preserve interfaces and change one behaviour at a time.

## 5. Ask for small, reviewable changes

Avoid broad requests such as:

```text
Rewrite the sensor code and make the robot work.
```

Use a constrained request instead:

```text
In src/sensors.cpp, add serial logging around the right VL53L0X
initialisation. Do not change addresses, timing constants, motor code or
public function signatures. Show me the diff and explain each new log line.
Do not commit or push.
```

Before running a change, agree on:

- the file or function that may change;
- the behaviour that must stay unchanged;
- the observation that will count as success; and
- a stopping condition if the test fails.

## 6. Create a Git safety checkpoint

Commit the last known-good state before a large agent-assisted change:

```powershell
git status
git diff
git add src/sensors.cpp docs/pinout.md
git commit -m "checkpoint: verified single distance sensor"
```

After the agent edits files, review before committing:

```powershell
git status
git diff
```

A checkpoint does not prove the new code is correct. It gives the team a clear comparison point and makes it easier to undo a bad experiment without losing known-good work.

## 7. Coordinate agent work across the team

Two people should not ask separate agents to rewrite the same file at the same time.

Use a simple ownership rule:

- one person owns a file or subsystem during a task;
- pull or sync before starting;
- announce the files being changed;
- use small commits with descriptive messages;
- share serial logs with the commit or pull request; and
- integrate one tested change before starting the next overlapping change.

A useful handoff note looks like this:

```text
Owner: Nick
Files: src/sensors.cpp, docs/pinout.md
Hardware tested: left and right VL53L0X
Result: both addresses visible; right reading still noisy
Serial log: logs/2026-09-10-distance-sensors.txt
Next test: keep wiring fixed and compare timing budget only
```

## 8. Know when to stop the agent

Pause the software work and ask a human to inspect the robot when:

- a component becomes hot;
- power or logic voltage is uncertain;
- the board resets when a motor starts;
- serial output disappears after rewiring;
- the minimal device example also fails; or
- the proposed change would disable a safety limit.

## Practical exercise

Use one real subsystem on your Micromouse and complete this checklist:

- [ ] Record the exact board, component and library versions.
- [ ] Create or verify a wiring table.
- [ ] Save the relevant datasheet or link under `docs/`.
- [ ] Ask the agent for one logging-only change.
- [ ] Run the code and paste the real serial output.
- [ ] Ask for one diagnosis test, not a rewrite.
- [ ] Review `git diff` before committing.
- [ ] Add the result to a team handoff note.

## Key takeaway

AI works best on hardware when the team supplies the part it cannot observe: the real circuit, verified documentation and measured output. Keep changes small, use evidence and protect every known-good state.
