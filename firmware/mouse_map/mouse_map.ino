/*
 * ============================================================================
 *  MICROMOUSE - MAZE MAPPING with FLOOD FILL  (slow, centred, closed-loop)
 * ============================================================================
 *
 *  Dublin Micromouse Open 2026  -  ESP32-C6 + 3x VL53L0X + MPU-6050 + DRI0044.
 *
 *  Keeps a map of walls, runs flood fill (maze.h) to decide where to go, and
 *  heads for the centre, discovering walls and re-planning as it goes.
 *
 *  Motion is fully closed-loop so it behaves the same on carpet or wood:
 *    - STRAIGHTS: each wheel runs a speed controller on its encoder (it holds
 *      150 mm/s whatever the drag), ramping up from a crawl and back down to a
 *      crawl at the end of every square so it stops where it means to. Heading
 *      is held with the gyro and it centres between the side walls.
 *    - TURNS: the gyro controls the turn RATE, slowing as it nears the target.
 *      If carpet drag holds it back, the controller pushes harder until it
 *      moves, so turns never stall short or fling past.
 *    - SELF-CHECK: every run starts with a small wiggle that detects which way
 *      the gyro and each encoder count, so nothing has to be set by hand.
 *    - WALLS: in the start square (walls both sides) it measures what "centred"
 *      reads on each side sensor, and centres to that.
 *    - A turn that misses badly stops the run instead of driving into a wall,
 *      and a wall found right in front never counts as moving a square, so the
 *      map can't get out of step with where the mouse really is.
 *
 *  Runs cable-free:
 *    1. Power it from the battery. Put it CENTRED in the start square with the
 *       outer wall on its LEFT, facing the open side.
 *    2. Press BOOT and let go. Hands off: it waits 3 s, calibrates the gyro,
 *       wiggles, then maps.
 *    3. Onboard LED:  dim white = ready, blue flashing = mapping,
 *       green = reached the centre, red = stopped (reason in the log),
 *       red flashing = hardware error.
 *       Press BOOT while it's driving to stop it and keep the map so far.
 *    4. Plug in USB, open Serial Monitor at 115200: it prints the saved log of
 *       the last run (why it stopped + the map). Send 'p' if nothing shows.
 *  It never starts moving by itself, so plugging USB in (which can reset the
 *  board) is safe. The calibrate sketch is no longer needed. Needs the Pololu
 *  "VL53L0X" library. Tested in firmware/sim/robot_sim.cpp before flashing.
 * ============================================================================
 */

#include <Wire.h>
#include <VL53L0X.h>
#include <Preferences.h>
#include <stdarg.h>
#include "maze.h"

// ============================================================================
//  PINS
// ============================================================================
const int PIN_SDA = 6, PIN_SCL = 7;
const int     XSHUT[3]       = {  18, 19, 20 };
const char   *SENSOR_NAME[3] = { "LEFT",  "FRONT", "RIGHT" };
const uint8_t SENSOR_ADDR[3] = { 0x30,    0x31,    0x32   };
enum { S_LEFT = 0, S_FRONT = 1, S_RIGHT = 2 };

const int PIN_L_DIR = 0, PIN_L_PWM = 2;
const int PIN_R_DIR = 3, PIN_R_PWM = 10;
const int L_DIR_SIGN = +1, R_DIR_SIGN = -1;     // from motor_encoder_test 'd'

const int PIN_L_ENC_A = 21, PIN_L_ENC_B = 22;
const int PIN_R_ENC_A = 23, PIN_R_ENC_B = 11;

const int STATUS_RGB_PIN = 8;                   // onboard RGB LED (DevKitC-1)
const int PIN_BOOT_BTN = 9;                     // onboard BOOT button, LOW when pressed
const unsigned long START_DELAY_MS = 3000;      // time to take your hand away

// ============================================================================
//  GEOMETRY
// ============================================================================
const float CELL_MM = 180.0, WHEEL_DIAMETER_MM = 44.0, ENC_TICKS_PER_REV = 402.0;
const float MM_PER_TICK = (PI * WHEEL_DIAMETER_MM) / ENC_TICKS_PER_REV;
const int   PWM_FREQ_HZ = 20000, PWM_BITS = 8, PWM_MAX = 255;

