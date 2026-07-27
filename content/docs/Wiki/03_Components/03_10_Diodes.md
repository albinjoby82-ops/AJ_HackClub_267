---
title: Diodes
layout: default
parent: 4. Components
nav_order: 10
---

# Diodes

A diode primarily allows current in one direction. The two terminals are the **anode** and **cathode**.

The cathode is commonly marked with a stripe on the component body. On the schematic symbol, the bar marks the cathode.

[Diodes Explained (The Engineering Mindset)](https://youtu.be/Fwj_d3uO5g8)

<iframe width="560" height="315" src="https://www.youtube.com/embed/Fwj_d3uO5g8" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

## Common types

| Type | Typical use |
| --- | --- |
| Rectifier diode | Power rectification and reverse-polarity paths |
| Signal diode | Fast, low-current switching |
| Schottky diode | Lower forward drop and fast switching |
| Zener diode | Voltage reference or clamping in reverse breakdown |
| LED | Producing light |

## Flyback protection

Coils in relays, solenoids, and DC motors can generate a large voltage when switched off. A correctly oriented flyback diode provides a safe current path in DC circuits.

```text
       +V
        |
      [coil]
        |
        +----|<|----+
        |   diode   |
     transistor    +V
```

The diode is normally reverse-biased while the coil is powered.

## Testing

With power disconnected, diode mode should normally show a forward voltage in one direction and open circuit in the other. In-circuit paths can affect the result.

{: .warning}
> Diodes have maximum current, reverse-voltage, power, and switching-speed ratings. “A diode” is not automatically a suitable replacement for another diode.
