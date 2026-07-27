---
title: Low-Voltage Electrical Safety
layout: default
parent: 1. Safety & Fundamentals
nav_order: 2
---

# Low-Voltage Electrical Safety

Build Club normally works with current-limited, extra-low-voltage circuits powered by USB, batteries or bench supplies. Low voltage reduces shock risk, but short circuits can still cause burns, fire, damaged cells and flying molten metal.

## Safe working rules

1. Turn the output off before changing wiring.
2. Check the supply voltage and polarity before connection.
3. Set a sensible current limit before enabling a bench supply.
4. Keep conductive tools away from energised circuits.
5. Remove rings, watches or metal jewellery when working near batteries or high-current conductors.
6. Never bypass a fuse, protective earth, interlock or current limit.
7. Treat damaged insulation, loose plugs and exposed copper as faults.
8. Do not work with wet hands or in a wet area.

## Before applying power

- Check power and ground are not shorted.
- Confirm polarised parts: electrolytic capacitors, diodes, LEDs, ICs and battery connectors.
- Place ICs, op-amps and microcontrollers across the breadboard's centre gap so opposite pins are not connected together.
- Check the voltage rating of every connected module.
- Make sure motors and servos are powered through suitable drivers or supplies—not directly from GPIO.
- Keep an accessible way to disconnect power.

{: .warning-title}
> Mains electricity is outside the normal club scope
>
> Do not construct, modify or probe exposed mains-voltage circuits. Use approved enclosed adapters and commercially manufactured equipment. Damaged mains equipment must be unplugged, labelled and referred to the responsible technician.

## Stored energy

A circuit may remain dangerous after its supply is removed. Capacitors, inductors, motors and batteries can retain or return energy.

- Use suitable discharge paths where required.
- Verify with an appropriate meter before touching higher-energy circuits.
- Never discharge a capacitor by deliberately shorting it with a screwdriver.
- Do not assume a motor has stopped generating voltage merely because its supply is off.

## If someone receives an electric shock

Do not touch them while they may still be in contact with the source. Isolate the supply if it is safe to do so, raise the alarm and get trained first-aid help. Call the appropriate emergency service for a serious injury.
