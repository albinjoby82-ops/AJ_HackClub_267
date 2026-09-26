// Fake VL53L0X: ranges are ray-cast against the simulated maze walls, with the
// sensor's real continuous-mode timing (a read blocks until the next result).
#pragma once
#include "Arduino.h"

class VL53L0X {
public:
  uint8_t address = 0x29;
  uint32_t budgetUs = 33000;
  double phaseUs = 0, consumedUs = -1;
  bool ranging = false, timedOut = false;

  void setTimeout(uint16_t) {}
  bool init(bool io2v8 = true);
  void setAddress(uint8_t a) { address = a; }
  bool setMeasurementTimingBudget(uint32_t us) { budgetUs = us; return true; }
  void startContinuous(uint32_t period = 0);
  uint16_t readRangeContinuousMillimeters();
  bool timeoutOccurred() { bool t = timedOut; timedOut = false; return t; }
};
