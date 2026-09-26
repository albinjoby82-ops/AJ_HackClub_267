/*
 * ============================================================================
 *  MICROMOUSE - MAZE MAPPING with FLOOD FILL  (map the maze on the first run)
 * ============================================================================
 *
 *  Dublin Micromouse Open 2026  -  ESP32-C6 + 3x VL53L0X + MPU-6050 + DRI0044.
 *
 *  This is the "real" exploration: it keeps a map of walls, runs flood fill to
 *  decide where to go, and heads for the centre - discovering walls and
 *  re-planning as it goes - until it has mapped a route to the goal.
 *
 *  The MAPPING BRAIN lives in maze.h and is proven in the desktop simulator
 *  (firmware/sim), which reaches the goal on 100% of solvable mazes. So the job
 *  of THIS file is the hard part everyone warns about: moving and sensing
 *  reliably enough that the map stays correct. One wrong wall, or losing track
 *  of which cell you're in, and flood fill will confidently plan through a wall.
 *
 *  The three tricks that fight odometry drift, each pinning one degree of
 *  freedom against the walls every cell so error can't pile up:
 *    - HEADING: turns are closed-loop on the gyro, and the gyro angle is reset
 *      to zero each move, so every straight is held against "0 degrees" and
 *      every cell re-squares the mouse to the cardinal direction.
 *    - SIDEWAYS: while crossing a cell it centres between the side walls, so it
 *      re-centres in the corridor every single cell.
 *    - FORWARD: when there's a wall ahead it stops at a fixed distance from it
 *      (front ToF), pinning how far along the cell it actually is.
 *  Walls are only ever read while stopped and squared up, and every wall is
 *  written to both cells that share it, so the map cannot disagree with itself.
 *
 *  Run calibrate first (it saves what this sketch loads). Runs cable-free:
 *    1. Power it from the battery, put it in the start corner with the outer
 *       wall on its LEFT, facing the open side.
 *    2. Press BOOT and let go. Hands off while it calibrates the gyro.
 *    3. Onboard LED:  dim white = ready, blue flashing = mapping,
 *       green = reached the centre, red = stopped (reason in the log),
 *       red flashing = hardware error.
 *       Press BOOT while it's driving to stop it and keep the map so far.
 *    4. Plug in USB, open Serial Monitor at 115200: it prints the saved log of
 *       the last run (why it stopped + the map). Send 'p' if nothing shows.
 *  It never starts moving by itself, so plugging USB in (which can reset the
 *  board) is safe. Needs the Pololu "VL53L0X" library.
 * ============================================================================
 */

#include <Wire.h>
#include <VL53L0X.h>
#include <Preferences.h>
#include <stdarg.h>
#include "maze.h"

// ============================================================================
//  CONFIG  (identical hardware to mouse_explore - keep them in sync)
// ============================================================================
const int PIN_SDA = 6, PIN_SCL = 7;

const int     XSHUT[3]       = {  18, 19, 20 };
const char   *SENSOR_NAME[3] = { "LEFT",  "FRONT", "RIGHT" };
const uint8_t SENSOR_ADDR[3] = { 0x30,    0x31,    0x32   };
enum { S_LEFT = 0, S_FRONT = 1, S_RIGHT = 2 };

const int PIN_L_DIR = 0, PIN_L_PWM = 2;
const int PIN_R_DIR = 3, PIN_R_PWM = 10;
const int L_DIR_SIGN = +1, R_DIR_SIGN = -1;

const int PIN_L_ENC_A = 21, PIN_L_ENC_B = 22;
const int PIN_R_ENC_A = 23, PIN_R_ENC_B = 11;

const int STATUS_RGB_PIN = 8;       // onboard RGB LED (DevKitC-1)
const int PIN_BOOT_BTN = 9;         // onboard BOOT button, LOW when pressed
const unsigned long START_DELAY_MS = 3000;   // time to take your hand away

