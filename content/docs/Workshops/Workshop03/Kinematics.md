---
title: Advanced Task 2 - Coordinate Motion with Kinematics
layout: default
parent: Workshop 03 - Servos & Linkages
nav_order: 5
---

# Advanced Task 2 - Coordinate Motion with Kinematics

Instead of choosing two joint angles directly, calculate where the end of the arm should appear.

For a two-link arm with link lengths `L1` and `L2`, shoulder angle `a` and elbow angle `b`:

```text
x = L1 cos(a) + L2 cos(a + b)
y = L1 sin(a) + L2 sin(a + b)
```

Arduino trigonometric functions use **radians**, not degrees.

## Plot the calculated position

Add this function:

```cpp
void printPosition(float shoulderDeg, float elbowDeg) {
  const float L1 = 90.0;
  const float L2 = 75.0;

  float a = radians(shoulderDeg);
  float b = radians(elbowDeg);
  float x = L1 * cos(a) + L2 * cos(a + b);
  float y = L1 * sin(a) + L2 * sin(a + b);

  Serial.print("x:");
  Serial.print(x);
  Serial.print(",y:");
  Serial.println(y);
}
```

Replace `L1` and `L2` with your linkage lengths in millimetres. Move the arm and watch the calculated endpoint in the Serial Monitor.

## Accuracy experiment

1. Draw axes on a sheet of paper beneath the arm.
2. Command five pairs of angles.
3. Mark the physical endpoint.
4. Compare each measured point with the calculated coordinates.
5. Explain errors caused by flexible cardboard, loose pivots, servo offsets and link measurements.

## Advanced challenge: move in a straight line

Create a sequence of target joint angles that makes the endpoint follow an approximately straight path. Plot the calculated points first, then test the physical mechanism slowly.

For a deeper challenge, research **inverse kinematics**: calculating joint angles from a requested `(x, y)` position. Detect positions the arm cannot reach instead of sending invalid angles to the servos.