// ============================================================================
//  STRAIGHTS - per-wheel speed control (mm/s)
// ============================================================================
const float CRUISE_MM_S  = 150.0;   // slow on purpose
const float CRAWL_MM_S   = 45.0;    // speed at the very start and end of a move
const float ACCEL_MM     = 40.0;    // ramp up over the first 40 mm
const float DECEL_MM     = 60.0;    // ramp down over the last 60 mm
const float STOP_TOL_MM  = 2.0;
const float FF_DEAD_FRAC = 0.8;     // feed-forward: this much of the dead-band PWM...
const float KF_V = 0.16;            // ...plus this many PWM per mm/s
const float KP_V = 0.15;            // PWM per mm/s of speed error
const float KI_V = 1.5;             // PWM per mm of accumulated speed error
const float I_V_MAX = 90.0;
const unsigned long STALL_MS = 1500;   // no progress for this long = stuck

// Steering: output is a left-right SPEED difference in mm/s (+ = turn right).
const float KH = 4.0;               // per degree of heading error
const float KD = 0.25;              // per deg/s of turn rate (damping)
const float KC = 2.0;               // per mm off-centre, both walls
const float KS = 2.0;               // per mm off-centre, one wall
const float STEER_MAX_FRAC = 0.5;   // never more than half the forward speed

// ============================================================================
//  TURNS - gyro rate control
// ============================================================================
const float TURN_DPS      = 120.0;  // max turn rate - slow and controlled
const float TURN_MIN_DPS  = 30.0;   // creep rate for the last few degrees
const float TURN_KP_ANGLE = 4.0;    // deg/s of turn rate per degree still to go
const float TURN_DONE_DEG = 1.5;
const float KF_T = 0.12;            // PWM per deg/s (feed-forward)
const float KP_T = 0.10;            // PWM per deg/s of rate error
const float KI_T = 1.2;             // PWM per degree of accumulated rate error
const float I_T_MAX = 120.0;
const float KP_BAL = 1.0;           // PWM per encoder tick of forward/back creep during a turn
const float KI_BAL = 8.0;
const float I_BAL_MAX = 60.0;
const unsigned long TURN_TIMEOUT_MS = 5000;
const float TURN_FAIL_DEG = 20.0;   // still this far off = stop, don't drive blind

// ============================================================================
//  WALLS (mm) - side values are learned in the start square
// ============================================================================
const int   MAX_VALID_MM     = 1200;
const int   FRONT_WALL_MM    = 120;     // wall ahead of this cell if front < this
const int   FRONT_PIN_MM     = 110;     // wall within this of the stop point = it ends the destination cell
const int   MAX_OVERRUN_MM   = 60;      // never drive further than this past the odometry cell end
const int   FRONT_STOP_DEF   = 25;
const float POST_WIN_MIN = 20, POST_WIN_MAX = 170;   // where in a move the post between cells can show up
const float POST_MAX_FIX = 50;      // ignore a post that disagrees with the count by more than this      // safety stop if it couldn't learn the centred front reading
const int   SIDE_WALL_MARGIN = 45;      // side wall if reading < centred reading + this
const int   SIDE_TRUST_MARGIN = 25;     // only centre off a wall this close
const int   SIDE_DEFAULT_MM  = 60;      // used only if it can't learn in the start square

// ============================================================================
//  IMU
// ============================================================================
const uint8_t MPU_ADDR = 0x68, MPU_PWR_MGMT_1 = 0x6B, MPU_GYRO_CONFIG = 0x1B, MPU_GYRO_ZOUT_H = 0x47;
const float   GYRO_LSB_PER_DPS = 32.8;      // +-1000 dps range
const int     GYRO_CAL_SAMPLES = 800;

// ============================================================================
//  MAZE
// ============================================================================
const int MAZE_W = 16, MAZE_H = 16;
const int START_X = 0, START_Y = 0, START_DIR = DIR_N;
const int MAX_RECOVERY = 3;

// forwardOneCell() results.
const int MOVE_OK = 1, MOVE_STALLED = 0, MOVE_BLOCKED = -1;

