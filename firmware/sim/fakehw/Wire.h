// Fake I2C bus: the MPU-6050 gyro is answered from the simulated robot.
#pragma once
#include "Arduino.h"

struct TwoWire {
  bool begin(int sda, int scl);
  void setClock(uint32_t hz);
  void beginTransmission(uint8_t addr);
  size_t write(uint8_t b);
  uint8_t endTransmission(bool stop = true);
  uint8_t requestFrom(int addr, int n);
  int read();
};
extern TwoWire Wire;
