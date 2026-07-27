---
title: Task 2 - Build a Signal-Strength Survey
layout: default
parent: Workshop 06 - ESP32-C6 Wi-Fi Explorer
nav_order: 2
---

# Task 2 - Build a Signal-Strength Survey

Choose one network you are permitted to observe and measure its RSSI in several locations.

## Method

1. Mark five locations on a simple room sketch.
2. Keep the ESP32-C6 at the same height and orientation.
3. Take ten scans at each location.
4. Calculate the mean RSSI.
5. Record walls, doors and large metal objects between the board and access point.

Do not store or publish other people's network names. Use an anonymous label in your results.

## Code challenge

Filter scan results for the selected SSID, accumulate ten valid readings and print:

```text
samples,mean_rssi,min_rssi,max_rssi
10,-61.4,-68,-57
```

{: .challenge-title}
> Make a signal indicator
>
> Use the ESP32-C6's available LED, an external RGB LED or Serial text bars to show strong, medium and weak signal ranges.