// ============================================================================
//  STATE
// ============================================================================
// Types used in function signatures must be defined before any function: the
// Arduino IDE auto-inserts function prototypes above the first function.
enum LedState { LED_BOOT, LED_EXPLORING, LED_TURNING, LED_RECOVER, LED_BLOCKED, LED_ERROR, LED_DONE };
enum LedMode  { MODE_READY, MODE_RUNNING, MODE_GOAL, MODE_STOPPED, MODE_FAULT };

VL53L0X laser[3];
Maze<16, 16> maze;

volatile long countL = 0, countR = 0;
int   encSignL = +1, encSignR = +1, gyroSign = +1;      // detected by selfCheck()
int   deadL = 50, deadR = 50;                           // dead-band PWM (calibrate's, if saved)

int   posX = START_X, posY = START_Y, headingDir = START_DIR;
float gyroBiasRaw = 0.0, gyroAngle = 0.0, lastGyroZ = 0.0;
unsigned long lastGyroUs = 0;

int   distL = MAX_VALID_MM, distF = MAX_VALID_MM, distR = MAX_VALID_MM;
int   setL = SIDE_DEFAULT_MM, setR = SIDE_DEFAULT_MM;   // centred side readings
float frontStopMm = FRONT_STOP_DEF;

float lastTravelMm = 0;
bool  startTrusted = true;          // this move starts from a known-good spot (placed, or lined up on a wall)
float postOdo[2][2];                // [left/right][0 = wall ends, 1 = wall starts]: count at the post
int   postN[2][2];
int   recoveryAttempts = 0;
bool  running = false;

LedState ledState = LED_BOOT;
volatile LedMode ledMode = MODE_READY;

// Mapping prints a lot, so keep only the most recent part - that's where the
// map and the reason it stopped are. Saved to flash at the end of a run.
const size_t LOG_CAP = 3800;                // flash strings max out at 4000 bytes
char   logRing[LOG_CAP];
size_t logHead = 0;
bool   logWrapped = false;

void IRAM_ATTR isrLeft()  { if (digitalRead(PIN_L_ENC_A) == digitalRead(PIN_L_ENC_B)) countL++; else countL--; }
void IRAM_ATTR isrRight() { if (digitalRead(PIN_R_ENC_A) == digitalRead(PIN_R_ENC_B)) countR++; else countR--; }
long tL() { return encSignL * countL; }         // + = that wheel rolled forward
long tR() { return encSignR * countR; }

// ============================================================================
//  LOG / LED / STATE
// ============================================================================
void stopMotors();

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
    if (s != LED_EXPLORING && s != LED_TURNING) report("[state] %s\n", n);
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
//  MOTORS  (raw PWM; the controllers above do all the compensating)
// ============================================================================
void motorWrite(int dirPin, int pwmPin, int dirSign, int spd) {
  if (spd == 0) { ledcWrite(pwmPin, 0); return; }
  int mag = min(abs(spd), PWM_MAX);
  digitalWrite(dirPin, (spd * dirSign) > 0 ? HIGH : LOW);
  ledcWrite(pwmPin, mag);
}
void setMotors(int l, int r) {
  motorWrite(PIN_L_DIR, PIN_L_PWM, L_DIR_SIGN, l);
  motorWrite(PIN_R_DIR, PIN_R_PWM, R_DIR_SIGN, r);
}
void stopMotors() { ledcWrite(PIN_L_PWM, 0); ledcWrite(PIN_R_PWM, 0); }

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
  if (!readGyroRaw(raw)) return lastGyroZ;
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
  report("Gyro bias %.3f dps\n", gyroBiasRaw);
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

// Dead-band from the calibrate sketch, if it was ever run. Everything else it
// used to learn is now handled live by the controllers.
void loadDeadband() {
  Preferences p;
  if (p.begin("mousecal", true)) {
    if (p.getBool("ok", false)) { deadL = p.getInt("minL", deadL); deadR = p.getInt("minR", deadR); }
    p.end();
  }
  deadL = constrain(deadL, 20, 120); deadR = constrain(deadR, 20, 120);
}