const int PWM_FREQ_HZ = 20000, PWM_BITS = 8, PWM_MAX = 255;
const int CRUISE_PWM = 90, TURN_PWM = 85, BACKUP_PWM = 80, MIN_MOVE_PWM = 45;

// Geometry - MEASURE (guide H6).
const float CELL_MM = 180.0, WHEEL_DIAMETER_MM = 44.0, ENC_TICKS_PER_REV = 402.0;
const long  TICKS_PER_CELL =
    (long)((CELL_MM * ENC_TICKS_PER_REV) / (PI * WHEEL_DIAMETER_MM) + 0.5);

// Wall detection (mm) - TUNE on real walls. A wall is only recorded when a
// reading is comfortably inside these, to avoid poisoning the map.
const int FRONT_WALL_MM = 120;      // wall ahead of this cell if front < this
const int SIDE_WALL_MM  = 100;      // side wall if that ToF < this
const int FRONT_STOP_MM = 65;       // stop this far from a wall ahead
const int MAX_VALID_MM  = 1200;
const int WALL_TRUST_MM = 90;       // only centre off a side wall this close
const int SIDE_SETPOINT_MM = 70;

// Steering gains (see mouse_explore for the rationale - heading first).
const float KP_HEAD = 3.0, KD_HEAD = 0.4, KP_ENC = 0.5;
const float KP_CENTER = 0.25, KP_SIDE = 0.30;
const int   CORR_MAX = 55;

// Turns.
const float TURN_SLOW_ZONE_DEG = 25.0;
const unsigned long TURN_TIMEOUT_MS = 3000;
const float TURN_STALL_DPS = 15.0;             // rotating slower than this = stalled
const unsigned long TURN_STALL_MS = 120;
const int   TURN_BOOST_STEP = 6, TURN_BOOST_MAX = 90;
const float TURN_NUDGE_DEG = 4.0;              // landed further off than this = creep back
const float TURN_FAIL_DEG  = 20.0;             // still this far off = stop, don't drive blind

// forwardOneCell() results.
const int MOVE_OK = 1, MOVE_STALLED = 0, MOVE_BLOCKED = -1;

// Recovery / stall.
const int           MAX_RECOVERY = 3;
const long          STALL_TICKS = 3;
const unsigned long STALL_MS = 700, CELL_TIMEOUT_MS = 6000;

// MPU-6050.
const uint8_t MPU_ADDR = 0x68, MPU_PWR_MGMT_1 = 0x6B, MPU_GYRO_CONFIG = 0x1B, MPU_GYRO_ZOUT_H = 0x47;
const float   GYRO_LSB_PER_DPS = 32.8;      // +-1000 dps range, so a fast spin can't clip
const int     GYRO_SIGN = +1, GYRO_CAL_SAMPLES = 800;

// Learned by the calibrate sketch and loaded from flash at boot (see loadCal).
// These defaults are only used if calibrate has never been run.
int   gyroSign = GYRO_SIGN;
int   minPwmL = MIN_MOVE_PWM, minPwmR = MIN_MOVE_PWM;
float trimLF = 1.0, trimRF = 1.0, trimLR = 1.0, trimRR = 1.0;
float stopLeadFwd = 0.0, stopLeadRev = 0.0;   // ticks
float turnLeadL = 2.0, turnLeadR = 2.0;       // degrees

// Maze.
const int MAZE_W = 16, MAZE_H = 16;
const int START_X = 0, START_Y = 0, START_DIR = DIR_N;

// ============================================================================
//  STATE
// ============================================================================
VL53L0X laser[3];
Maze<16, 16> maze;

volatile long countL = 0, countR = 0;

int posX = START_X, posY = START_Y, headingDir = START_DIR;   // pose in cells
float gyroBiasRaw = 0.0, gyroAngle = 0.0, lastGyroZ = 0.0;    // per-move gyro
unsigned long lastGyroUs = 0;

int  distL = MAX_VALID_MM, distF = MAX_VALID_MM, distR = MAX_VALID_MM;
int  recoveryAttempts = 0;
bool running = false;
bool calLoaded = false;

