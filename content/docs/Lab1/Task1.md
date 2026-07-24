---
title: Task1 - Simple Traffic Light
layout: default
parent: Lab1 - RGB Controllers
nav_order: 4
---

<!-- EDIT MADE: Added explanations + tips/nuggets + troubleshooting callouts between versions (no changes to code blocks) ✅ -->

# Table of Contents
- [Table of Contents](#table-of-contents)
  - [Traffic Light (v1)](#traffic-light-v1)
  - [Traffic Light (v2)](#traffic-light-v2)
  - [Traffic Light (v3)](#traffic-light-v3)
  - [Traffic Light (v4)](#traffic-light-v4)
  - [Traffic Light (v5)](#traffic-light-v5)

{: .tip-title }
> 🚦 What you’re building
>
> A simple “traffic light” sequence using a **common anode** RGB LED.  
> You’ll then refactor the code step-by-step (like real engineering) 🛠️

{: .tip}
> 💡 **Reminder (common anode logic):** the LED’s common pin is at **+5V**, so a colour usually turns **ON** when its Arduino pin goes **LOW**, and turns **OFF** when the pin goes **HIGH**.

{: .extra}
> 🧠 **Why do multiple versions?**  
> Each version teaches a core habit:
> - v1: basic sequencing ✅  
> - v2: reduce repetition (functions) ♻️  
> - v3: debugging with Serial 🔍  
> - v4: compress data (encoding) 📦  
> - v5: user control (inputs) 🎛️

{: .warning}
> ⏳ **Delays block everything:** `delay()` pauses the entire program. That’s fine for now, but later (sensors/robots) you’ll often switch to `millis()` for non-blocking timing.

----

## Traffic Light (v1)
*We make a simple program that cycles between the colours, like a traffic light!*

{: .tip}
> ✅ **Basics to notice in v1**
> - `pinMode(pin, OUTPUT)` tells the Arduino you want to drive that pin.  
> - You explicitly set each pin HIGH/LOW each time (very clear, but repetitive).  
> - The LED states are “hard-coded” in the loop (works, but scaling gets messy).


----
## Traffic Light (v1)
*We make a simple program that cycles between the colours, like a traffic light!*
```cpp
/*
  Title:              MakerLab1-RGB-Task1
  Organisation:       UCD ElecSoc - MakerLab
  Author(s):          Joe Biju
  Created:            24/09/2025

  Description:
  - Control a Common Anode RGB LED using Serial Monitor.

  Ingredients:
  - Arduino Uno
  - RGB LED with common anode configuration
  - 330Ω resistor
  - Breadboard
  - Jumper cables

  Notes:
  - Use the 5V pin for powering the LEDs
  - Be careful not to get injured on the sharp LED pins!
  - Please use a 330Ω resistor in series with the anode.
  - Since grounding a pin will turn on that colour, logic HIGH in code actually turns OFF an LED.

  Edit History:
  - 
*/

/*Global Declarations*/
const int RED_PIN = 3;
const int GREEN_PIN = 5;
const int BLUE_PIN = 6;

void setup() {
  pinMode(RED_PIN, OUTPUT);
  pinMode(GREEN_PIN, OUTPUT);
  pinMode(BLUE_PIN, OUTPUT);

  // Start with all off
  digitalWrite(RED_PIN, HIGH);
  digitalWrite(GREEN_PIN, HIGH);
  digitalWrite(BLUE_PIN, HIGH);
}

void loop() {
  // Red ON
  digitalWrite(RED_PIN, LOW);
  digitalWrite(GREEN_PIN, HIGH);
  digitalWrite(BLUE_PIN, HIGH);
  delay(3000);

  // Green ON
  digitalWrite(RED_PIN, HIGH);
  digitalWrite(GREEN_PIN, LOW);
  digitalWrite(BLUE_PIN, HIGH);
  delay(2000);

  // Orange (Red + Green)
  digitalWrite(RED_PIN, LOW);
  digitalWrite(GREEN_PIN, LOW);
  digitalWrite(BLUE_PIN, HIGH);
  delay(1000);
}
```

## Traffic Light (v2)
*Now we make a function to do the repetive parts*
{: .Hello!}
> ♻️ **Why we introduce a function (v2):**  
 In v1 you repeat the same three `digitalWrite()` lines every time you change colour.  
 In v2 we wrap that repeated pattern into **one function**, so the loop becomes cleaner and easier to expand later (more colours, more effects) 🛠️

```cpp
/*
  Title:              MakerLab1-RGB-Task1
  Organisation:       UCD ElecSoc - MakerLab
  Author(s):          Joe Biju
  Created:            24/09/2025

  Description:
  - Control a Common Anode RGB LED using Serial Monitor.

  Ingredients:
  - Arduino Uno
  - RGB LED with common anode configuration
  - 330Ω resistor
  - Breadboard
  - Jumper cables

  Notes:
  - Use the 5V pin for powering the LEDs
  - Be careful not to get injured on the sharp LED pins!
  - Please use a 330Ω resistor in series with the anode.
  - Since grounding a pin will turn on that colour, logic HIGH in code actually turns OFF an LED.

  Edit History:
  - Added function to control colours
*/

/*Global Declarations*/
const int RED_PIN = 3;
const int GREEN_PIN = 5;
const int BLUE_PIN = 6;

// Function to control LED states (0 = off, 1 = on)
void setLEDColour(int redValue, int greenValue, int blueValue) {
  // Red control
  if (redValue == 1) {
    digitalWrite(RED_PIN, LOW);   // ON
  } else {
    digitalWrite(RED_PIN, HIGH);  // OFF
  }

  // Green control
  if (greenValue == 1) {
    digitalWrite(GREEN_PIN, LOW);   // ON
  } else {
    digitalWrite(GREEN_PIN, HIGH);  // OFF
  }

  // Blue control
  if (blueValue == 1) {
    digitalWrite(BLUE_PIN, LOW);   // ON
  } else {
    digitalWrite(BLUE_PIN, HIGH);  // OFF
  }
}

void setup() {

  pinMode(RED_PIN, OUTPUT);
  pinMode(GREEN_PIN, OUTPUT);
  pinMode(BLUE_PIN, OUTPUT);

  // All LEDs off at the start
  setLEDColour(0, 0, 0);
}

void loop() {
  // Red for 3 seconds
  setLEDColour(1, 0, 0);
  delay(3000);

  // Green for 2 seconds
  setLEDColour(0, 1, 0);
  delay(2000);

  // Orange (red + green) for 1 second
  setLEDColour(1, 1, 0);
  delay(1000);
}
```


----
## Traffic Light (v3)
*Now we add debug statements to better understand what's happening in the code at any moment.*
*We use Serial Monitor to do this.*
*(This will come in handy when making our Arduino's talk to each other!)*
```cpp
/*
  Title:              MakerLab1-RGB-Task1
  Organisation:       UCD ElecSoc - MakerLab
  Author(s):          Joe Biju
  Created:            24/09/2025

  Description:
  - Control a Common Anode RGB LED using Serial Monitor.

  Ingredients:
  - Arduino Uno
  - RGB LED with common anode configuration
  - 330Ω resistor
  - Breadboard
  - Jumper cables

  Notes:
  - Use the 5V pin for powering the LEDs
  - Be careful not to get injured on the sharp LED pins!
  - Please use a 330Ω resistor in series with the anode.
  - Since grounding a pin will turn on that colour, logic HIGH in code actually turns OFF an LED.

  Edit History:
  - Added function to control colours
  - Added serial monitor for debugging
*/

/*Global Declarations*/
const int RED_PIN = 3;
const int GREEN_PIN = 5;
const int BLUE_PIN = 6;

// Function to control LED states (0 = off, 1 = on)
void setLEDColour(int redValue, int greenValue, int blueValue) {
  // Red control
  if (redValue == 1) {
    digitalWrite(RED_PIN, LOW);   // ON
  } else {
    digitalWrite(RED_PIN, HIGH);  // OFF
  }

  // Green control
  if (greenValue == 1) {
    digitalWrite(GREEN_PIN, LOW);   // ON
  } else {
    digitalWrite(GREEN_PIN, HIGH);  // OFF
  }

  // Blue control
  if (blueValue == 1) {
    digitalWrite(BLUE_PIN, LOW);   // ON
  } else {
    digitalWrite(BLUE_PIN, HIGH);  // OFF
  }
}

void setup() {
  Serial.begin(9600);

  pinMode(RED_PIN, OUTPUT);
  pinMode(GREEN_PIN, OUTPUT);
  pinMode(BLUE_PIN, OUTPUT);

  // All LEDs off at the start
  setLEDColour(0, 0, 0);
  Serial.println("All off");
}

void loop() {
  // Red for 3 seconds
  setLEDColour(1, 0, 0);
  delay(3000);
  Serial.println("Red");

  // Green for 2 seconds
  setLEDColour(0, 1, 0);
  delay(2000);
  Serial.println("Green");

  // Orange (red + green) for 1 second
  setLEDColour(1, 1, 0);
  delay(1000);
  Serial.println("Amber (Orange)");
}
```


----
## Traffic Light (v4)
*Now instead of 3 arguments, we only use one. This saves space!*
*Welcome to embedded engineering :)*
```cpp
/*
  Title:              MakerLab1-RGB-Task1
  Organisation:       UCD ElecSoc - MakerLab
  Author(s):          Joe Biju
  Created:            24/09/2025

  Description:
  - Control a Common Anode RGB LED using Serial Monitor.

  Ingredients:
  - Arduino Uno
  - RGB LED with common anode configuration
  - 330Ω resistor
  - Breadboard
  - Jumper cables

  Notes:
  - Use the 5V pin for powering the LEDs
  - Be careful not to get injured on the sharp LED pins!
  - Please use a 330Ω resistor in series with the anode.
  - Since grounding a pin will turn on that colour, logic HIGH in code actually turns OFF an LED.

  Edit History:
  - Added function to control colours
  - Added serial monitor for debugging
  - Changed function to use 1 argument instead of 3
*/

/*Global Declarations*/
const int RED_PIN = 3;
const int GREEN_PIN = 5;
const int BLUE_PIN = 6;

// Function to control LED states using a 3-digit number (e.g. 101 = Red ON, Green OFF, Blue ON)
void setLEDColour(int colourCode) {
  int blueValue  = colourCode % 10;          // last digit
  int greenValue = (colourCode / 10) % 10;   // middle digit
  int redValue   = (colourCode / 100) % 10;  // first digit

  // Red control
  if (redValue == 1) {
    digitalWrite(RED_PIN, LOW);   // ON
  } else {
    digitalWrite(RED_PIN, HIGH);  // OFF
  }

  // Green control
  if (greenValue == 1) {
    digitalWrite(GREEN_PIN, LOW);   // ON
  } else {
    digitalWrite(GREEN_PIN, HIGH);  // OFF
  }

  // Blue control
  if (blueValue == 1) {
    digitalWrite(BLUE_PIN, LOW);   // ON
  } else {
    digitalWrite(BLUE_PIN, HIGH);  // OFF
  }
}


void setup() {
  Serial.begin(9600);

  pinMode(RED_PIN, OUTPUT);
  pinMode(GREEN_PIN, OUTPUT);
  pinMode(BLUE_PIN, OUTPUT);

  // All LEDs off at the start
  setLEDColour(0, 0, 0);
  Serial.println("All off");

}
void loop() {
  setLEDColour(100); // Red
  delay(3000);
  Serial.println("Red (100)");

  setLEDColour(10); // Green (Q: why did we not use "010"?)
  delay(2000);
  Serial.println("Green (10)");

  setLEDColour(110); // Orange (Red + Green)
  delay(1000);
  Serial.println("Orange (110)");
}

```
----
## Traffic Light (v5)
*Finally, let's give the user control! Now, we'll type and set what colour we want*
*through the Serial Monitor*
```cpp
/*
  Title:              MakerLab1-RGB-Task1
  Organisation:       UCD ElecSoc - MakerLab
  Author(s):          Joe Biju
  Created:            24/09/2025

  Description:
  - Control a Common Anode RGB LED using Serial Monitor.

  Ingredients:
  - Arduino Uno
  - RGB LED with common anode configuration
  - 330Ω resistor
  - Breadboard
  - Jumper cables

  Notes:
  - Use the 5V pin for powering the LEDs
  - Be careful not to get injured on the sharp LED pins!
  - Please use a 330Ω resistor in series with the anode.
  - Since grounding a pin will turn on that colour, logic HIGH in code actually turns OFF an LED.

  Edit History:
  - Added function to control colours
  - Added serial monitor for debugging
  - Changed function to use 1 argument instead of 3
  - Removed traffic light sequence. Added ability for user to set colour
  - Added "DEBUG" preprocessor directive
*/
/*Global Declarations*/
#define DEBUG
// #define DEBUG if(false)
const int RED_PIN   = 3;
const int GREEN_PIN = 5;
const int BLUE_PIN  = 6;

// Function to control LED states using a 3-digit number (e.g. 101 = Red ON, Green OFF, Blue ON)
void setLEDColour(int colourCode) {
  int blueValue  = colourCode % 10;          // last digit
  int greenValue = (colourCode / 10) % 10;   // middle digit
  int redValue   = (colourCode / 100);  // first digit
  DEBUG Serial.print("blueValue="); Serial.println(blueValue);
  DEBUG Serial.print("greenValue="); Serial.println(greenValue);
  DEBUG Serial.print("redValue="); Serial.println(redValue);

  // Red control
  if (redValue == 1) {
    digitalWrite(RED_PIN, LOW);   // ON
  } else {
    digitalWrite(RED_PIN, HIGH);  // OFF
  }

  // Green control
  if (greenValue == 1) {
    digitalWrite(GREEN_PIN, LOW);   // ON
  } else {
    digitalWrite(GREEN_PIN, HIGH);  // OFF
  }

  // Blue control
  if (blueValue == 1) {
    digitalWrite(BLUE_PIN, LOW);   // ON
  } else {
    digitalWrite(BLUE_PIN, HIGH);  // OFF
  }
}

void setup() {
  Serial.begin(9600);

  pinMode(RED_PIN, OUTPUT);
  pinMode(GREEN_PIN, OUTPUT);
  pinMode(BLUE_PIN, OUTPUT);

  // All LEDs off at the start
  setLEDColour(0);
  Serial.println("All off");
  Serial.println("Type a 3-digit number (RGB) to set the LED colour, e.g. 101 for Red + Blue");
}

void loop() {
  // Check if data is available in Serial Monitor
  if (Serial.available() > 0) {
    int colourCode = Serial.parseInt();  // Read the typed number
    setLEDColour(colourCode);

    Serial.print("LED set to: ");
    Serial.println(colourCode);

    // Optional: small delay to avoid repeated reads of the same number
    delay(200);
  }
}
```
