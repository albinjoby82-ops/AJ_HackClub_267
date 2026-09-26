/*
 * ============================================================================
 *  CALIBRATE - the mouse learns how IT moves, then locks it in
 * ============================================================================
 *
 *  Drives forward one square, reverses back, turns left 90 and right 90 -
 *  over and over. After every round it measures its own mistakes and corrects
 *  them. When two rounds in a row are within tolerance it saves everything to
 *  flash ("LOCKED IN"). mouse_map loads the saved values automatically at boot.
 *
 *  What it learns:
 *    - gyro direction   (backwards = turns spin out, and "hold straight"
 *                        steers INTO the wall instead of away from it)
 *    - each motor's minimum PWM that actually moves it
 *    - per-wheel trim (forward and reverse) so equal commands = equal speed
 *    - how far it coasts after the motors cut, so it stops exactly 1 square on
 *    - how far it over-rotates after a turn, so it lands on exactly 90 degrees
 *
 *  Runs cable-free on battery:
 *    1. Flash this, unplug USB, power it from the battery.
 *    2. Put it on the maze floor with ~30 cm clear in front AND behind.
 *    3. Press the BOOT button on the board and let go. Hands off.
 *    4. Wait for the onboard LED:
 *         dim white      ready - waiting for the BOOT button
 *         blue flashing  running (the first ~5 s is the gyro calibrating)
 *         green          LOCKED IN - saved
 *         yellow         saved, but not fully settled - run it again
 *         red flashing   stopped with an error
 *    5. Plug in USB and open Serial Monitor at 115200. It prints the full log
 *       of the last run (saved in flash) plus the learned values. If nothing
 *       shows, send 'p'.
 *  It never starts moving by itself, so plugging in USB (which can reset the
 *  board) is safe. Press BOOT or send 'r' to run again from what it learned.
 *
 *  The motion constants below MUST match mouse_map - that's what it learns for.
 * ============================================================================
 */

#include <Wire.h>
#include <VL53L0X.h>
#include <Preferences.h>
#include <stdarg.h>

// ---- Pins (same as every other sketch) -------------------------------------
const int PIN_SDA = 6, PIN_SCL = 7;
const int XSHUT[3] = { 18, 19, 20 };            // left, front, right
const int PIN_L_DIR = 0, PIN_L_PWM = 2;
const int PIN_R_DIR = 3, PIN_R_PWM = 10;
const int L_DIR_SIGN = +1, R_DIR_SIGN = -1;
const int PIN_L_ENC_A = 21, PIN_L_ENC_B = 22;
const int PIN_R_ENC_A = 23, PIN_R_ENC_B = 11;
const int STATUS_RGB_PIN = 8;                      // onboard RGB LED (DevKitC-1)
const int PIN_BOOT_BTN = 9;                     // onboard BOOT button, LOW when pressed

// ---- Motion constants: MUST match mouse_map --------------------------------
const int   PWM_FREQ_HZ = 20000, PWM_BITS = 8, PWM_MAX = 255;
const int   CRUISE_PWM = 90, TURN_PWM = 85;
const float CELL_MM = 180.0, WHEEL_DIAMETER_MM = 44.0, ENC_TICKS_PER_REV = 402.0;
const float MM_PER_TICK = (PI * WHEEL_DIAMETER_MM) / ENC_TICKS_PER_REV;
const long  TICKS_PER_CELL = (long)(CELL_MM / MM_PER_TICK + 0.5);
const float KP_HEAD = 3.0, KD_HEAD = 0.4, KP_ENC = 0.5;
const int   CORR_MAX = 55;
const float TURN_SLOW_ZONE_DEG = 25.0;
const unsigned long TURN_TIMEOUT_MS = 3000;
const float TURN_STALL_DPS = 15.0;             // rotating slower than this = stalled
const unsigned long TURN_STALL_MS = 120;
const int   TURN_BOOST_STEP = 6, TURN_BOOST_MAX = 90;

// ---- IMU -------------------------------------------------------------------
const uint8_t MPU_ADDR = 0x68, MPU_PWR_MGMT_1 = 0x6B, MPU_GYRO_CONFIG = 0x1B, MPU_GYRO_ZOUT_H = 0x47;
const float   GYRO_LSB_PER_DPS = 32.8;          // +-1000 dps range, so a fast spin can't clip
const int     GYRO_CAL_SAMPLES = 800;

