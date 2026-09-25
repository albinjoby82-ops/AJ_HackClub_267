/*
 * ============================================================================
 *  MICROMOUSE - SLOW MAZE EXPLORATION  (exploration only)
 * ============================================================================
 *
 *  Dublin Micromouse Open 2026  -  ESP32-C6 + 3x VL53L0X + MPU-6050 + DRI0044.
 *
 *  GOAL of this sketch: drive the mouse smoothly and slowly through the maze,
 *  keeping itself centred between the walls, taking sensible turns, and never
 *  crashing into a wall. It explores using the classic LEFT-HAND rule (keep a
 *  wall on your left). That rule always has a legal move, so the mouse keeps
 *  going - it does not stop and give up unless it is *physically* stuck.
 *
 *  It is deliberately light so an ESP32-C6 can run the whole control loop:
 *      - Pololu VL53L0X library for the three ToF sensors (continuous mode).
 *      - Raw register reads for the MPU-6050 gyro (no heavy DMP / no float
 *        matrix maths) - just gyro-Z integrated into a heading for turns and
 *        for holding a straight line when there are no side walls to hug.
 *      - Pin-change interrupts for the wheel encoders (distance + wheel match).
 *
 *  SENSORS AND WHAT EACH ONE IS FOR:
 *      LEFT  ToF  (0x30) - is there a wall on the left?  + centring
 *      FRONT ToF (0x31) - is there a wall ahead? + stop before crashing
 *      RIGHT ToF (0x32) - is there a wall on the right? + centring
 *      MPU-6050  (0x68) - gyro heading for accurate 90/180 turns and for
 *                          driving straight through gaps with no side walls
 *      Encoders          - how far a cell is (180 mm) and keeping wheels even
 *
 *  BEFORE YOU DRIVE:
 *      1. Run the i2c_scanner sketch first. All 4 devices must show FOUND.
 *      2. Set every pin in the CONFIG block to match your wiring.
 *      3. MEASURE and set ENC_TICKS_PER_REV and WHEEL_DIAMETER_MM (see H6).
 *      4. Put the wheels off the table for the first flash and watch Serial.
 *      5. Tune the wall thresholds on the REAL maze walls (see H4 / S4).
 *
 *  Every stop prints a reason on Serial at 115200. You should never have to
 *  guess why the mouse halted.
 *
 *  Needs the "VL53L0X" library by Pololu (Library Manager -> search VL53L0X).
 * ============================================================================
 */

#include <Wire.h>
#include <VL53L0X.h>

// ============================================================================
//  CONFIG  -  everything you are meant to change lives here.
// ============================================================================

// --- I2C bus pins -----------------------------------------------------------
const int PIN_SDA = 6;
const int PIN_SCL = 7;

// --- VL53L0X XSHUT pins + names + addresses (order must line up) ------------
//     Avoid ESP32-C6 strapping pins (4,5,8,9,15) and USB pins (12,13).
const int     XSHUT[3]       = {  18, 19, 20 };
const char   *SENSOR_NAME[3] = { "LEFT",  "FRONT", "RIGHT" };
const uint8_t SENSOR_ADDR[3] = { 0x30,    0x31,    0x32   };
enum { LEFT = 0, FRONT = 1, RIGHT = 2 };   // index names

// --- DRI0044 motor driver pins ---------------------------------------------
//     Each motor: one direction pin + one PWM (speed) pin.
const int PIN_L_DIR = 0;
const int PIN_L_PWM = 2;
const int PIN_R_DIR = 3;
const int PIN_R_PWM = 10;

// If a wheel drives the wrong way, flip its sign here (or swap its motor wires).
const int L_DIR_SIGN = +1;
const int R_DIR_SIGN = -1;

// --- Wheel encoder pins (A and B per wheel) --------------------------------
const int PIN_L_ENC_A = 21;
const int PIN_L_ENC_B = 22;
const int PIN_R_ENC_A = 11;
const int PIN_R_ENC_B = 23;

// --- Status LED (a plain LED to a GPIO through a resistor). Optional. -------
//     Set to -1 if you have no status LED; states still print on Serial.
const int PIN_STATUS_LED = -1;

// --- PWM setup (ESP32 LEDC) -------------------------------------------------
const int      PWM_FREQ_HZ = 20000;   // above hearing, easy on the driver
const int      PWM_BITS    = 8;       // 0..255 duty
const int      PWM_MAX     = (1 << PWM_BITS) - 1;

