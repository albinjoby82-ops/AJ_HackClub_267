<!-- ---
title: Modulus
layout: default
parent: MakerLabs Wiki
nav_order: 21
--- -->
# % (Modulus)
Returns the remainder after division.

Example code:
```cpp
int x = 10;
int answer;

void setup()
{
  Serial.begin(9600);   // Start Serial Monitor

  answer = x % 3;       // Modulus operation
  Serial.print(answer); // Print result
}

void loop()
{
  
}
```
Answer will be 1, because 10 divided by 3 is 3 remainder 1.