// ---- Learning --------------------------------------------------------------
const int   MAX_ROUNDS = 10, GOOD_ROUNDS_TO_LOCK = 2;
const float LEARN_RATE = 0.7;                   // fraction of each error corrected per round
// Tolerances are what the maze needs, not perfection: mouse_map re-centres
// between walls and lines up on the wall ahead every square.
const float TURN_TOL_DEG = 2.5;
const long  DIST_TOL_TICKS = 30;                // ~10 mm
const float TRIM_TOL_PWM = 5.0;
const int   FRONT_ABORT_MM = 50;
const unsigned long START_DELAY_MS = 3000;      // time to take your hand away

// ---- What gets learned (and saved) -----------------------------------------
int   gyroSign = +1;
int   minPwmL = 45, minPwmR = 45;
float trimLF = 1.0, trimRF = 1.0, trimLR = 1.0, trimRR = 1.0;   // L/R x Fwd/Rev
float stopLeadFwd = 0.0, stopLeadRev = 0.0;                     // ticks
float turnLeadL = 2.0, turnLeadR = 2.0;                         // degrees

// ---- State -----------------------------------------------------------------
// Types used in function signatures must be defined before any function: the
// Arduino IDE auto-inserts function prototypes above the first function.
struct Run { long travelled; float avgCorr; float endHeading; bool aborted; };
enum LedMode { LED_READY, LED_RUNNING, LED_DONE, LED_UNSETTLED, LED_ERROR };

VL53L0X front;
volatile long countL = 0, countR = 0;
int encSignL = +1, encSignR = +1;               // learned in the spin test
float gyroBiasRaw = 0, gyroAngle = 0, lastGyroZ = 0;
unsigned long lastGyroUs = 0;
int gyroPeakRaw = 0;
volatile LedMode ledMode = LED_READY;

// Everything printed during a run is also kept here and saved to flash, so it
// can be read after the run with the cable plugged back in.
char   logBuf[3900];                             // flash strings max out at 4000 bytes
size_t logLen = 0;
bool   logFull = false;

void IRAM_ATTR isrLeft()  { if (digitalRead(PIN_L_ENC_A) == digitalRead(PIN_L_ENC_B)) countL++; else countL--; }
void IRAM_ATTR isrRight() { if (digitalRead(PIN_R_ENC_A) == digitalRead(PIN_R_ENC_B)) countR++; else countR--; }
long tL() { return encSignL * countL; }         // + = that wheel rolled forward
long tR() { return encSignR * countR; }

// ============================================================================
//  LOG + LED
// ============================================================================
void report(const char *fmt, ...) {
  char line[192];
  va_list ap; va_start(ap, fmt);
  int n = vsnprintf(line, sizeof(line), fmt, ap);
  va_end(ap);
  Serial.print(line);
  if (n <= 0) return;
  size_t k = min((size_t)n, sizeof(line) - 1);
  const char *full = "\n...(log full - learned values are still saved)\n";
  if (logLen + k + strlen(full) < sizeof(logBuf)) {
    memcpy(logBuf + logLen, line, k); logLen += k; logBuf[logLen] = 0;
  } else if (!logFull) {
    logFull = true;
    strcpy(logBuf + logLen, full); logLen += strlen(full);
  }
}
void clearLog() { logLen = 0; logBuf[0] = 0; logFull = false; }
void saveLog() {
  Preferences p;
  p.begin("mousecal", false);
  p.putString("log", logBuf);
  p.end();
}

void ledTask(void *) {
  bool on = false;
  while (true) {
    on = !on;
    switch (ledMode) {
      case LED_READY:     rgbLedWrite(STATUS_RGB_PIN, 6, 6, 6);            break;
      case LED_RUNNING:   rgbLedWrite(STATUS_RGB_PIN, 0, 0, on ? 60 : 0);  break;
      case LED_DONE:      rgbLedWrite(STATUS_RGB_PIN, 0, 60, 0);           break;
      case LED_UNSETTLED: rgbLedWrite(STATUS_RGB_PIN, 60, 35, 0);          break;
      case LED_ERROR:     rgbLedWrite(STATUS_RGB_PIN, on ? 60 : 0, 0, 0);  break;
    }
    vTaskDelay(pdMS_TO_TICKS(ledMode == LED_ERROR ? 150 : 300));
  }
}

