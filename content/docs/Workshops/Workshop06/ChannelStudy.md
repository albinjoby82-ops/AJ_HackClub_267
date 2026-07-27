---
title: Task 3 - Investigate Channels and Security
layout: default
parent: Workshop 06 - ESP32-C6 Wi-Fi Explorer
nav_order: 3
---

# Task 3 - Investigate Channels and Security

Extend the scanner to report channel number and the authentication mode advertised by each access point.

```cpp
Serial.print(" channel:");
Serial.print(WiFi.channel(i));
Serial.print(" encryption:");
Serial.println(WiFi.encryptionType(i));
```

Consult the installed ESP32 Arduino core examples for the available encryption labels because enum names can vary between versions.

## Investigate

- Count networks on each observed channel.
- Separate 2.4 GHz and 5 GHz results if your board/core exposes both.
- Compare channel congestion with RSSI.
- Identify networks advertising no encryption, without attempting to connect.

{: .challenge-title}
> Recommend a channel
>
> Create a simple congestion score that considers both the number and strength of nearby networks. Explain the limitations of your recommendation.