// --- Speeds (0..PWM_MAX). Keep them low - this is *slow* exploration. ------
const int CRUISE_PWM   = 90;    // forward cruise
const int TURN_PWM     = 85;    // in-place turning
const int BACKUP_PWM   = 80;    // reversing during recovery
const int MIN_MOVE_PWM = 45;    // below this a wheel may just buzz, not move

// --- Geometry - MEASURE THESE (see guide H6). Cell is 180 mm. ---------------
const float CELL_MM             = 180.0;  // maze cell pitch
const float WHEEL_DIAMETER_MM   = 44.0;   // measured
const float ENC_TICKS_PER_REV   = 402.0;  // measured by hand (L 395, R 408)
// Ticks to travel one cell, computed from the above.
const long  TICKS_PER_CELL =
    (long)((CELL_MM * ENC_TICKS_PER_REV) / (PI * WHEEL_DIAMETER_MM) + 0.5);

// --- Wall thresholds in mm - TUNE on the real walls (see H4). ---------------
//     Hysteresis: "present" below NEAR, "absent" above FAR, sticky between.
const int SIDE_WALL_NEAR_MM = 110;   // side wall counts as present below this
const int SIDE_WALL_FAR_MM  = 150;   // side wall counts as absent above this
const int FRONT_WALL_MM     = 130;   // wall ahead counts as blocking below this
const int FRONT_STOP_MM     = 70;    // hard stop: never get closer than this
const int MAX_VALID_MM      = 1200;  // reject readings beyond this (out of range)
const int SIDE_SETPOINT_MM  = 70;    // desired distance to a single hugged wall

// --- Steering gains ---------------------------------------------------------
// Straightness FIRST. Keeping the mouse *parallel* to the corridor is what stops
// it driving into a wall at an angle, and that job belongs to the gyro heading
// (with rate damping) plus keeping the two wheels' tick counts matched - both
// always active. Wall centring is only a gentle lateral trim added on top, and
// only when a side wall is close enough to trust. See steeringCorrection().
const float KP_HEAD   = 3.0;    // heading hold: PWM per degree of yaw error
const float KD_HEAD   = 0.4;    // heading damping: PWM per (deg/s) of yaw rate
const float KP_ENC    = 0.5;    // wheel-match: PWM per tick of left-minus-right
const float KP_CENTER = 0.25;   // centring between two walls: PWM per mm
const float KP_SIDE   = 0.30;   // hugging a single wall: PWM per mm
const int   WALL_TRUST_MM = 90; // only centre off a side wall this close or nearer
const int   CORR_MAX  = 55;     // clamp on the total steering correction

// --- Turn control -----------------------------------------------------------
const float TURN_SLOW_ZONE_DEG = 25.0;  // slow down within this of the target
const unsigned long TURN_TIMEOUT_MS = 3000;

// --- Recovery / stall -------------------------------------------------------
const int           MAX_RECOVERY   = 3;     // give up (loudly) after this many
const long          STALL_TICKS    = 3;     // "progress" = at least this many ticks
const unsigned long STALL_MS       = 700;   // no progress for this long = stalled
const unsigned long CELL_TIMEOUT_MS = 6000; // a single cell should never take this long
const long          BACKUP_TICKS   = TICKS_PER_CELL / 3;

// --- MPU-6050 ---------------------------------------------------------------
const uint8_t MPU_ADDR      = 0x68;
const uint8_t MPU_PWR_MGMT_1 = 0x6B;
const uint8_t MPU_GYRO_ZOUT_H = 0x47;
const float   GYRO_LSB_PER_DPS = 131.0;   // for the default +/-250 dps range
const int     GYRO_SIGN = +1;             // flip to -1 if left turns read negative
const int     GYRO_CAL_SAMPLES = 800;     // averaged at boot for bias

// ============================================================================
//  STATE
// ============================================================================
VL53L0X laser[3];

volatile long countL = 0;   // encoder tick counters (updated in ISRs)
volatile long countR = 0;

int  distLeft = MAX_VALID_MM, distFront = MAX_VALID_MM, distRight = MAX_VALID_MM;
bool wallLeft = false, wallFront = false, wallRight = false;