// ============================================================================
//  MOTORS
// ============================================================================
void motorWrite(int dirPin, int pwmPin, int dirSign, int spd, int minPwm, float trimF, float trimB) {
  if (spd == 0) { ledcWrite(pwmPin, 0); return; }
  int mag = (int)(abs(spd) * (spd > 0 ? trimF : trimB) + 0.5f);
  if (mag > PWM_MAX) mag = PWM_MAX;
  if (mag < minPwm)  mag = minPwm;
  digitalWrite(dirPin, (spd * dirSign) > 0 ? HIGH : LOW);
  ledcWrite(pwmPin, mag);
}
void setMotors(int l, int r) {             // learned min PWM + trim applied
  motorWrite(PIN_L_DIR, PIN_L_PWM, L_DIR_SIGN, l, minPwmL, trimLF, trimLR);
  motorWrite(PIN_R_DIR, PIN_R_PWM, R_DIR_SIGN, r, minPwmR, trimRF, trimRR);
}
void rawMotors(int l, int r) {             // exact PWM, nothing applied
  motorWrite(PIN_L_DIR, PIN_L_PWM, L_DIR_SIGN, l, 0, 1.0f, 1.0f);
  motorWrite(PIN_R_DIR, PIN_R_PWM, R_DIR_SIGN, r, 0, 1.0f, 1.0f);
}
void stopMotors() { ledcWrite(PIN_L_PWM, 0); ledcWrite(PIN_R_PWM, 0); }

void halt(const char *why) {
  stopMotors();
  report("\nHALT: %s\n", why);
  saveLog();
  ledMode = LED_ERROR;
  while (true) delay(1000);
}

// ============================================================================
//  GYRO  (+ angle = counter-clockwise = left)
// ============================================================================
bool mpuWrite(uint8_t reg, uint8_t val) {
  Wire.beginTransmission(MPU_ADDR); Wire.write(reg); Wire.write(val);
  return Wire.endTransmission() == 0;
}
bool readGyroRaw(int16_t &raw) {
  Wire.beginTransmission(MPU_ADDR); Wire.write(MPU_GYRO_ZOUT_H);
  if (Wire.endTransmission(false) != 0) return false;
  if (Wire.requestFrom((int)MPU_ADDR, 2) != 2) return false;
  uint8_t hi = Wire.read(), lo = Wire.read();   // separate reads: C++ may evaluate a()<<8 | a() either way round
  raw = (int16_t)((hi << 8) | lo);
  return true;
}
float readGyroZ() {
  int16_t raw;
  if (!readGyroRaw(raw)) return 0.0;
  if (abs(raw) > gyroPeakRaw) gyroPeakRaw = abs(raw);
  return gyroSign * (raw / GYRO_LSB_PER_DPS - gyroBiasRaw);
}
void resetGyro() { gyroAngle = 0.0; lastGyroZ = 0.0; lastGyroUs = micros(); }
void updateGyro() {
  unsigned long now = micros();
  float dt = (now - lastGyroUs) * 1e-6f; lastGyroUs = now;
  if (dt <= 0 || dt > 0.2f) return;
  lastGyroZ = readGyroZ();
  gyroAngle += lastGyroZ * dt;
}
void calibrateGyro() {
  double sum = 0; int n = 0; int16_t raw;
  for (int i = 0; i < GYRO_CAL_SAMPLES; i++) {
    if (readGyroRaw(raw)) { sum += raw / GYRO_LSB_PER_DPS; n++; }
    delay(2);
  }
  if (n < GYRO_CAL_SAMPLES / 2) halt("IMU reads keep failing - check its SDA/SCL/VCC/GND");
  gyroBiasRaw = (float)(sum / n);
  report("Gyro bias = %.3f dps\n", gyroBiasRaw);
}

// Wait until both wheels have stopped, integrating the gyro the whole time so
// the coast after the motors cut is counted.
void settle() {
  long lL = countL, lR = countR;
  unsigned long t0 = millis(), still = millis();
  while (millis() - t0 < 1000) {
    updateGyro(); delay(3);
    if (countL != lL || countR != lR) { lL = countL; lR = countR; still = millis(); }
    else if (millis() - still > 150) break;
  }
}

