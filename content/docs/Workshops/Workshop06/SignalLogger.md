---
title: Advanced Task 2 - Design a Roaming Signal Logger
layout: default
parent: Workshop 06 - ESP32-C6 Wi-Fi Explorer
nav_order: 5
---

# Advanced Task 2 - Design a Roaming Signal Logger

Design a portable survey tool that records location labels and signal summaries over time.

## Minimum design

- A button starts a measurement.
- Serial input assigns an anonymous location label.
- Each measurement averages several scans.
- Results are stored as CSV in flash using LittleFS.
- A command prints or clears the saved dataset.

Example:

```text
location,samples,mean_rssi,channel
desk,10,-48.2,6
door,10,-67.9,6
hall,10,-78.4,6
```

## Engineering questions

- How often can you scan without making the interface frustrating?
- How will you recover if power is removed during a write?
- How will you avoid collecting unnecessary network identifiers?
- How will you show that a measurement is still in progress?

{: .challenge-title}
> Make it installation-ready
>
> Add a battery-voltage estimate, status display and downloadable CSV page. Document the privacy choices in your design.