// ============================================================================
//  SENSORS
// ============================================================================
int readDist(int i) {
  uint16_t r = laser[i].readRangeContinuousMillimeters();
  if (laser[i].timeoutOccurred() || r == 0 || r > MAX_VALID_MM) return MAX_VALID_MM;
  return (int)r;
}
// Median of 5 reads while stopped, for a trustworthy wall decision. A median,
// not an average: the VL53L0X sometimes drops a reading (comes back as
// MAX_VALID_MM), and one of those in an average hides a wall that's right there.
int readDistStable(int i) {
  int r[5];
  for (int k = 0; k < 5; k++) { r[k] = readDist(i); delay(6); }
  for (int a = 1; a < 5; a++)
    for (int b = a; b > 0 && r[b] < r[b - 1]; b--) { int tmp = r[b]; r[b] = r[b - 1]; r[b - 1] = tmp; }
  return r[2];
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
    report("Sensor %-5s OK at 0x%02X\n", SENSOR_NAME[i], SENSOR_ADDR[i]);
  }
  // Start ranging only once all three are addressed, so none is busy while another boots.
  for (int i = 0; i < 3; i++) laser[i].startContinuous();
  if (!mpuWrite(MPU_PWR_MGMT_1, 0x00)) halt("MPU-6050 not responding: check SDA/SCL/VIN/GND");
  mpuWrite(MPU_GYRO_CONFIG, 0x10);   // +-1000 dps, must match GYRO_LSB_PER_DPS
  delay(50);
  report("IMU OK at 0x68\n");
}

// ============================================================================
//  CONTROLLERS
// ============================================================================
// One wheel: speed (mm/s, signed) -> PWM. Feed-forward gets it close, the PI
// term makes it exact whatever the floor is doing.
int wheelPwm(float target, float measured, float &integ, int dead, float dt) {
  if (fabs(target) < 1.0f) { integ = 0; return 0; }
  float err = target - measured;
  integ = constrain(integ + KI_V * err * dt, -I_V_MAX, I_V_MAX);
  float pwm = (target > 0 ? 1 : -1) * dead * FF_DEAD_FRAC + KF_V * target + KP_V * err + integ;
  return (int)constrain(pwm, (float)-PWM_MAX, (float)PWM_MAX);
}

// Left-right speed difference (mm/s, + = turn right) to hold heading and centre.
float steering(bool useWalls) {
  float s = KH * gyroAngle + KD * lastGyroZ;
  if (useWalls) {
    bool wl = distL < setL + SIDE_TRUST_MARGIN, wr = distR < setR + SIDE_TRUST_MARGIN;
    float offL = distL - setL, offR = distR - setR;   // - = closer than centred
    if (wl && wr)  s += KC * (offR - offL) * 0.5f;
    else if (wl)   s -= KS * offL;
    else if (wr)   s += KS * offR;
  }
  return s;
}

