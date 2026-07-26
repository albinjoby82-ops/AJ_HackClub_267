---
title: Relays and Solenoids
layout: default
parent: 4. Components
nav_order: 18
---

# Relays and Solenoids

Relays and solenoids use an electromagnet to create mechanical movement. A relay changes electrical contacts; a solenoid moves a plunger.

## Relay contacts

Common labels are:

- `COM`: moving common contact
- `NO`: normally open
- `NC`: normally closed

“Normally” describes the unenergised coil state.

## Driving a coil

A GPIO pin normally cannot power a relay or solenoid coil directly. Use:

- A suitable transistor or MOSFET
- A base/gate resistor and default-off resistor as required
- A flyback diode for a DC coil
- A supply sized for the coil current
- Common ground between low-voltage control and driver where required

{: .warning-title}
> Contact isolation does not make every use safe
>
> Relay contacts have voltage, current, load-type, and insulation ratings. This Wiki does not authorise switching mains or hazardous energy. Use supervised, approved equipment and procedures.

## Contact ratings

DC loads can be harder to interrupt than AC loads. Motors and other inductive loads create arcs and transients. Check the rating for the actual voltage, current, and load type.

## Common problems

- Coil voltage is wrong
- Driver current is insufficient
- Flyback diode is backwards or missing
- Contact pins are confused with coil pins
- Supply dips when the coil activates
- Contact bounce creates repeated digital events