// Types used in function signatures must be defined before any function: the
// Arduino IDE auto-inserts function prototypes above the first function.
enum LedState { LED_BOOT, LED_EXPLORING, LED_TURNING, LED_RECOVER, LED_BLOCKED, LED_ERROR, LED_DONE };
enum LedMode  { MODE_READY, MODE_RUNNING, MODE_GOAL, MODE_STOPPED, MODE_FAULT };
LedState ledState = LED_BOOT;
volatile LedMode ledMode = MODE_READY;

// Mapping prints a lot, so keep only the most recent part - that's where the
// map and the reason it stopped are. Saved to flash at the end of a run.
const size_t LOG_CAP = 3800;                // flash strings max out at 4000 bytes
char   logRing[LOG_CAP];
size_t logHead = 0;
bool   logWrapped = false;

// ============================================================================
//  ENCODER ISRs
// ============================================================================
void IRAM_ATTR isrLeft()  { if (digitalRead(PIN_L_ENC_A) == digitalRead(PIN_L_ENC_B)) countL++; else countL--; }
void IRAM_ATTR isrRight() { if (digitalRead(PIN_R_ENC_A) == digitalRead(PIN_R_ENC_B)) countR++; else countR--; }

// ============================================================================
//  LED / SERIAL STATE
// ============================================================================
void stopMotors();   // fwd decl used by halt()

void report(const char *fmt, ...) {
  char line[192];
  va_list ap; va_start(ap, fmt);
  int n = vsnprintf(line, sizeof(line), fmt, ap);
  va_end(ap);
  Serial.print(line);
  if (n <= 0) return;
  size_t k = min((size_t)n, sizeof(line) - 1);
  for (size_t i = 0; i < k; i++) {
    logRing[logHead++] = line[i];
    if (logHead == LOG_CAP) { logHead = 0; logWrapped = true; }
  }
}
void clearLog() { logHead = 0; logWrapped = false; }
void saveLog() {
  static char out[LOG_CAP + 64];
  size_t n = 0;
  if (logWrapped) {
    const char *cut = "...(earlier lines dropped)\n";
    n = strlen(cut); memcpy(out, cut, n);
    size_t skip = 0;                                    // start at the next full line
    while (skip < LOG_CAP && logRing[(logHead + skip) % LOG_CAP] != '\n') skip++;
    for (size_t i = skip + 1; i < LOG_CAP; i++) out[n++] = logRing[(logHead + i) % LOG_CAP];
  } else {
    memcpy(out, logRing, logHead); n = logHead;
  }
  out[n] = 0;
  Preferences p;
  p.begin("mousemap", false);
  p.putString("log", out);
  p.end();
}
void printSaved() {
  Preferences p;
  String saved;
  if (p.begin("mousemap", true)) { saved = p.getString("log", ""); p.end(); }
  if (saved.length()) {
    Serial.println(F("\n================ LAST RUN (saved in flash) ================"));
    Serial.print(saved);
    Serial.println(F("================ end of last run ================"));
  } else {
    Serial.println(F("\nNo saved run yet."));
  }
  Serial.println(F("Press BOOT or send 'r' to start mapping. 'p' prints the saved log again."));
}

void ledTask(void *) {
  bool on = false;
  while (true) {
    on = !on;
    switch (ledMode) {
      case MODE_READY:   rgbLedWrite(STATUS_RGB_PIN, 6, 6, 6);            break;
      case MODE_RUNNING: rgbLedWrite(STATUS_RGB_PIN, 0, 0, on ? 60 : 0);  break;
      case MODE_GOAL:    rgbLedWrite(STATUS_RGB_PIN, 0, 60, 0);           break;
      case MODE_STOPPED: rgbLedWrite(STATUS_RGB_PIN, 60, 0, 0);           break;
      case MODE_FAULT:   rgbLedWrite(STATUS_RGB_PIN, on ? 60 : 0, 0, 0);  break;
    }
    vTaskDelay(pdMS_TO_TICKS(ledMode == MODE_FAULT ? 150 : 300));
  }
}

