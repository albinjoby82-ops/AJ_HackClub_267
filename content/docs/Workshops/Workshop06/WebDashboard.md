---
title: Advanced Task 1 - Create a Live Web Dashboard
layout: default
parent: Workshop 06 - ESP32-C6 Wi-Fi Explorer
nav_order: 4
---

# Advanced Task 1 - Create a Live Web Dashboard

Connect the ESP32-C6 to a network you own or have permission to use, then serve the latest survey results as a local webpage.

## Architecture

```text
Wi-Fi scan → store safe summary → HTTP server → browser table
```

## Requirements

- Keep credentials out of screenshots and committed files.
- Show anonymised network labels, RSSI and channel.
- Include the time of the latest scan.
- Escape text before inserting it into HTML.
- Refresh results without blocking the web server.

Use the `WebServer` library supplied with the ESP32 Arduino core. Start with its basic HelloServer example, then add a route such as `/scan`.

{: .challenge-title}
> Add a tiny API
>
> Return the latest results from `/api/networks` as JSON and use browser JavaScript to update the table without reloading the page.
