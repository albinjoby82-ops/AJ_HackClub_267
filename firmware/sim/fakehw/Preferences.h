// Fake ESP32 Preferences (flash key/value store), kept in memory.
#pragma once
#include "Arduino.h"
#include <map>

struct PrefValue { std::string s; int32_t i = 0; float f = 0; bool b = false; };
extern std::map<std::string, std::map<std::string, PrefValue>> g_prefs;

class Preferences {
  std::string ns;
public:
  bool begin(const char *name, bool readOnly = false) {
    ns = name;
    return !readOnly || g_prefs.count(ns);
  }
  void end() {}
  bool has(const char *k) { return g_prefs.count(ns) && g_prefs[ns].count(k); }
  size_t putString(const char *k, const char *v) { g_prefs[ns][k].s = v; return strlen(v); }
  size_t putInt(const char *k, int32_t v) { g_prefs[ns][k].i = v; return 4; }
  size_t putFloat(const char *k, float v) { g_prefs[ns][k].f = v; return 4; }
  size_t putBool(const char *k, bool v) { g_prefs[ns][k].b = v; return 1; }
  String getString(const char *k, String d = String()) { return has(k) ? String(g_prefs[ns][k].s.c_str()) : d; }
  int32_t getInt(const char *k, int32_t d = 0) { return has(k) ? g_prefs[ns][k].i : d; }
  float getFloat(const char *k, float d = 0) { return has(k) ? g_prefs[ns][k].f : d; }
  bool getBool(const char *k, bool d = false) { return has(k) ? g_prefs[ns][k].b : d; }
};
