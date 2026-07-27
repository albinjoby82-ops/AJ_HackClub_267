---
title: Software Troubleshooting
layout: default
parent: 5. Software
nav_order: 5
---

# Software Troubleshooting

Start with the simplest layer and change one thing at a time.

## A board does not appear

1. Use a known data-capable USB cable.
2. Try another USB port.
3. Disconnect unnecessary USB devices.
4. Check whether the board powers on.
5. Reopen the IDE and board selector.
6. Check the operating system's device list.

## Upload fails

- Select the exact board and port.
- Close Serial Monitor and other programs using the port.
- Press reset once and retry.
- For some ESP32 boards, hold **BOOT** while upload begins.
- Remove circuits from pins used for USB Serial or boot configuration.
- Upload the smallest example, such as Blink.

## Code will not compile

Read the **first useful error**, not only the final summary. Check:

- Missing semicolons or braces
- Misspelled names and incorrect capitalisation
- A library that is not installed
- Code written for a different board
- Multiple tabs defining the same name

## Serial output is unreadable

Match the baud rate in the code and Serial Monitor:

```cpp
Serial.begin(115200);
```

Reset the board after opening the monitor if startup messages were missed.

## Ask for help effectively

Include:

- Board model
- Operating system
- IDE and board-package version
- Complete error text
- Smallest sketch that reproduces it
- Circuit diagram or clear photo
- What you expected and what happened
