---
title: Programming Basics
layout: default
parent: 5. Programming
nav_order: 3
---

# Programming
Writing instructions that tell a computer or microcontroller what to do.

## Serial Monitor
A tool in the Arduino IDE that displays messages sent from the microcontroller for debugging or data viewing.
 
## Conditionals:
* if: Evaluates a condition. If the condition is true, the code inside the block is executed.
* else if: Provides additional conditions.
* else: Executes code if no condition is true.

## Function
A block of code that performs a specific task and can be reused.

### pinMode
An Arduino command that sets a pin as an INPUT, OUTPUT, or INPUT_PULLUP.

Example code:
```cpp
void setup()
{
    pinMode(13, OUTPUT);   // Set pin 13 as an output
}
```
### digitalWrite
An Arduino command that sets a digital pin to HIGH or LOW.

Example code:
```cpp
void setup()
{
    pinMode(13, OUTPUT);
}

void loop() 
{
    digitalWrite(13, HIGH);  // Turn LED on
    delay(1000);
    digitalWrite(13, LOW);   // Turn LED off
    delay(1000);
}
```
### Serial.println
Sends data to the Serial Monitor and moves to a new line.

Example code:
```cpp
void setup()
{
    Serial.begin(9600);
    Serial.println("Elec Soc is the best!");
}

void loop()
{
    // code
}
```

### delay
Pauses the program for a specified amount of time (in milliseconds).

Example code:
```cpp
void setup()
{
    pinMode(13, OUTPUT);
}

void loop()
{
    digitalWrite(13, HIGH);  // Turn LED on
    delay(1000); // Wait 1000 milliseconds
    digitalWrite(13, LOW);   // Turn LED off
    delay(1000); // Wait 1000 milliseconds
}
```

### DEBUG Serial.print("______")
A debugging statement that prints text or variable values to help track program behaviour.

Example code:
```cpp
int sensorValue = 300;

void setup()
{
    Serial.begin(9600);
    Serial.print("Sensor value: ");
    Serial.println(sensorValue);
}

void loop()
{
    // code
}
```

## Custom Function
A function created by you to reuse the same code again easily.

Example code:
```cpp
void blinkLED()
{
    digitalWrite(13, HIGH);
    delay(500);
    digitalWrite(13, LOW);
    delay(500);
}

void setup()
{
    pinMode(13, OUTPUT);
}

void loop()
{
    blinkLED();  // Calls the custom function
}
```