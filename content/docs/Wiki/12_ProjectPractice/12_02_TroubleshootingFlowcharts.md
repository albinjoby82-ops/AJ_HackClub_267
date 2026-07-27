---
title: Hardware Troubleshooting Flowcharts
layout: default
parent: 8. Project Practice
nav_order: 2
---

# Hardware Troubleshooting Flowcharts

Turn power off before changing wiring. Change one thing at a time.

## It does not power on

```text
Is the source on and correctly set?
├─ No → Set voltage/current limit and enable output
└─ Yes
   Is voltage present at the source terminals?
   ├─ No → Check source, fuse and cable
   └─ Yes
      Is voltage present at the board input?
      ├─ No → Check connector, polarity and continuity
      └─ Yes → Check regulator outputs and shorts
```

## The board will not upload

```text
Does the board appear as a port?
├─ No → Try known data cable, USB port and device list
└─ Yes
   Correct board and port selected?
   ├─ No → Select them
   └─ Yes
      Other program using port?
      ├─ Yes → Close Serial Monitor/scripts
      └─ No → Upload Blink; then check boot/reset procedure
```

## A sensor reads incorrectly

```text
Correct supply and common ground?
├─ No → Fix power/reference
└─ Yes
   Pinout and interface correct?
   ├─ No → Check exact datasheet/module
   └─ Yes
      Raw reading plausible?
      ├─ No → Check range, pull-ups, address and wiring
      └─ Yes → Check conversion, units, calibration and mounting
```

## A motor resets the controller

```text
Motor powered directly from GPIO?
├─ Yes → Use a driver and suitable supply
└─ No
   Supply handles startup/stall current?
   ├─ No → Improve supply and wiring
   └─ Yes
      Grounds joined and noise protection fitted?
      ├─ No → Correct grounding/decoupling/flyback
      └─ Yes → Check mechanical stall and driver temperature
```

## An LED does not light

1. Check current-limiting resistor.
2. Check polarity.
3. Check pin number and `pinMode`.
4. Test the GPIO with a meter or known LED circuit.
5. Check common-anode/common-cathode logic for RGB LEDs.

## Useful evidence

- Expected and measured voltage
- Supply current
- Exact board/module
- Smallest test sketch
- Circuit diagram
- Clear photo
- First useful error message

{: .tip-title}
> Divide the system
>
> Test power, controller, input, output and mechanics separately. The failing boundary is often easier to find than the failing component.