// ============================================================================
//  FRONT SENSOR (safety stop only)
// ============================================================================
void startFront() {
  for (int i = 0; i < 3; i++) { pinMode(XSHUT[i], OUTPUT); digitalWrite(XSHUT[i], LOW); }
  delay(20);
  digitalWrite(XSHUT[1], HIGH); delay(50);
  front.setTimeout(200);
  if (!front.init()) halt("FRONT VL53L0X init failed - it's the safety stop, won't drive without it");
  front.setMeasurementTimingBudget(33000);
  front.startContinuous();
}
int readFront() {
  uint16_t r = front.readRangeContinuousMillimeters();
  if (front.timeoutOccurred() || r == 0 || r > 1200) return 1200;
  return (int)r;
}

// ============================================================================
//  CALIBRATION STORAGE
// ============================================================================
void printCal() {
  report("  gyro sign %+d | min PWM  L %d  R %d\n", gyroSign, minPwmL, minPwmR);
  report("  trim fwd  L %.3f  R %.3f | trim rev  L %.3f  R %.3f\n", trimLF, trimRF, trimLR, trimRR);
  report("  stop lead fwd %.0f  rev %.0f ticks | turn lead L %.1f  R %.1f deg\n",
       stopLeadFwd, stopLeadRev, turnLeadL, turnLeadR);
}
bool loadCal() {
  Preferences p;
  if (!p.begin("mousecal", true)) return false;
  bool ok = p.getBool("ok", false);
  if (ok) {
    gyroSign = p.getInt("gyroSign", gyroSign);
    minPwmL = p.getInt("minL", minPwmL);        minPwmR = p.getInt("minR", minPwmR);
    trimLF = p.getFloat("trimLF", trimLF);      trimRF = p.getFloat("trimRF", trimRF);
    trimLR = p.getFloat("trimLR", trimLR);      trimRR = p.getFloat("trimRR", trimRR);
    stopLeadFwd = p.getFloat("leadF", stopLeadFwd); stopLeadRev = p.getFloat("leadR", stopLeadRev);
    turnLeadL = p.getFloat("turnL", turnLeadL); turnLeadR = p.getFloat("turnR", turnLeadR);
  }
  p.end();
  return ok;
}
void saveCal() {
  Preferences p;
  p.begin("mousecal", false);
  p.putInt("gyroSign", gyroSign);
  p.putInt("minL", minPwmL);        p.putInt("minR", minPwmR);
  p.putFloat("trimLF", trimLF);     p.putFloat("trimRF", trimRF);
  p.putFloat("trimLR", trimLR);     p.putFloat("trimRR", trimRR);
  p.putFloat("leadF", stopLeadFwd); p.putFloat("leadR", stopLeadRev);
  p.putFloat("turnL", turnLeadL);   p.putFloat("turnR", turnLeadR);
  p.putBool("ok", true);
  p.end();
}

// Print the saved log of the last run, then the values currently in use.
void printSaved() {
  Preferences p;
  String saved;
  if (p.begin("mousecal", true)) { saved = p.getString("log", ""); p.end(); }
  if (saved.length()) {
    Serial.println(F("\n================ LAST RUN (saved in flash) ================"));
    Serial.print(saved);
    Serial.println(F("================ end of last run ================"));
  } else {
    Serial.println(F("\nNo saved run yet."));
  }
  Serial.println(F("Values in use now:"));
  Serial.printf("  gyro sign %+d | min PWM  L %d  R %d\n", gyroSign, minPwmL, minPwmR);
  Serial.printf("  trim fwd  L %.3f  R %.3f | trim rev  L %.3f  R %.3f\n", trimLF, trimRF, trimLR, trimRR);
  Serial.printf("  stop lead fwd %.0f  rev %.0f ticks | turn lead L %.1f  R %.1f deg\n",
                stopLeadFwd, stopLeadRev, turnLeadL, turnLeadR);
  Serial.println(F("Press BOOT or send 'r' to run calibration. 'p' prints this again."));
}