// Drive `mm` in a straight line (negative = reverse). Forward moves use the
// walls to centre, the front sensor to stop, and side-wall posts to correct
// the distance count.
int driveStraight(float mm, bool forwardCell) {
  int dir = (mm > 0) ? 1 : -1;
  float goal = fabs(mm);
  long sL = tL(), sR = tR(), pL = sL, pR = sR;
  float iL = 0, iR = 0, best = 0, trav = 0, corr = 0;
  bool corrected = false;
  int side[2] = { -1, -1 }, pend[2] = { -1, -1 }, pendN[2] = { 0, 0 };
  int fStart = -1;
  resetGyro();
  unsigned long tPrev = micros(), lastProg = millis();

  while (true) {
    updateGyro();
    if (forwardCell) readAll(); else delay(10);
    unsigned long now = micros();
    float dt = (now - tPrev) * 1e-6f;
    if (dt < 0.004f) continue;
    tPrev = now;

    long cL = tL(), cR = tR();
    float vL = (cL - pL) * MM_PER_TICK / dt, vR = (cR - pR) * MM_PER_TICK / dt;
    pL = cL; pR = cR;
    float odo = dir * ((cL - sL) + (cR - sR)) * 0.5f * MM_PER_TICK;

    if (forwardCell) {
      // POSTS: a side wall starting or ending happens at the post between this
      // cell and the next - a fixed spot. Learn the distance count at which each
      // kind of edge shows up (from moves that started from a known-good spot),
      // then snap the count to it whenever the start was less certain.
      // An edge must hold for 2 reads so a sensor drop-out can't fake one.
      int rd[2] = { distL, distR }, sp[2] = { setL, setR };
      for (int k = 0; k < 2; k++) {
        int st = (rd[k] < sp[k] + SIDE_WALL_MARGIN) ? 1 : 0;
        if (side[k] < 0) { side[k] = st; continue; }
        if (st == side[k]) { pend[k] = -1; pendN[k] = 0; continue; }
        if (pend[k] == st) pendN[k]++; else { pend[k] = st; pendN[k] = 1; }
        if (pendN[k] < 2) continue;
        side[k] = st; pend[k] = -1; pendN[k] = 0;
        if (odo < POST_WIN_MIN || odo > POST_WIN_MAX || corrected) continue;
        float &learned = postOdo[k][st];
        if (startTrusted) {
          learned = postN[k][st] ? 0.7f * learned + 0.3f * odo : odo;
          postN[k][st]++;
        } else if (postN[k][st] > 0 && fabs(learned - odo) < POST_MAX_FIX) {
          corr = learned - odo;
          corrected = true;
        }
      }
      // STUCK: a wall within a cell ahead isn't getting closer although the
      // wheels say we moved - wheels slipping against something. Don't count a
      // cell. (Only a near wall: far away, the sensor's wide beam catches the
      // side walls instead, and that reading travels along with the mouse.)
      if (fStart < 0 && odo < 20 && distF < 230) fStart = distF;
      if (fStart > 0 && odo > 80 && fStart - distF < 30 && distF < MAX_VALID_MM) {
        stopMotors(); settle(); startTrusted = false;
        report("  stuck: wheels turning but the wall ahead isn't getting closer\n");
        return MOVE_STALLED;
      }
    }
    trav = odo + corr;
    lastTravelMm = trav;

    if (forwardCell && distF < frontStopMm) {
      stopMotors(); settle(); startTrusted = true;
      // Stopped by a wall before really leaving this cell: it did NOT move a
      // cell. Counting it as one is what corrupts the map after a bad turn.
      return (trav < CELL_MM / 3) ? MOVE_BLOCKED : MOVE_OK;
    }
    float left = goal - trav;
    // A wall at the far end of the destination cell pins exactly where the cell
    // centre is, wiping out distance drift (carpet slip): keep crawling until the
    // front reading says "centred". Otherwise odometry decides, as it must.
    bool pinned = forwardCell && distF < frontStopMm + FRONT_PIN_MM && left < CELL_MM / 2;
    if (!pinned && left <= STOP_TOL_MM) {
      stopMotors(); settle();
      if (forwardCell) startTrusted = corrected;
      return MOVE_OK;
    }
    if (pinned && left < -MAX_OVERRUN_MM) { stopMotors(); settle(); startTrusted = false; return MOVE_OK; }

    float v = CRUISE_MM_S;
    v = min(v, CRAWL_MM_S + (CRUISE_MM_S - CRAWL_MM_S) * max(0.0f, left) / DECEL_MM);
    v = min(v, CRAWL_MM_S + (CRUISE_MM_S - CRAWL_MM_S) * max(0.0f, trav) / ACCEL_MM);
    if (forwardCell && distF < MAX_VALID_MM) v = min(v, CRAWL_MM_S + (distF - frontStopMm) * 2.0f);
    v = max(v, CRAWL_MM_S);

    float s = steering(forwardCell);
    s = constrain(s, -STEER_MAX_FRAC * v, STEER_MAX_FRAC * v);
    setMotors(wheelPwm(dir * v + s, vL, iL, deadL, dt), wheelPwm(dir * v - s, vR, iR, deadR, dt));

    if (trav > best + 5) { best = trav; lastProg = millis(); }
    if (millis() - lastProg > STALL_MS) { stopMotors(); settle(); startTrusted = false; return MOVE_STALLED; }
  }
}