float gyroBiasZ = 0.0;      // gyro-Z zero offset (dps), found at boot
float heading   = 0.0;      // integrated heading in degrees
float lastGyroZ = 0.0;      // latest yaw rate (dps) - used to damp steering
unsigned long lastHeadingUs = 0;

int  recoveryAttempts = 0;
bool gaveUp = false;

enum LedState { LED_BOOT, LED_EXPLORING, LED_TURNING, LED_RECOVER, LED_BLOCKED, LED_ERROR };
LedState ledState = LED_BOOT;

// ============================================================================
//  ENCODER ISRs  -  count A edges, use B for direction.
// ============================================================================
void IRAM_ATTR isrLeft() {
  if (digitalRead(PIN_L_ENC_A) == digitalRead(PIN_L_ENC_B)) countL++;
  else                                                      countL--;
}
void IRAM_ATTR isrRight() {
  if (digitalRead(PIN_R_ENC_A) == digitalRead(PIN_R_ENC_B)) countR++;
  else                                                      countR--;
}

// ============================================================================
//  STATUS LED / SERIAL STATE
// ============================================================================
void showLED(LedState s) {
  if (s != ledState) {
    ledState = s;
    const char *name = "";
    switch (s) {
      case LED_BOOT:      name = "BOOT";      break;
      case LED_EXPLORING: name = "EXPLORING"; break;
      case LED_TURNING:   name = "TURNING";   break;
      case LED_RECOVER:   name = "RECOVER";   break;
      case LED_BLOCKED:   name = "BLOCKED";   break;
      case LED_ERROR:     name = "ERROR";     break;
    }
    Serial.printf("[state] %s\n", name);
  }
  if (PIN_STATUS_LED < 0) return;
  // Steady-ON for normal running; the blocked/error loops blink separately.
  digitalWrite(PIN_STATUS_LED, (s == LED_EXPLORING || s == LED_TURNING) ? HIGH : LOW);
}

// Blink the LED forever - used only for the two terminal states.
void blinkForever(int onMs, int offMs) {
  while (true) {
    if (PIN_STATUS_LED >= 0) digitalWrite(PIN_STATUS_LED, HIGH);
    delay(onMs);
    if (PIN_STATUS_LED >= 0) digitalWrite(PIN_STATUS_LED, LOW);
    delay(offMs);
  }
}

// Fatal, unrecoverable setup problem: say why, then stop (blink fast).
void halt(const char *why) {
  Serial.printf("HALT: %s\n", why);
  ledState = LED_ERROR;
  stopMotors();
  blinkForever(80, 80);   // never returns
}

// ============================================================================
//  MOTORS
// ============================================================================
void motorWrite(int dirPin, int pwmPin, int dirSign, int signedSpeed) {
  int s = signedSpeed * dirSign;
  bool forward = (s >= 0);
  int mag = abs(s);
  if (mag > PWM_MAX) mag = PWM_MAX;
  if (mag != 0 && mag < MIN_MOVE_PWM) mag = MIN_MOVE_PWM;   // beat static friction
  digitalWrite(dirPin, forward ? HIGH : LOW);
  ledcWrite(pwmPin, mag);
}

// Positive = forward for both wheels.
void setMotors(int left, int right) {
  motorWrite(PIN_L_DIR, PIN_L_PWM, L_DIR_SIGN, left);
  motorWrite(PIN_R_DIR, PIN_R_PWM, R_DIR_SIGN, right);
}

void stopMotors() {
  ledcWrite(PIN_L_PWM, 0);
  ledcWrite(PIN_R_PWM, 0);
}

// ============================================================================
//  MPU-6050 GYRO  (raw registers, kept tiny)
// ============================================================================
bool mpuWrite(uint8_t reg, uint8_t val) {
  Wire.beginTransmission(MPU_ADDR);
  Wire.write(reg);
  Wire.write(val);
  return (Wire.endTransmission() == 0);
}

// Read gyro-Z in degrees/second (bias removed), signed by GYRO_SIGN.
float readGyroZ() {
  Wire.beginTransmission(MPU_ADDR);
  Wire.write(MPU_GYRO_ZOUT_H);
  if (Wire.endTransmission(false) != 0) return 0.0;
  if (Wire.requestFrom((int)MPU_ADDR, 2) != 2) return 0.0;
  int16_t raw = (Wire.read() << 8) | Wire.read();
  return GYRO_SIGN * (raw / GYRO_LSB_PER_DPS) - gyroBiasZ;
}