// ============================================================================
//  STEP 1: spin test - which way is the gyro, which way do encoders count
// ============================================================================
void spinTest() {
  report("\n[1/3] Spin test (short left spin, then back)\n");
  gyroSign = +1; encSignL = encSignR = +1; gyroPeakRaw = 0;
  long sL = countL, sR = countR;
  resetGyro();
  unsigned long t0 = millis();
  while (millis() - t0 < 350) { updateGyro(); rawMotors(-TURN_PWM, +TURN_PWM); delay(3); }
  stopMotors(); settle();
  float ang = gyroAngle;
  long dL = countL - sL, dR = countR - sR;
  report("  gyro %+.1f deg | left enc %+ld | right enc %+ld | gyro peak %d/32767\n",
       ang, dL, dR, gyroPeakRaw);

  if (labs(dL) < 10) halt("LEFT encoder didn't count during the spin - check its wires/power");
  if (labs(dR) < 10) halt("RIGHT encoder didn't count during the spin - check its wires/power");
  if (fabs(ang) < 10) halt("Mouse didn't rotate: both wheels turned the same way. Re-check motor directions (motor_encoder_test, 'd').");
  if (gyroPeakRaw > 32000) report("  WARNING: gyro hit its limit - spin was very fast\n");

  gyroSign = (ang > 0) ? +1 : -1;               // left spin must read positive
  encSignL = (dL < 0) ? +1 : -1;                // left wheel went backward
  encSignR = (dR > 0) ? +1 : -1;                // right wheel went forward
  report("  -> gyro sign %+d%s\n", gyroSign, gyroSign < 0 ? "  (was BACKWARDS - this alone crashes mouse_map)" : "");
  if (encSignL < 0) report("  -> left encoder counts backwards (handled here)\n");
  if (encSignR < 0) report("  -> right encoder counts backwards (handled here)\n");

  t0 = millis();
  while (millis() - t0 < 350) { rawMotors(+TURN_PWM, -TURN_PWM); delay(3); }
  stopMotors(); settle();
}

// ============================================================================
//  STEP 2: dead-band - lowest PWM that actually moves each wheel
// ============================================================================
int findDeadband(bool left) {
  long start = left ? tL() : tR();
  int found = -1;
  for (int p = 20; p <= 160 && found < 0; p += 2) {
    if (left) rawMotors(p, 0); else rawMotors(0, p);
    delay(60);
    if ((left ? tL() : tR()) - start >= 8) found = p;
  }
  stopMotors(); settle();
  if (found < 0) halt(left ? "LEFT wheel never moved up to PWM 160 - check motor wires / battery"
                           : "RIGHT wheel never moved up to PWM 160 - check motor wires / battery");
  int back = min(found + 15, 160);
  unsigned long t0 = millis();
  while ((left ? tL() : tR()) - start > 3 && millis() - t0 < 2000) {
    if (left) rawMotors(-back, 0); else rawMotors(0, -back);
    delay(3);
  }
  stopMotors(); settle();
  return min(found + 5, 160);                   // small margin so it never stalls
}

// ============================================================================
//  STEP 3 primitives - identical logic to mouse_map
// ============================================================================
// dir +1 = forward, -1 = reverse. One square, heading held by gyro + encoders.
Run driveStraight(int dir) {
  float lead = (dir > 0) ? stopLeadFwd : stopLeadRev;
  long sL = tL(), sR = tR();
  resetGyro();
  double corrSum = 0; long corrN = 0;
  Run r = { 0, 0.0, 0.0, false };
  unsigned long t0 = millis();
  while (true) {
    updateGyro();
    long dL = (tL() - sL) * dir, dR = (tR() - sR) * dir;
    long avg = (dL + dR) / 2;
    if (avg >= TICKS_PER_CELL - (long)lead) break;
    if (dir > 0 && readFront() < FRONT_ABORT_MM) { r.aborted = true; break; }
    if (millis() - t0 > 4000) { r.aborted = true; break; }
    float c = KP_HEAD * gyroAngle + KD_HEAD * lastGyroZ + KP_ENC * dir * (float)(dR - dL);
    if (c >  CORR_MAX) c =  CORR_MAX;
    if (c < -CORR_MAX) c = -CORR_MAX;
    int corr = (int)c;
    setMotors(dir * CRUISE_PWM + corr, dir * CRUISE_PWM - corr);
    if (avg > TICKS_PER_CELL / 4 && avg < TICKS_PER_CELL * 3 / 4) { corrSum += corr; corrN++; }
    delay(5);
  }
  stopMotors();
  settle();
  long dL = (tL() - sL) * dir, dR = (tR() - sR) * dir;
  r.travelled  = (dL + dR) / 2;
  r.avgCorr    = corrN ? (float)(corrSum / corrN) : 0.0f;
  r.endHeading = gyroAngle;
  return r;
}

