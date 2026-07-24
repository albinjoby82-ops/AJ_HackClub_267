---
title: Task-0
layout: default
parent: Lab1 - RGB Controllers
nav_order: 3
---

<!-- EDIT MADE: Added tips/nuggets + troubleshooting callouts (common anode, PWM pins, resistors, COM-port tips, etc.) ✅ -->

# Setting up the circuit
But first, we gotta get basic.

## Ingredients:
  - Arduino Uno
  - RGB LED with common anode configuration
  - 330Ω resistor
  - Breadboard
  - Jumper cables

{: .tip}
> 💡 **Resistor choice (330Ω isn’t magic):** 330Ω is a safe, common value for Arduino LED work.  
> Lower resistance = brighter (more current), higher resistance = dimmer (safer).  
> Also, different colours won’t be equally bright even with the same resistor.

{: .warning}
> ⚠️ **Arduino pin safety:** Arduino pins are not power supplies. Always use resistors with LEDs and never try to drive high-current loads directly from I/O pins.

## Circuit
- 5V of Arduino Uno to the resistor
- Connect the other end of resistor to common anode of LED
- Connect the other pins of the LED to the Arduino digital pins
  - RED -> `pin 3`
  - GREEN -> `pin 5`
  - BLUE -> `pin 6`


{: .extra}
> 🎯 **Why pins 3, 5, 6?** These are **PWM-capable** on the Uno, which lets you smoothly control brightness later (instead of just ON/OFF).

{: .tip}
> 🏷️ **Wire-labelling saves you:** keep track of which jumper is R / G / B. The #1 beginner bug is “wrong colour” caused by swapped LED legs.


{: .note}
> ✅ **Resistor placement note:** one resistor on the common anode limits the **total** current.  
> Best practice is **one resistor per colour** (R, G, B) for more consistent brightness and protection.

## Arduino IDE
You can use:
- Lab computers
- Arduino Cloud
- Install Arduino IDE on your laptop

{: .tip}
> 🛠️ In Arduino IDE, always verify you are using the correct COM Port (There is no majic trick, try them all until the uno flashes)

{: .troubleshooting}
> 🔌 **COM port not showing?**  
> - Try a different USB port  
> - Make sure your cable is **data-capable** (some are charge-only)  
> - You can always ask us!

## Test your Arduino is working
- Go to `File` > `Examples` > `01.Basic` > `Blink`
- Select the correct COM Port
- Upload the file to your arduino

You should see the onboard LED blinking. 
*(If not, please let one of the robotics officers know)*