// Keep the running heading up to date. Call this often.
void updateHeading() {
  unsigned long now = micros();
  float dt = (now - lastHeadingUs) * 1e-6f;
  lastHeadingUs = now;
  if (dt <= 0 || dt > 0.2f) return;   // ignore silly gaps
  lastGyroZ = readGyroZ();            // remember the rate for steering damping
  heading += lastGyroZ * dt;
}

// Sit still and average gyro-Z to find its zero offset. Mouse MUST be still.
void calibrateGyro() {
  Serial.println(F("Calibrating gyro - keep the mouse completely still..."));
  gyroBiasZ = 0.0;
  double sum = 0.0;
  for (int i = 0; i < GYRO_CAL_SAMPLES; ++i) {
    Wire.beginTransmission(MPU_ADDR);
    Wire.write(MPU_GYRO_ZOUT_H);
    Wire.endTransmission(false);
    Wire.requestFrom((int)MPU_ADDR, 2);
    int16_t raw = (Wire.read() << 8) | Wire.read();
    sum += GYRO_SIGN * (raw / GYRO_LSB_PER_DPS);
    delay(2);
  }
  gyroBiasZ = (float)(sum / GYRO_CAL_SAMPLES);
  Serial.printf("Gyro bias Z = %.3f dps\n", gyroBiasZ);
}

// ============================================================================
//  SENSORS
// ============================================================================
int readDist(int i) {
  uint16_t r = laser[i].readRangeContinuousMillimeters();
  if (laser[i].timeoutOccurred() || r == 0 || r > MAX_VALID_MM) return MAX_VALID_MM;
  return (int)r;
}

void updateWall(bool &state, int dist, int nearMM, int farMM) {
  if (dist < nearMM)      state = true;    // clearly a wall
  else if (dist > farMM)  state = false;   // clearly open
  // in between: keep previous state (hysteresis)
}

// Read all three ToF sensors and refresh the wall booleans.
void senseWalls() {
  distLeft  = readDist(LEFT);
  distFront = readDist(FRONT);
  distRight = readDist(RIGHT);
  updateWall(wallLeft,  distLeft,  SIDE_WALL_NEAR_MM, SIDE_WALL_FAR_MM);
  updateWall(wallRight, distRight, SIDE_WALL_NEAR_MM, SIDE_WALL_FAR_MM);
  updateWall(wallFront, distFront, FRONT_WALL_MM,     FRONT_WALL_MM + 20);
}

// ============================================================================
//  SETUP HELPERS
// ============================================================================
void startSensors() {
  // All ToF sensors off first.
  for (int i = 0; i < 3; ++i) {
    pinMode(XSHUT[i], OUTPUT);
    digitalWrite(XSHUT[i], LOW);
  }
  delay(20);

  // Bring each up, give it its own address, start continuous ranging.
  for (int i = 0; i < 3; ++i) {
    digitalWrite(XSHUT[i], HIGH);
    delay(20);
    laser[i].setTimeout(200);
    if (!laser[i].init()) {
      char msg[80];
      snprintf(msg, sizeof(msg),
               "VL53L0X %s init failed: check XSHUT/SDA/SCL/VIN/GND", SENSOR_NAME[i]);
      halt(msg);
    }
    laser[i].setAddress(SENSOR_ADDR[i]);
    // ~33 ms budget: a good balance of speed and accuracy for maze walls.
    if (!laser[i].setMeasurementTimingBudget(33000)) halt("VL53L0X timing budget rejected");
    laser[i].startContinuous();
    // Fix B: say out loud that each sensor came up, so a boot that gets this
    // far can never be mistaken for a sensor that failed silently.
    Serial.printf("Sensor %-5s initialized OK at 0x%02X\n", SENSOR_NAME[i], SENSOR_ADDR[i]);
  }

  // IMU: wake it, then confirm and calibrate.
  if (!mpuWrite(MPU_PWR_MGMT_1, 0x00)) halt("MPU-6050 not responding: check SDA/SCL/VIN/GND");
  delay(50);
  Serial.println(F("IMU (MPU-6050) initialized OK at 0x68"));
  calibrateGyro();
}

// ============================================================================
//  MOTION PRIMITIVES
// ============================================================================

