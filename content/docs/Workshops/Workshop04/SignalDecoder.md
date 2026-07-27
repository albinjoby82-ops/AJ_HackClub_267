---
title: Advanced Task 2 - Decode a Noisy Message
layout: default
parent: Workshop 04 - Good Waves, Bad Vibes
nav_order: 5
---

# Advanced Task 2 - Decode a Noisy Message

Encode text as timed HIGH and LOW pulses, add imperfect timing, then recover it.

## Protocol

- Start marker: `20 ms HIGH`
- Binary `0`: `5 ms HIGH`, then `5 ms LOW`
- Binary `1`: `10 ms HIGH`, then `5 ms LOW`
- Send eight bits per character, most significant bit first

## Decoder requirements

- Detect the start marker.
- Measure each HIGH pulse.
- Classify it as `0`, `1` or invalid.
- Assemble eight bits into a character.
- Reject incomplete or badly timed frames.
- Print the decoded message and an error count.

{: .challenge-title}
> Make it robust
>
> Randomly vary every pulse by up to 15%. Choose classification thresholds that still decode reliably, then determine the largest variation your decoder tolerates.
