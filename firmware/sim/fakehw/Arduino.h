// Fake Arduino core for the robot simulator: just enough of the ESP32 Arduino
// API for mouse_map.ino to compile unchanged. The functions are implemented in
// robot_sim.cpp on top of a physics model.
#pragma once
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cmath>
#include <cstdarg>
#include <string>
#include <algorithm>
using std::min;
using std::max;

#define IRAM_ATTR
#ifndef PI
#define PI 3.1415926535897932384626433832795
#endif
#define HIGH 1
#define LOW 0
#define INPUT 0
#define OUTPUT 1
#define INPUT_PULLUP 2
#define CHANGE 3
#define F(x) (x)
#define constrain(amt, low, high) ((amt) < (low) ? (low) : ((amt) > (high) ? (high) : (amt)))

// Names the real esp32c6 variant defines, so a clash fails here too.
#define PIN_RGB_LED 8
#define RGB_BUILTIN (30 + PIN_RGB_LED)
#define LED_BUILTIN RGB_BUILTIN
#define BUILTIN_LED LED_BUILTIN
#define RGB_BRIGHTNESS 64
static const uint8_t TX = 16, RX = 17, SDA = 23, SCL = 22, SS = 18, MOSI = 19, MISO = 20, SCK = 21;

struct String {
  std::string s;
  String() {}
  String(const char *c) : s(c ? c : "") {}
  size_t length() const { return s.size(); }
  const char *c_str() const { return s.c_str(); }
};

struct SimSerial {
  void begin(long) {}
  int available();
  int read();
  void print(const char *s);
  void print(const String &s) { print(s.c_str()); }
  void println(const char *s = "") { print(s); print("\n"); }
  int printf(const char *fmt, ...);
};
extern SimSerial Serial;

void delay(unsigned long ms);
unsigned long millis();
unsigned long micros();
void pinMode(int pin, int mode);
void digitalWrite(int pin, int val);
int digitalRead(int pin);
bool ledcAttach(int pin, int freq, int bits);
bool ledcWrite(int pin, uint32_t duty);
inline int digitalPinToInterrupt(int p) { return p; }
void attachInterrupt(int pin, void (*fn)(), int mode);
inline void rgbLedWrite(uint8_t, uint8_t, uint8_t, uint8_t) {}
typedef void (*TaskFunction_t)(void *);
inline int xTaskCreate(TaskFunction_t, const char *, uint32_t, void *, unsigned, void *) { return 1; }
inline void vTaskDelay(uint32_t ms) { delay(ms); }
#define pdMS_TO_TICKS(x) (x)