// Compute the steering correction (positive = steer RIGHT) for driving straight
// down a cell. The philosophy (same as the reference mouse): keep the mouse
// PARALLEL first, then trim its lateral position - not the other way round.
//
//   1) Heading hold (ALWAYS): a gyro PD term. Keeps the mouse pointing the way
//      it started the cell, so it never quietly rotates toward a wall. The
//      derivative is just the yaw rate, which damps the weave.
//   2) Wheel match (ALWAYS): keep left and right ticks equal. Equal wheel
//      travel is a straight line, and it catches slow curve the gyro misses.
//   3) Wall centring (ONLY when a wall is close enough to trust): a gentle
//      lateral trim. Skipped when walls are far/open so a wall that ends can't
//      yank the steering. When one wall is present, hold the setpoint off it.
//
// Terms 1 and 2 provide the damping, so the wall term can stay a simple P.
int steeringCorrection(long dL, long dR, float targetHeading) {
  // 1) Heading hold + rate damping. If yawed left (heading > target) or yawing
  //    left now (rate > 0), steer right (positive).
  float corr = KP_HEAD * (heading - targetHeading) + KD_HEAD * lastGyroZ;

  // 2) Wheel match. If the left wheel ran ahead (dL > dR) the mouse is curving
  //    right, so steer left (negative).
  corr += KP_ENC * (float)(dR - dL);

  // 3) Wall centring trim, only off walls we can trust this iteration.
  bool trustL = (distLeft  < WALL_TRUST_MM);
  bool trustR = (distRight < WALL_TRUST_MM);
  if (trustL && trustR) {
    corr += KP_CENTER * (distRight - distLeft);        // pull toward the middle
  } else if (trustL) {
    corr += KP_SIDE * (SIDE_SETPOINT_MM - distLeft);   // too close to left -> steer right
  } else if (trustR) {
    corr -= KP_SIDE * (SIDE_SETPOINT_MM - distRight);  // too close to right -> steer left
  }
  // else: no trustworthy wall - ride the heading hold straight through the gap.

  if (corr >  CORR_MAX) corr =  CORR_MAX;
  if (corr < -CORR_MAX) corr = -CORR_MAX;
  return (int)corr;
}

// Drive forward exactly one maze cell, staying centred and never crashing.
// Returns true if it completed (or reached a wall ahead), false if it stalled.
bool driveOneCell() {
  long startL = countL, startR = countR;
  float targetHeading = heading;      // hold the heading we start this cell on
  unsigned long t0 = millis();
  unsigned long lastProgressMs = t0;
  long bestProgress = 0;

  showLED(LED_EXPLORING);

  while (true) {
    updateHeading();
    senseWalls();

    long dL = labs(countL - startL);
    long dR = labs(countR - startR);
    long avg = (dL + dR) / 2;

    // Done: we've covered a full cell.
    if (avg >= TICKS_PER_CELL) { stopMotors(); break; }

    // Safety: a wall is right in front - stop before touching it.
    if (distFront < FRONT_STOP_MM) { stopMotors(); break; }

    int corr = steeringCorrection(dL, dR, targetHeading);
    setMotors(CRUISE_PWM + corr, CRUISE_PWM - corr);

    // Progress / stall tracking.
    if (avg > bestProgress + STALL_TICKS) { bestProgress = avg; lastProgressMs = millis(); }
    if (millis() - lastProgressMs > STALL_MS) { stopMotors(); return false; }
    if (millis() - t0 > CELL_TIMEOUT_MS)      { stopMotors(); return false; }

    delay(5);   // gentle pacing; sensors are the real rate limiter
  }

  recoveryAttempts = 0;   // a completed cell means we are not stuck
  return true;
}

// Turn in place by 'degrees' (positive = LEFT / CCW) using the gyro, with a
// timeout fallback so a dead gyro can never hang the mouse forever.
void turnInPlace(float degrees) {
  showLED(LED_TURNING);
  heading = 0.0;                 // measure this turn relative to now
  lastHeadingUs = micros();
  unsigned long t0 = millis();
  float target = degrees;

  while (millis() - t0 < TURN_TIMEOUT_MS) {
    updateHeading();
    float remaining = target - heading;
    if (fabs(remaining) < 2.0) break;          // close enough

    // Slow down as we approach the target for a clean stop.
    int pwm = TURN_PWM;
    if (fabs(remaining) < TURN_SLOW_ZONE_DEG) {
      pwm = MIN_MOVE_PWM + (int)((TURN_PWM - MIN_MOVE_PWM) *
                                 (fabs(remaining) / TURN_SLOW_ZONE_DEG));
    }
    if (remaining > 0) setMotors(-pwm, +pwm);   // left / CCW
    else               setMotors(+pwm, -pwm);   // right / CW
    delay(3);
  }
  stopMotors();
  delay(120);   // let it settle before the next reading
}