// + = left (CCW). Returns where it actually ended up after coasting to a stop.
float turnDeg(float degrees) {
  float lead = (degrees > 0) ? turnLeadL : turnLeadR;
  int slowMin = max(minPwmL, minPwmR);
  resetGyro();
  unsigned long t0 = millis(), stallSince = 0;
  int boost = 0;
  while (millis() - t0 < TURN_TIMEOUT_MS) {
    updateGyro();
    float remaining = degrees - gyroAngle;
    if (remaining * (degrees > 0 ? 1 : -1) <= lead) break;
    int pwm = TURN_PWM;
    if (fabs(remaining) < TURN_SLOW_ZONE_DEG && TURN_PWM > slowMin)
      pwm = slowMin + (int)((TURN_PWM - slowMin) * (fabs(remaining) / TURN_SLOW_ZONE_DEG));
    // Carpet drag can stall the slow end of a turn short of the target:
    // if it stops rotating, keep stepping the power up until it moves.
    if (fabs(lastGyroZ) < TURN_STALL_DPS) {
      if (!stallSince) stallSince = millis();
      else if (millis() - stallSince > TURN_STALL_MS && boost < TURN_BOOST_MAX) { boost += TURN_BOOST_STEP; stallSince = millis(); }
    } else stallSince = 0;
    pwm = min(pwm + boost, PWM_MAX);
    if (degrees > 0) setMotors(-pwm, +pwm); else setMotors(+pwm, -pwm);
    delay(3);
  }
  if (millis() - t0 >= TURN_TIMEOUT_MS) report("  (turn timed out)\n");
  stopMotors();
  settle();
  return gyroAngle;
}

// Scale trims so a wheel that needed +c extra steering gets that much more power.
void learnTrim(float &tLeft, float &tRight, float leftNeeds) {
  float k = LEARN_RATE * leftNeeds / CRUISE_PWM;
  tLeft *= (1.0f + k); tRight *= (1.0f - k);
  float m = (tLeft + tRight) / 2.0f;
  tLeft = constrain(tLeft / m, 0.7f, 1.3f);
  tRight = constrain(tRight / m, 0.7f, 1.3f);
}

// Returns true if it LOCKED IN (converged), false if saved but not settled.
bool runCalibration() {
  spinTest();

  report("\n[2/3] Motor dead-band\n");
  minPwmL = findDeadband(true);
  minPwmR = findDeadband(false);
  report("  -> min PWM  L %d  R %d\n", minPwmL, minPwmR);

  report("\n[3/3] Learning: fwd 1 square, back 1 square, L90 R90 R90 L90  (1 square = %ld ticks)\n",
       TICKS_PER_CELL);
  int good = 0, aborts = 0;
  bool locked = false;
  for (int round = 1; round <= MAX_ROUNDS; round++) {
    Run f = driveStraight(+1); delay(300);
    Run b = driveStraight(-1); delay(300);
    float l1 = turnDeg(+90); delay(250);
    float r1 = turnDeg(-90); delay(250);
    float r2 = turnDeg(-90); delay(250);
    float l2 = turnDeg(+90); delay(250);

    long  overF = f.travelled - TICKS_PER_CELL, overB = b.travelled - TICKS_PER_CELL;
    float overL = ((l1 - 90.0f) + (l2 - 90.0f)) / 2.0f;       // + = turned too far
    float overR = ((-r1 - 90.0f) + (-r2 - 90.0f)) / 2.0f;

    report("round %2d: fwd %+5.1fmm %+4.1fdeg steer %+5.1f%s | rev %+5.1fmm %+4.1fdeg steer %+5.1f%s\n",
           round, overF * MM_PER_TICK, f.endHeading, f.avgCorr, f.aborted ? " STOPPED" : "",
           overB * MM_PER_TICK, b.endHeading, b.avgCorr, b.aborted ? " STOPPED" : "");
    report("          L90 %5.1f %5.1f | R90 %5.1f %5.1f", l1, l2, -r1, -r2);

    bool ok = !f.aborted && !b.aborted
           && labs(overF) <= DIST_TOL_TICKS && labs(overB) <= DIST_TOL_TICKS
           && fabs(f.avgCorr) <= TRIM_TOL_PWM && fabs(b.avgCorr) <= TRIM_TOL_PWM
           && fabs(overL) <= TURN_TOL_DEG && fabs(overR) <= TURN_TOL_DEG;

    if (f.aborted || b.aborted) {
      aborts++;
      report("\n          straight STOPPED early (wall ahead or stuck) - distance not learned this round");
      if (aborts >= 3) { saveCal(); halt("Keeps stopping early. Give it ~30 cm clear in front and behind."); }
    } else {
      stopLeadFwd = constrain(stopLeadFwd + LEARN_RATE * overF, 0.0f, TICKS_PER_CELL / 2.0f);
      stopLeadRev = constrain(stopLeadRev + LEARN_RATE * overB, 0.0f, TICKS_PER_CELL / 2.0f);
      learnTrim(trimLF, trimRF, +f.avgCorr);   // fwd: left gets CRUISE + corr
      learnTrim(trimLR, trimRR, -b.avgCorr);   // rev: left gets CRUISE - corr in magnitude
    }
    turnLeadL = constrain(turnLeadL + LEARN_RATE * overL, 0.5f, 30.0f);
    turnLeadR = constrain(turnLeadR + LEARN_RATE * overR, 0.5f, 30.0f);

    good = ok ? good + 1 : 0;
    report(" | %s %d/%d\n", ok ? "GOOD" : "adjusting", good, GOOD_ROUNDS_TO_LOCK);
    if (good >= GOOD_ROUNDS_TO_LOCK) { locked = true; break; }
  }

  saveCal();
  report("\n============================================\n");
  if (locked) report("  LOCKED IN - saved. Flash mouse_map next.\n");
  else        report("  Saved, but NOT fully settled after %d rounds.\n  See which line above stays off; run again to keep learning.\n", MAX_ROUNDS);
  printCal();
  report("============================================\n");
  return locked;
}

