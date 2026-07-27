---
title: Linkages and Degrees of Freedom
layout: default
parent: 7. Engineering Concepts
nav_order: 7
---

# Linkages and Degrees of Freedom

A linkage connects rigid parts with joints to guide motion or transmit force.

- **Revolute joint:** rotates around a pivot
- **Prismatic joint:** slides along a line
- **Fixed joint:** prevents relative movement

A degree of freedom (DOF) is an independent way a mechanism can move. A hinged arm has one rotational DOF. A two-servo planar arm usually has two.

## Mechanical limits

Avoid:

- Links colliding
- Servos reaching hard stops
- Wires being stretched
- Joints folding into unstable positions
- Flexible parts changing the intended geometry

## Prototype with cardboard

1. Cut links with several pivot holes.
2. Join them loosely with paper fasteners.
3. Move the mechanism by hand.
4. Mark collisions and useful travel.
5. Only then attach a servo.

{: .tip}
> Centre a servo before fastening its horn so travel remains available in both directions.