void turnLeft()   { turnInPlace(+90.0); }
void turnRight()  { turnInPlace(-90.0); }
void turnAround() { turnInPlace(+180.0); }

// Back off and re-look. Escalates; only truly gives up when physically stuck.
void recoverExplore() {
  recoveryAttempts++;
  Serial.printf("Recovery attempt %d/%d (something blocked forward progress)\n",
                recoveryAttempts, MAX_RECOVERY);
  showLED(LED_RECOVER);

  // Fix A: after a few honest tries, stop pushing against an obstruction - but
  // SAY SO, once, so the mouse never freezes silently.
  if (recoveryAttempts >= MAX_RECOVERY) {
    Serial.println(F("STOP: gave up after 3 recovery attempts. Reposition and RESET."));
    showLED(LED_BLOCKED);
    stopMotors();
    gaveUp = true;
    return;
  }

  // Back up about a third of a cell so the next look is from clear space.
  long startL = countL, startR = countR;
  unsigned long t0 = millis();
  while (labs(countL - startL) < BACKUP_TICKS &&
         labs(countR - startR) < BACKUP_TICKS &&
         millis() - t0 < 1500) {
    setMotors(-BACKUP_PWM, -BACKUP_PWM);
    delay(5);
  }
  stopMotors();
  delay(150);
  senseWalls();   // fresh look for the next decision
}

// ============================================================================
//  ARDUINO ENTRY POINTS
// ============================================================================
void setup() {
  Serial.begin(115200);
  delay(400);
  Serial.println();
  Serial.println(F("=== Micromouse exploration - booting ==="));

  if (PIN_STATUS_LED >= 0) pinMode(PIN_STATUS_LED, OUTPUT);
  showLED(LED_BOOT);

  // Motor pins.
  pinMode(PIN_L_DIR, OUTPUT);
  pinMode(PIN_R_DIR, OUTPUT);
  ledcAttach(PIN_L_PWM, PWM_FREQ_HZ, PWM_BITS);
  ledcAttach(PIN_R_PWM, PWM_FREQ_HZ, PWM_BITS);
  stopMotors();

  // Encoder pins + interrupts.
  pinMode(PIN_L_ENC_A, INPUT_PULLUP);
  pinMode(PIN_L_ENC_B, INPUT_PULLUP);
  pinMode(PIN_R_ENC_A, INPUT_PULLUP);
  pinMode(PIN_R_ENC_B, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(PIN_L_ENC_A), isrLeft,  CHANGE);
  attachInterrupt(digitalPinToInterrupt(PIN_R_ENC_A), isrRight, CHANGE);

  // I2C + all four sensors (this halts loudly if anything fails to come up).
  Wire.begin(PIN_SDA, PIN_SCL);
  Wire.setClock(100000);   // same safe speed the scanner proved works
  startSensors();

  Serial.printf("Ticks per cell = %ld (from wheel %.0f mm, %.0f ticks/rev)\n",
                TICKS_PER_CELL, WHEEL_DIAMETER_MM, ENC_TICKS_PER_REV);
  Serial.println(F("Bring-up complete. Starting exploration in 2 s..."));
  delay(2000);
  lastHeadingUs = micros();
}

void loop() {
  // If we have genuinely given up, hold here blinking BLOCKED. Not silent, not
  // pretending to still drive - just clearly waiting for a human.
  if (gaveUp) blinkForever(400, 400);   // never returns

  senseWalls();

  // LEFT-HAND RULE. There is always a move, so the mouse keeps exploring.
  // Each branch performs one cell of progress (an optional turn + a forward),
  // which is what stops a plain turn-and-recheck from spinning on the spot.
  bool ok;
  if (!wallLeft) {
    turnLeft();
    ok = driveOneCell();
  } else if (!wallFront) {
    ok = driveOneCell();
  } else if (!wallRight) {
    turnRight();
    ok = driveOneCell();
  } else {
    turnAround();
    ok = driveOneCell();
  }

  if (!ok) recoverExplore();   // stalled -> back off and try again (or halt loudly)
}