int forwardOneCell() {
  showLED(LED_EXPLORING);
  int r = driveStraight(CELL_MM, true);
  if (r == MOVE_STALLED) {
    report("  stuck after %.0f mm - backing up to the cell centre\n", lastTravelMm);
    if (lastTravelMm > 5) driveStraight(-lastTravelMm, false);
  }
  return r;
}

// Turn in place by `degrees` (+ = left/CCW). The gyro sets the turn RATE,
// slowing as it gets close; the integral term pushes harder if carpet holds it
// back. The encoders keep the two wheels moving equal and opposite, so it spins
// about its centre even though one motor needs more power than the other.
// Returns where it actually ended up.
float turnInPlace(float degrees) {
  showLED(LED_TURNING);
  resetGyro();
  float integ = 0, balI = 0;
  int lastSign = 0;
  int dead = (deadL + deadR) / 2;
  long sL = tL(), sR = tR();
  unsigned long t0 = millis(), tPrev = micros();
  bool timedOut = true;
  while (millis() - t0 < TURN_TIMEOUT_MS) {
    updateGyro();
    float rem = degrees - gyroAngle;
    if (fabs(rem) < TURN_DONE_DEG) { timedOut = false; break; }
    unsigned long now = micros();
    float dt = (now - tPrev) * 1e-6f; tPrev = now;
    int s = (rem > 0) ? 1 : -1;
    if (s != lastSign) { integ = 0; lastSign = s; }        // reversing: start fresh
    float w = s * constrain(TURN_KP_ANGLE * fabs(rem), TURN_MIN_DPS, TURN_DPS);
    float err = w - lastGyroZ;
    integ = constrain(integ + KI_T * err * dt, -I_T_MAX, I_T_MAX);
    float p = s * dead * FF_DEAD_FRAC + KF_T * w + KP_T * err + integ;
    // Net forward creep (ticks): push both wheels back against it.
    float drift = (float)((tL() - sL) + (tR() - sR));
    balI = constrain(balI + KI_BAL * drift * dt, -I_BAL_MAX, I_BAL_MAX);
    float c = -(KP_BAL * drift + balI);
    setMotors((int)constrain(-p + c, (float)-PWM_MAX, (float)PWM_MAX),
              (int)constrain(+p + c, (float)-PWM_MAX, (float)PWM_MAX));
    delay(2);
  }
  unsigned long ms = millis() - t0;
  stopMotors(); settle();
  report("  turn %+.0f -> %+.1f (%lu ms%s)\n", degrees, gyroAngle, ms, timedOut ? ", TIMED OUT" : "");
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
//  START-OF-RUN CHECKS
// ============================================================================
// Small left wiggle: works out which way the gyro and each encoder count, so
// none of it depends on settings. Then turns back.
void selfCheck() {
  report("Self-check wiggle...\n");
  gyroSign = +1; encSignL = encSignR = +1;
  long sL = countL, sR = countR;
  resetGyro();
  unsigned long t0 = millis();
  // Ramp each wheel's power on its own until THAT wheel moves, so both take
  // part even when one motor needs much more power to get going.
  int pL = (deadL + deadR) / 2, pR = pL;
  while (millis() - t0 < 3000) {
    updateGyro();
    bool movedL = labs(countL - sL) >= 8, movedR = labs(countR - sR) >= 8;
    if (movedL && movedR && fabs(gyroAngle) >= 15) break;
    if (!movedL) pL = min(pL + 1, PWM_MAX);
    if (!movedR) pR = min(pR + 1, PWM_MAX);
    setMotors(-pL, +pR);                                            // commanded: left turn
    delay(8);
  }
  stopMotors(); settle();
  float a = gyroAngle;
  long dL = countL - sL, dR = countR - sR;
  report("  gyro %+.1f deg | left enc %+ld | right enc %+ld\n", a, dL, dR);
  if (fabs(a) < 8) halt("Self-check: the mouse didn't rotate. Check motor power and directions.");
  if (labs(dL) < 5) halt("Self-check: LEFT encoder isn't counting. Check its wires/power.");
  if (labs(dR) < 5) halt("Self-check: RIGHT encoder isn't counting. Check its wires/power.");
  gyroSign = (a > 0) ? +1 : -1;               // a left turn must read positive
  encSignL = (dL < 0) ? +1 : -1;              // left wheel went backward
  encSignR = (dR > 0) ? +1 : -1;              // right wheel went forward
  report("  gyro sign %+d, encoder signs L %+d R %+d\n", gyroSign, encSignL, encSignR);
  turnInPlace(-fabs(a));                      // back to where it started
  // One motor needs more power, so the wiggle pivots off-centre and shifts the
  // mouse a little: drive that shift back out.
  float shift = 0.5f * (encSignL * dL + encSignR * dR) * MM_PER_TICK;
  if (fabs(shift) > 3) { report("  undoing %.0f mm shift\n", shift); driveStraight(-shift, false); }
}

// Placed centred between two walls in the start square: learn what "centred"
// reads on each side sensor, so centring works whatever the sensor mounting.
void learnSides() {
  int dl = readDistStable(S_LEFT), dr = readDistStable(S_RIGHT);
  if (dl < 150 && dr < 150) {
    setL = dl; setR = dr;
    report("Centred side readings: L %d  R %d mm\n", setL, setR);
    if (abs(dl - dr) > 30) report("  (uneven - was it placed centred? continuing)\n");
  } else {
    report("WARNING: no walls both sides at the start (L %d R %d) - using %d mm\n", dl, dr, SIDE_DEFAULT_MM);
  }
}

// The start square always has a wall on its right. Still centred, turn to face
// it and read the front sensor: that's exactly what "centred in a cell" reads,
// so every stop at a wall ahead lands in the middle of the cell. Then turn back.
void learnFront() {
  turnInPlace(-90.0);
  int df = readDistStable(S_FRONT);
  if (df < 150) {
    frontStopMm = df;
    report("Centred front reading: %d mm\n", df);
  } else {
    report("WARNING: no wall right of the start square (F %d) - front stop %d mm\n", df, FRONT_STOP_DEF);
  }
  turnInPlace(+90.0);
}

// ============================================================================
//  MAP: record what the three sensors see into the maze (must be stopped)
// ============================================================================
void recordWalls() {
  int dl = readDistStable(S_LEFT), df = readDistStable(S_FRONT), dr = readDistStable(S_RIGHT);
  distL = dl; distF = df; distR = dr;
  bool wf = df < FRONT_WALL_MM, wl = dl < setL + SIDE_WALL_MARGIN, wr = dr < setR + SIDE_WALL_MARGIN;
  if (wf) maze.setWall(posX, posY, headingDir);
  if (wl) maze.setWall(posX, posY, dirLeft(headingDir));
  if (wr) maze.setWall(posX, posY, dirRight(headingDir));
  report("cell (%d,%d) dir %d | L%4d F%4d R%4d | walls %c%c%c\n",
         posX, posY, headingDir, dl, df, dr, wf ? 'F' : '.', wl ? 'L' : '.', wr ? 'R' : '.');
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
//  RUN CONTROL
// ============================================================================
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
  frontStopMm = FRONT_STOP_DEF;
  startTrusted = true;
  memset(postN, 0, sizeof(postN));
  showLED(LED_EXPLORING);
  report("=== mapping run ===  dead-band L %d R %d\n", deadL, deadR);
  Serial.println(F("HANDS OFF - starting in 3 s..."));
  delay(START_DELAY_MS);
  calibrateGyro();
  learnSides();
  selfCheck();
  learnFront();
  running = true;
}

void finishRun(LedState how) {
  stopMotors();
  running = false;
  showLED(how);
  saveLog();
  Serial.println(F("\nSaved. Press BOOT or send 'r' to map again. 'p' prints the saved log."));
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
  loadDeadband();
  startSensors();

  printSaved();
  showLED(LED_BOOT);
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

  // 4) Face that direction and drive one cell.
  if (!turnToHeading(d)) {
    report("STOP: turn missed its target by more than %.0f deg - stopped instead of driving blind.\n", TURN_FAIL_DEG);
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
