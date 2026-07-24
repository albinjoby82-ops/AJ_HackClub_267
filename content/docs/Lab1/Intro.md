---
title: Intro
layout: default
parent: Lab1 - RGB Controllers
nav_order: 1
---

# Introduction

Welcome to the first MakerLab! In this lab, we'll be
- working with **Arduino** microcontrollers
- wiring simple **circuits**
- using **PWM** to control colour
- using **Serial** to send messages via UART

By the end, you'll learn everything it takes to build an actual **RGB strip** in real-life


----
# Prologue
Have you ever wondered how an RGB strip works? Those Phillips ones can [cost €50<](https://www.amazon.co.uk/Philips-Lightstrip-Ambiance-Bluetooth-Assistant/dp/B088RX9CSZ/ref=sr_1_1?dib=eyJ2IjoiMSJ9.8CTtQPJJCYCT3zuBS7E-L4LCifk0r0okcTMA5WwUF-EBmLcrrh2nhM0hfuvEK0NylAAuMZOiQ9T-GdsKoTpLA6LpenLxdHPRmeYmM-T-jaNvHfd2cSz7wtYN74sJt8lM6PPfneX5mUk5lPRn3w9hYGP8lkrsnq3yY7u75OZ-5sRc5nfs5NrIz_AHHEaIe1A1f6rq7_KXlJPHFT1e9UNVhTTTQhDA0Me0TDvkWjBTJUFZ2PuojTean1jiaXfAszXk5bDOaH5r4E846-s8LpobQJotUWBcDUUKcdclb9E5QnY.JC7seYiOVlcS7_AcAFf9J1trV79l3baOOaWOpW-Z3SU&dib_tag=se&keywords=philips%2Bhue%2Blight%2Bstrip&qid=1758718699&sr=8-1&th=1) for just 2m, 
when I bought a 5m one that's also waterproof, for *half* the [price](https://www.amazon.co.uk/BTF-LIGHTING-Individual-Addressable-300Pixels-Non-Waterproof/dp/B088BDLMH2/ref=sr_1_3_sspa?dib=eyJ2IjoiMSJ9.-RKkIXaeka4TEp7slay4Ul_9gjsTlDBMxy1hO2AQTX6DiEOwiQgZstSpOIVkTwKkvArUsxfVZ779nNtd2jDnOEKBaUXGLdbZAtINF5-WW3jou8M8IEowCzSeX6kWQf34EO5Z9gpew98ZQUXz83o5uC7-M54A2lWzOKl2HpkDtWl91NtShB4c1VmmnIsSMhqyR4CRXiHOcVudecrohQF4czofD2llQXZhaxqph5jttkh4CQqHrn_7o0HM-Uo0d9U6376fmaLdZkrfZ0CCZ-hQVZ6qiE_aB_yIK-lFBUVuGmY.d4W5N6_gCiQpUlDZPU_UEpZvj_aQdLQfNm8HFZ01FKI&dib_tag=se&keywords=Addressable%2BLED&qid=1750197634&sr=8-3-spons&sp_csd=d2lkZ2V0TmFtZT1zcF9hdGY&th=1) (probably there are even cheaper ones if not purchasing from Amazon)
![Expensive vs Cheap LED strips](https://i.ytimg.com/vi/CojuVyJF0JM/maxresdefault.jpg)

And what are in them? How can I just cut them to whatever length I want? Or even extend them?

And if each LED has 3 colours, does that a 5m strip with 60 LEDs/m has
5\*60\*3=**900 wires** connecting to the controller? 😱

![How do addressable LEDs work](https://content.instructables.com/FUB/HOYI/HZ9O2X6L/FUBHOYIHZ9O2X6L.jpg)
Well my friends, the solution is all thanks to the **addressable LEDs** (in my case, the WS2812 LED chip).

And this lab will teach you all about *how it works*.

And for those who manage to get a full pseudo-RGB strip working, I'll have a prize :)