void showLED(LedState s) {
  if (s != ledState) {
    ledState = s;
    const char *n = "";
    switch (s) {
      case LED_BOOT: n = "BOOT"; break;           case LED_EXPLORING: n = "EXPLORING"; break;
      case LED_TURNING: n = "TURNING"; break;     case LED_RECOVER: n = "RECOVER"; break;
      case LED_BLOCKED: n = "BLOCKED"; break;     case LED_ERROR: n = "ERROR"; break;
      case LED_DONE: n = "DONE"; break;
    }
    report("[state] %s\n", n);
  }
  switch (s) {
    case LED_BOOT:    ledMode = MODE_READY;   break;
    case LED_DONE:    ledMode = MODE_GOAL;    break;
    case LED_BLOCKED: ledMode = MODE_STOPPED; break;
    case LED_ERROR:   ledMode = MODE_FAULT;   break;
    default:          ledMode = MODE_RUNNING; break;
  }
}

void halt(const char *why) {
  stopMotors();
  running = false;
  report("HALT: %s\n", why);
  showLED(LED_ERROR);
  saveLog();
  while (true) delay(1000);
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
void setMotors(int l, int r) {
  motorWrite(PIN_L_DIR, PIN_L_PWM, L_DIR_SIGN, l, minPwmL, trimLF, trimLR);
  motorWrite(PIN_R_DIR, PIN_R_PWM, R_DIR_SIGN, r, minPwmR, trimRF, trimRR);
}
void stopMotors() { ledcWrite(PIN_L_PWM, 0); ledcWrite(PIN_R_PWM, 0); }

// ============================================================================
//  GYRO
// ============================================================================
bool mpuWrite(uint8_t reg, uint8_t val) {
  Wire.beginTransmission(MPU_ADDR); Wire.write(reg); Wire.write(val);
  return Wire.endTransmission() == 0;
}
bool readGyroRaw(int16_t &raw) {
  Wire.beginTransmission(MPU_ADDR); Wire.write(MPU_GYRO_ZOUT_H);
  if (Wire.endTransmission(false) != 0) return false;
  if (Wire.requestFrom((int)MPU_ADDR, 2) != 2) return false;
  raw = (int16_t)((Wire.read() << 8) | Wire.read());
  return true;
}
float readGyroZ() {
  int16_t raw;
  if (!readGyroRaw(raw)) return 0.0;
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
  report("Gyro bias Z = %.3f dps\n", gyroBiasRaw);
}

// Wait for both wheels to stop, integrating the gyro so the coast is counted.
void settle() {
  long lL = countL, lR = countR;
  unsigned long t0 = millis(), still = millis();
  while (millis() - t0 < 1000) {
    updateGyro(); delay(3);
    if (countL != lL || countR != lR) { lL = countL; lR = countR; still = millis(); }
    else if (millis() - still > 150) break;
  }
}

void loadCal() {
  Preferences p;
  bool ok = p.begin("mousecal", true) && p.getBool("ok", false);
  if (ok) {
    gyroSign = p.getInt("gyroSign", gyroSign);
    minPwmL = p.getInt("minL", minPwmL);        minPwmR = p.getInt("minR", minPwmR);
    trimLF = p.getFloat("trimLF", trimLF);      trimRF = p.getFloat("trimRF", trimRF);
    trimLR = p.getFloat("trimLR", trimLR);      trimRR = p.getFloat("trimRR", trimRR);
    stopLeadFwd = p.getFloat("leadF", stopLeadFwd); stopLeadRev = p.getFloat("leadR", stopLeadRev);
    turnLeadL = p.getFloat("turnL", turnLeadL); turnLeadR = p.getFloat("turnR", turnLeadR);
  }
  p.end();
  calLoaded = ok;
}
void reportCal() {
  if (!calLoaded) { report("WARNING: no calibration saved - run the calibrate sketch first. Using defaults.\n"); return; }
  report("Loaded calibration:\n");
  report("  gyro sign %+d | min PWM  L %d  R %d\n", gyroSign, minPwmL, minPwmR);
  report("  trim fwd  L %.3f  R %.3f | trim rev  L %.3f  R %.3f\n", trimLF, trimRF, trimLR, trimRR);
  report("  stop lead fwd %.0f  rev %.0f ticks | turn lead L %.1f  R %.1f deg\n",
         stopLeadFwd, stopLeadRev, turnLeadL, turnLeadR);
}

// ============================================================================
//  SENSORS
// ============================================================================
int readDist(int i) {
  uint16_t r = laser[i].readRangeContinuousMillimeters();
  if (laser[i].timeoutOccurred() || r == 0 || r > MAX_VALID_MM) return MAX_VALID_MM;
  return (int)r;
}
// Average a few reads while stopped, for a trustworthy wall decision.
int readDistStable(int i) {
  long sum = 0; int n = 0;
  for (int k = 0; k < 5; k++) { sum += readDist(i); n++; delay(6); }
  return (int)(sum / n);
}
void readAll() { distL = readDist(S_LEFT); distF = readDist(S_FRONT); distR = readDist(S_RIGHT); }

void dumpBus() {
  report("Devices answering on I2C:");
  for (uint8_t a = 1; a < 127; a++) {
    Wire.beginTransmission(a);
    if (Wire.endTransmission() == 0) report(" 0x%02X", a);
  }
  report("   (expect 0x30 0x31 0x32 0x68 when all are up)\n");
}

void startSensors() {
  for (int i = 0; i < 3; i++) { pinMode(XSHUT[i], OUTPUT); digitalWrite(XSHUT[i], LOW); }
  delay(20);
  for (int i = 0; i < 3; i++) {
    bool ok = false;
    for (int attempt = 1; attempt <= 3 && !ok; attempt++) {
      digitalWrite(XSHUT[i], LOW);  delay(10);   // hard-reset just this sensor
      digitalWrite(XSHUT[i], HIGH); delay(50);
      laser[i].setTimeout(200);
      ok = laser[i].init();
      if (!ok) report("VL53L0X %s init attempt %d/3 failed\n", SENSOR_NAME[i], attempt);
    }
    if (!ok) {
      dumpBus();
      char m[96]; snprintf(m, sizeof(m), "VL53L0X %s init failed: check its XSHUT (GPIO%d), SDA/SCL, VIN, GND", SENSOR_NAME[i], XSHUT[i]);
      halt(m);
    }
    laser[i].setAddress(SENSOR_ADDR[i]);
    if (!laser[i].setMeasurementTimingBudget(33000)) halt("VL53L0X timing budget rejected");
    report("Sensor %-5s initialized OK at 0x%02X\n", SENSOR_NAME[i], SENSOR_ADDR[i]);
  }
  // Start ranging only once all three are addressed, so none is busy while another boots.
  for (int i = 0; i < 3; i++) laser[i].startContinuous();
  if (!mpuWrite(MPU_PWR_MGMT_1, 0x00)) halt("MPU-6050 not responding: check SDA/SCL/VIN/GND");
  mpuWrite(MPU_GYRO_CONFIG, 0x10);   // +-1000 dps, must match GYRO_LSB_PER_DPS
  delay(50);
  report("IMU (MPU-6050) initialized OK at 0x68\n");
}

// ============================================================================
//  MAP: record what the three sensors see into the maze (must be stopped)
// ============================================================================
void recordWalls() {
  int dl = readDistStable(S_LEFT), df = readDistStable(S_FRONT), dr = readDistStable(S_RIGHT);
  distL = dl; distF = df; distR = dr;
  if (df < FRONT_WALL_MM) maze.setWall(posX, posY, headingDir);
  if (dl < SIDE_WALL_MM)  maze.setWall(posX, posY, dirLeft(headingDir));
  if (dr < SIDE_WALL_MM)  maze.setWall(posX, posY, dirRight(headingDir));
  report("cell (%d,%d) dir %d | L%4d F%4d R%4d | walls %c%c%c\n",
         posX, posY, headingDir, dl, df, dr,
         (df < FRONT_WALL_MM) ? 'F' : '.',
         (dl < SIDE_WALL_MM)  ? 'L' : '.',
         (dr < SIDE_WALL_MM)  ? 'R' : '.');
}

// ============================================================================
//  MOTION PRIMITIVES
// ============================================================================
int steeringCorrection(long dL, long dR) {
  float corr = KP_HEAD * gyroAngle + KD_HEAD * lastGyroZ;   // heading hold (target 0)
  corr += KP_ENC * (float)(dR - dL);                        // wheel match
  bool tl = (distL < WALL_TRUST_MM), tr = (distR < WALL_TRUST_MM);
  if (tl && tr)      corr += KP_CENTER * (distR - distL);
  else if (tl)       corr += KP_SIDE * (SIDE_SETPOINT_MM - distL);
  else if (tr)       corr -= KP_SIDE * (SIDE_SETPOINT_MM - distR);
  if (corr > CORR_MAX) corr = CORR_MAX;
  if (corr < -CORR_MAX) corr = -CORR_MAX;
  return (int)corr;
}

// Drive forward one cell. MOVE_OK = it's now in the next cell. MOVE_BLOCKED =
// a wall was right in front before it left this cell (pose unchanged).
// MOVE_STALLED = it got stuck and backed off to where it started.
int forwardOneCell() {
  long startL = countL, startR = countR;
  resetGyro();
  unsigned long t0 = millis(), lastProg = t0; long best = 0;
  showLED(LED_EXPLORING);

  while (true) {
    updateGyro(); readAll();
    long dL = labs(countL - startL), dR = labs(countR - startR), avg = (dL + dR) / 2;

    if (distF < FRONT_STOP_MM) {
      stopMotors();
      // Stopped by a wall before really leaving this cell: it did NOT move a
      // cell. Counting it as one is what corrupts the map after a bad turn.
      return (avg < TICKS_PER_CELL / 3) ? MOVE_BLOCKED : MOVE_OK;
    }
    if (avg >= TICKS_PER_CELL - (long)stopLeadFwd) { stopMotors(); return MOVE_OK; }   // coasts the rest

    int corr = steeringCorrection(dL, dR);
    setMotors(CRUISE_PWM + corr, CRUISE_PWM - corr);

    if (avg > best + STALL_TICKS) { best = avg; lastProg = millis(); }
    if (millis() - lastProg > STALL_MS || millis() - t0 > CELL_TIMEOUT_MS) {
      // Stalled: back up roughly to where this cell started, leave pose unchanged.
      stopMotors(); delay(100);
      unsigned long tb = millis();
      while (labs(countL - startL) > STALL_TICKS && millis() - tb < 1500) {
        setMotors(-BACKUP_PWM, -BACKUP_PWM); delay(5);
      }
      stopMotors(); return MOVE_STALLED;
    }
    delay(5);
  }
}

// Creep toward the exact target at low power after the main turn coasts to a
// stop. Continues from the same gyro angle, so it can fix under- or overshoot.
void nudgeTo(float degrees, int slowMin) {
  for (int tries = 0; tries < 3 && fabs(degrees - gyroAngle) > TURN_NUDGE_DEG; tries++) {
    unsigned long t0 = millis(), stallSince = 0;
    int boost = 0;
    while (millis() - t0 < 800) {
      updateGyro();
      float rem = degrees - gyroAngle;
      if (fabs(rem) < 1.0) break;
      if (fabs(lastGyroZ) < TURN_STALL_DPS) {
        if (!stallSince) stallSince = millis();
        else if (millis() - stallSince > TURN_STALL_MS && boost < TURN_BOOST_MAX) { boost += TURN_BOOST_STEP; stallSince = millis(); }
      } else stallSince = 0;
      int pwm = min(slowMin + boost, PWM_MAX);
      if (rem > 0) setMotors(-pwm, +pwm); else setMotors(+pwm, -pwm);
      delay(3);
    }
    stopMotors(); settle();
  }
}

// Returns where it actually ended up, in degrees from where it started.
float turnInPlace(float degrees) {
  showLED(LED_TURNING);
  float lead = (degrees > 0) ? turnLeadL : turnLeadR;   // learned coast after cut-off
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
  bool timedOut = millis() - t0 >= TURN_TIMEOUT_MS;
  unsigned long ms = millis() - t0;
  stopMotors(); settle();
  float landed = gyroAngle;
  nudgeTo(degrees, slowMin);
  report("  turn %+.0f: landed %+.1f, after nudge %+.1f (%lu ms%s%s)\n",
         degrees, landed, gyroAngle, ms, boost ? ", boosted" : "", timedOut ? ", TIMED OUT" : "");
  return gyroAngle;
}

// Turn to an absolute cardinal direction by the shortest rotation.
// Returns false if it couldn't get within TURN_FAIL_DEG of the target.
bool turnToHeading(int target) {
  int diff = (target - headingDir) & 3;
  float want = 0.0;
  if (diff == 1)      want = -90.0;   // target is to our right (CW)
  else if (diff == 3) want = +90.0;   // to our left (CCW)
  else if (diff == 2) want = 180.0;
  if (want == 0.0) return true;
  float got = turnInPlace(want);
  if (fabs(got - want) > TURN_FAIL_DEG) return false;
  headingDir = target;
  return true;
}

// ============================================================================
//  MAP PRINTOUT (matches the simulator's rendering)
// ============================================================================
void printMap() {
  report("\n--- discovered map (M=mouse, G=goal) ---\n");
  char row[96];
  for (int y = maze.H - 1; y >= 0; y--) {
    int n = 0;
    for (int x = 0; x < maze.W; x++) n += snprintf(row + n, sizeof(row) - n, "+%s", maze.hasWall(x, y, DIR_N) ? "---" : "   ");
    report("%s+\n", row);
    n = 0;
    for (int x = 0; x < maze.W; x++)
      n += snprintf(row + n, sizeof(row) - n, "%c%s", maze.hasWall(x, y, DIR_W) ? '|' : ' ',
                    (x == posX && y == posY) ? " M " : maze.isGoal(x, y) ? " G " : "   ");
    report("%s%c\n", row, maze.hasWall(maze.W - 1, y, DIR_E) ? '|' : ' ');
  }
  int n = 0;
  for (int x = 0; x < maze.W; x++) n += snprintf(row + n, sizeof(row) - n, "+%s", maze.hasWall(x, 0, DIR_S) ? "---" : "   ");
  report("%s+\n", row);
}

// ============================================================================
//  ARDUINO ENTRY POINTS
// ============================================================================
void setup() {
  Serial.begin(115200); delay(400);
  Serial.println(F("\n=== Micromouse flood-fill mapping - booting ==="));

  xTaskCreate(ledTask, "led", 2048, nullptr, 1, nullptr);
  pinMode(PIN_BOOT_BTN, INPUT_PULLUP);
  showLED(LED_BOOT);

  pinMode(PIN_L_DIR, OUTPUT); pinMode(PIN_R_DIR, OUTPUT);
  ledcAttach(PIN_L_PWM, PWM_FREQ_HZ, PWM_BITS);
  ledcAttach(PIN_R_PWM, PWM_FREQ_HZ, PWM_BITS);
  stopMotors();

  pinMode(PIN_L_ENC_A, INPUT_PULLUP); pinMode(PIN_L_ENC_B, INPUT_PULLUP);
  pinMode(PIN_R_ENC_A, INPUT_PULLUP); pinMode(PIN_R_ENC_B, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(PIN_L_ENC_A), isrLeft,  CHANGE);
  attachInterrupt(digitalPinToInterrupt(PIN_R_ENC_A), isrRight, CHANGE);

  Wire.begin(PIN_SDA, PIN_SCL); Wire.setClock(100000);   // same safe speed the scanner proved works
  loadCal();
  reportCal();
  startSensors();

  printSaved();
  showLED(LED_BOOT);
}

bool bootPressed() {
  if (digitalRead(PIN_BOOT_BTN) != LOW) return false;
  delay(30);
  if (digitalRead(PIN_BOOT_BTN) != LOW) return false;
  while (digitalRead(PIN_BOOT_BTN) == LOW) delay(10);    // wait for release
  return true;
}

void startRun() {
  clearLog();
  maze.begin(MAZE_W, MAZE_H);
  posX = START_X; posY = START_Y; headingDir = START_DIR;
  recoveryAttempts = 0;
  showLED(LED_EXPLORING);
  report("=== mapping run ===\n");
  reportCal();
  report("Ticks per cell = %ld. Goal = centre 2x2. Start (%d,%d) dir %d\n",
         TICKS_PER_CELL, posX, posY, headingDir);
  Serial.println(F("HANDS OFF - starting in 3 s..."));
  delay(START_DELAY_MS);
  calibrateGyro();
  resetGyro();
  running = true;
}

void finishRun(LedState how) {
  stopMotors();
  running = false;
  showLED(how);
  saveLog();
  Serial.println(F("\nSaved. Press BOOT or send 'r' to map again. 'p' prints the saved log."));
}

void loop() {
  if (!running) {
    if (bootPressed()) startRun();
    else if (Serial.available()) {
      char c = Serial.read();
      if (c == 'r') startRun();
      else if (c == 'p') printSaved();
    }
    delay(10);
    return;
  }

  // BOOT while driving = stop now and keep the map so far.
  if (bootPressed()) {
    report("STOP: BOOT pressed.\n");
    printMap();
    finishRun(LED_BLOCKED);
    return;
  }

  // 1) Look around from a standstill and record walls into the map.
  recordWalls();

  // 2) Reached the centre? Then we've mapped a route - show it and stop.
  if (maze.isGoal(posX, posY)) {
    report("\n*** REACHED GOAL - maze route mapped. ***\n");
    printMap();
    finishRun(LED_DONE);
    return;
  }

  // 3) Flood fill and pick the next cell to step into.
  maze.flood();
  int d = maze.bestDir(posX, posY, headingDir);
  if (d < 0) {
    report("STOP: no route to goal from here with the walls seen so far.\n");
    report("(Check for a mis-read wall, or that the start pose is right.)\n");
    printMap();
    finishRun(LED_BLOCKED);
    return;
  }

  // 4) Face that direction and drive one cell, with self-correcting odometry.
  if (!turnToHeading(d)) {
    report("STOP: turn missed its target by more than %.0f deg - stopped instead of driving blind.\n", TURN_FAIL_DEG);
    report("(Re-run calibrate on this surface; send this log.)\n");
    printMap();
    finishRun(LED_BLOCKED);
    return;
  }
  int moved = forwardOneCell();
  if (moved == MOVE_OK) {
    posX += DIR_DX[headingDir];
    posY += DIR_DY[headingDir];
    recoveryAttempts = 0;
  } else if (moved == MOVE_BLOCKED) {
    report("  wall right ahead that the map thought was open - recording it and re-planning\n");
    maze.setWall(posX, posY, headingDir);
  } else {
    recoveryAttempts++;
    report("Recovery attempt %d/%d (stalled crossing a cell)\n", recoveryAttempts, MAX_RECOVERY);
    showLED(LED_RECOVER);
    if (recoveryAttempts >= MAX_RECOVERY) {
      report("STOP: gave up after 3 recovery attempts.\n");
      printMap();
      finishRun(LED_BLOCKED);
    }
  }
}
