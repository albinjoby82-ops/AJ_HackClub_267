---
title: C++ Libraries
layout: default
parent: 5. Programming
nav_order: 4
---

# Libraries

Pre-written code collections that add extra features and simplify programming.

## #include &lt;Servo.h&gt;

Includes the Servo library, which provides built-in functions to control servo motors easily in Arduino programs.

### Servo code

**Setting up a servo**
```cpp
Servo myServo1;
```
Creates a Servo object named myServo1.
This object represents one physical servo motor in the code.

**Next we must tell the Arduino where the servo is attached.**
```cpp
myServo1.attach(9, 500, 2500);
```

Connects the servo to pin 9.
* 500 → minimum pulse width (microseconds)
* 2500 → maximum pulse width (microseconds)

These values help define the servo’s movement range and improve accuracy.

**Using the servo**

```cpp
myServo1.write(0);
```
Moves the servo to 0 degrees.

{: .tip}
  > The value inside the myServo.write() function does not have to be a fixed number, you could give it a variable.


*A full tutorial with all data types, examples, and when to use them will be released soon. Please refer to [docs.arduino.cc](https://docs.arduino.cc/) for general Arduino help*

*Arduino Language Reference Glossary*
----
*Website: docs.arduino.cc*

[https://docs.arduino.cc/language-reference/#variables/](https://docs.arduino.cc/language-reference/#variables))