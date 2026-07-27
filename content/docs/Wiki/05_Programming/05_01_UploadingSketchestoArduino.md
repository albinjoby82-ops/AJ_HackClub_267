---
title: Upload Your First Sketch
layout: default
parent: 6. Programming
nav_order: 1
---

# Upload Your First Sketch

A **sketch** is the program uploaded to an Arduino-compatible board.

## Upload Blink

1. Connect the board with a data-capable USB cable.
2. Open Arduino IDE.
3. Select the correct board and port.
4. Open **File > Examples > 01.Basics > Blink**.
5. Select **Verify** to compile the sketch.
6. Select **Upload**.

The onboard LED should blink after uploading.

## Change it

Find these lines:

```cpp
delay(1000);
```

The number is milliseconds. Change both values to `200`, upload again and predict what will happen.

## What the messages mean

- **Compiling:** translating and checking the program
- **Uploading:** transferring the compiled program
- **Done uploading:** transfer completed
- **Error:** compilation or upload failed; read the first useful message

If the board is missing or upload fails, use [Software Troubleshooting](../04_Software/04_05_Troubleshooting.md).

{: .tip}
> Save your own copy before making large changes to an example.
