---
title: Common Errors
layout: default
parent: 5. Programming
nav_order: 0
---

# Board Errors

## ❌ Arduino Not Detected by Computer
### Symptoms
*	“Port not found”
*	No COM port appears in Tools → Port
*	Upload button does nothing
### Possible causes
*	Port not selected correctly
*	Board not selected correctly
### How to Fix
1.	Go to:
*	Tools → Board → Arduino Uno
*	Tools → Port → select the COM port
 
2.	Try a different USB cable
3.	Restart the Arduino IDE

## ❌ Wrong Board Selected
### Symptoms
*	Upload fails with mysterious errors
*	Code worked on another board but not this one
### Possible causes
*	Arduino IDE defaults to the wrong board (e.g., Nano, Mega)
### How to Fix
*	In the Arduino IDE:
*	Tools → Board → Arduino Uno

# Syntax Errors (Code Won’t Compile)
## ❌ Missing Semicolon (;)
### Symptoms
*	Red error messages
*	Errors point to lines that look correct
### Example Error
```cpp
int ledPin = 13
```
### Fix
Add a semicolon:
```cpp
int ledPin = 13;
```
Every Arduino instruction ends with a semicolon.

## ❌ Misspelled Keywords
### Symptoms
*	Error: 'lodop' was not declared in this scope
### Possible causes
*	Arduino is case-sensitive
*	Typing mistakes
### Example
```cpp
digitalwrite(13, HIGH);
```
### Fix
Correct capitalization:
```cpp
digitalWrite(13, HIGH);
```

## ❌ Missing or Extra Braces { }
### Symptoms
*	Error: expected '}' at end of input
*	Code compiles halfway
### Why It Happens
*	setup() or loop() not closed properly
### Fix
Ensure matching braces:

```cpp
void setup()
{
    // code
}

void loop()
{
    // code
}
```


## ❌ Using = Instead of ==
### Symptoms
*	if statements always run or never run
### Example
```cpp
if (buttonState = HIGH)
```
### Possible causes
*	= assigns a value
*	== compares values
### Fix
```cpp
if (buttonState == HIGH)
```

## ❌ Forgetting pinMode()
### Symptoms
*	LED doesn’t turn on
*	Button gives random values
### Possible causes
*	Arduino pins default to INPUT
### Fix
In setup():
```cpp
pinMode(13, OUTPUT);
pinMode(2, INPUT);
```

## ❌ Wrong Pin Number
### Symptoms
*	LED or sensor doesn’t respond
### Possible causes
*	Code uses a pin, but wire is connected to a different pin
### Fix
*	Double-check wiring
*	Match code pin numbers to physical pins

## ❌ Problems with Serial Monitor
### Symptoms
*	Serial Monitor shows gibberish
### Possible causes
*	Serial Monitor speed doesn’t match code
### Fix
Ensure both match:
```cpp
Serial.begin(9600);
```
Set Serial Monitor to 9600 baud

## ❌ Serial Monitor Not Open
### Symptoms
*	Nothing prints
### Fix
*	Click Tools → Serial Monitor
*	Or press Ctrl + Shift + M

## ❌ LED Wired Backwards
### Symptoms
*	LED doesn’t light up
### Possible causes
*	LEDs are polarized
### Fix
*	Long leg → positive (pin)
*	Short leg → GND (Ground)

## ❌ LED not working
### Symptoms
*	LED burns out
*	Arduino resets randomly
### Fix
1.	Add a 220Ω–330Ω resistor in series with LED
2.	Try a different LED with a resistor in series

## ❌ Button Issues
### Symptoms
*	Button reads random HIGH/LOW
### Possible causes
*	Input pin is not pulled up or down
### Fix
Use internal pull-up:
```cpp
pinMode(buttonPin, INPUT_PULLUP);
```

## ❌ Board Powered But Not Running Code
### Symptoms
*	Power LED is on
*	Nothing else works
### Fix
*	Re-upload sketch
*	Check setup() runs (add a test LED blink)

## ❌ Putting Code Outside loop() or setup()
### Symptoms
*	Compile errors
### Fix
All executable code must be inside:
```cpp
void setup() { }
void loop() { }
```

## ❌ Code only supposed to Run Once
### Symptoms
*	Unexpected repeated behavior
### Possible causes
*	loop() runs forever
*   while() or for() runs forever
### Fix
*	setup() → runs once
*	loop() → repeats endlessly
*   Check conditions inside for() or while() loops are correct