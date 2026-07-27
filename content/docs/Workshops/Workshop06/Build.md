---
title: Task 1 - Scan Nearby Networks
layout: default
parent: Workshop 06 - ESP32-C6 Wi-Fi Explorer
nav_order: 1
---

# Task 1 - Scan Nearby Networks

## Prepare the board

In Arduino IDE, install the **esp32 by Espressif Systems** board package. Select the ESP32-C6 board that matches your development board, connect its data-capable USB cable and select the new port.

If uploading stalls, hold the board's **BOOT** button, begin the upload and release the button when writing starts.

## Upload the scanner

```cpp
#include <WiFi.h>

void setup() {
  Serial.begin(115200);
  WiFi.mode(WIFI_STA);
  WiFi.disconnect();
  delay(100);
}

void loop() {
  Serial.println("Scanning...");
  int count = WiFi.scanNetworks();

  if (count == 0) {
    Serial.println("No networks found.");
  } else {
    for (int i = 0; i < count; i++) {
      Serial.print(i + 1);
      Serial.print(": ");
      Serial.print(WiFi.SSID(i));
      Serial.print("  RSSI ");
      Serial.print(WiFi.RSSI(i));
      Serial.println(" dBm");
    }
  }

  WiFi.scanDelete();
  Serial.println();
  delay(5000);
}
```

Open the Serial Monitor at `115200` baud. An RSSI value closer to zero generally means a stronger signal: for example, `-45 dBm` is stronger than `-80 dBm`.

## Investigate

- Move the board to three locations and compare the strongest signal.
- Sort or filter the results by signal strength.
- Count how many networks appear on each Wi-Fi channel.
- Print a text bar beside each network without exposing passwords or attempting to connect.