void startRun() {
  clearLog();
  ledMode = LED_RUNNING;
  Serial.println(F("\nStarting - HANDS OFF..."));
  delay(START_DELAY_MS);
  calibrateGyro();
  delay(500);
  bool locked = runCalibration();
  saveLog();
  ledMode = locked ? LED_DONE : LED_UNSETTLED;
  Serial.println(F("\nPress BOOT or send 'r' to run again. 'p' prints the saved log."));
}

// ============================================================================
void setup() {
  Serial.begin(115200); delay(400);
  Serial.println(F("\n=== Calibrate: learn straight / reverse / 90 turns, then lock in ==="));

  xTaskCreate(ledTask, "led", 2048, nullptr, 1, nullptr);
  pinMode(PIN_BOOT_BTN, INPUT_PULLUP);

  pinMode(PIN_L_DIR, OUTPUT); pinMode(PIN_R_DIR, OUTPUT);
  ledcAttach(PIN_L_PWM, PWM_FREQ_HZ, PWM_BITS);
  ledcAttach(PIN_R_PWM, PWM_FREQ_HZ, PWM_BITS);
  stopMotors();

  pinMode(PIN_L_ENC_A, INPUT_PULLUP); pinMode(PIN_L_ENC_B, INPUT_PULLUP);
  pinMode(PIN_R_ENC_A, INPUT_PULLUP); pinMode(PIN_R_ENC_B, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(PIN_L_ENC_A), isrLeft,  CHANGE);
  attachInterrupt(digitalPinToInterrupt(PIN_R_ENC_A), isrRight, CHANGE);

  Wire.begin(PIN_SDA, PIN_SCL); Wire.setClock(100000);
  startFront();
  if (!mpuWrite(MPU_PWR_MGMT_1, 0x00)) halt("MPU-6050 not responding - check SDA/SCL/VCC/GND");
  mpuWrite(MPU_GYRO_CONFIG, 0x10);               // +-1000 dps
  delay(50);

  loadCal();
  printSaved();
  ledMode = LED_READY;
}

void loop() {
  if (digitalRead(PIN_BOOT_BTN) == LOW) {
    delay(30);
    if (digitalRead(PIN_BOOT_BTN) == LOW) {
      while (digitalRead(PIN_BOOT_BTN) == LOW) delay(10);   // wait for release
      startRun();
    }
  }
  if (Serial.available()) {
    char c = Serial.read();
    if (c == 'r') startRun();
    else if (c == 'p') printSaved();
  }
  delay(10);
}
