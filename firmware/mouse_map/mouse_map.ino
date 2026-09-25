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
 *  Run the i2c_scanner first (all 4 devices FOUND), then flash this with the
 *  wheels off the table and watch Serial at 115200. It prints the map when it
 *  reaches the goal. Set the pins and MEASURE the geometry, same as the
 *  mouse_explore sketch. Needs the Pololu "VL53L0X" library.
 * ============================================================================
 */

#include <Wire.h>
#include <VL53L0X.h>
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
const int L_DIR_SIGN = +1, R_DIR_SIGN = +1;

const int PIN_L_ENC_A = 21, PIN_L_ENC_B = 22;
const int PIN_R_ENC_A = 11, PIN_R_ENC_B = 23;

const int PIN_STATUS_LED = -1;      // -1 if none

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

// Recovery / stall.
const int           MAX_RECOVERY = 3;
const long          STALL_TICKS = 3;
const unsigned long STALL_MS = 700, CELL_TIMEOUT_MS = 6000;

// MPU-6050.
const uint8_t MPU_ADDR = 0x68, MPU_PWR_MGMT_1 = 0x6B, MPU_GYRO_ZOUT_H = 0x47;
const float   GYRO_LSB_PER_DPS = 131.0;
const int     GYRO_SIGN = +1, GYRO_CAL_SAMPLES = 800;

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
float gyroBiasZ = 0.0, gyroAngle = 0.0, lastGyroZ = 0.0;      // per-move gyro
unsigned long lastGyroUs = 0;

int  distL = MAX_VALID_MM, distF = MAX_VALID_MM, distR = MAX_VALID_MM;
int  recoveryAttempts = 0;
bool mappedDone = false, gaveUp = false;

enum LedState { LED_BOOT, LED_EXPLORING, LED_TURNING, LED_RECOVER, LED_BLOCKED, LED_ERROR, LED_DONE };
LedState ledState = LED_BOOT;

// ============================================================================
//  ENCODER ISRs
// ============================================================================
void IRAM_ATTR isrLeft()  { if (digitalRead(PIN_L_ENC_A) == digitalRead(PIN_L_ENC_B)) countL++; else countL--; }
void IRAM_ATTR isrRight() { if (digitalRead(PIN_R_ENC_A) == digitalRead(PIN_R_ENC_B)) countR++; else countR--; }

// ============================================================================
//  LED / SERIAL STATE
// ============================================================================
void stopMotors();   // fwd decl used by halt()

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
    Serial.printf("[state] %s\n", n);
  }
  if (PIN_STATUS_LED < 0) return;
  digitalWrite(PIN_STATUS_LED, (s == LED_EXPLORING || s == LED_TURNING || s == LED_DONE) ? HIGH : LOW);
}

void blinkForever(int on, int off) {
  while (true) {
    if (PIN_STATUS_LED >= 0) digitalWrite(PIN_STATUS_LED, HIGH); delay(on);
    if (PIN_STATUS_LED >= 0) digitalWrite(PIN_STATUS_LED, LOW);  delay(off);
  }
}

void halt(const char *why) { Serial.printf("HALT: %s\n", why); ledState = LED_ERROR; stopMotors(); blinkForever(80, 80); }

// ============================================================================
//  MOTORS
// ============================================================================
void motorWrite(int dirPin, int pwmPin, int dirSign, int spd) {
  int s = spd * dirSign; bool fwd = (s >= 0); int mag = abs(s);
  if (mag > PWM_MAX) mag = PWM_MAX;
  if (mag != 0 && mag < MIN_MOVE_PWM) mag = MIN_MOVE_PWM;
  digitalWrite(dirPin, fwd ? HIGH : LOW);
  ledcWrite(pwmPin, mag);
}
void setMotors(int l, int r) {
  motorWrite(PIN_L_DIR, PIN_L_PWM, L_DIR_SIGN, l);
  motorWrite(PIN_R_DIR, PIN_R_PWM, R_DIR_SIGN, r);
}
void stopMotors() { ledcWrite(PIN_L_PWM, 0); ledcWrite(PIN_R_PWM, 0); }

// ============================================================================
//  GYRO
// ============================================================================
bool mpuWrite(uint8_t reg, uint8_t val) {
  Wire.beginTransmission(MPU_ADDR); Wire.write(reg); Wire.write(val);
  return Wire.endTransmission() == 0;
}
float readGyroZ() {
  Wire.beginTransmission(MPU_ADDR); Wire.write(MPU_GYRO_ZOUT_H);
  if (Wire.endTransmission(false) != 0) return 0.0;
  if (Wire.requestFrom((int)MPU_ADDR, 2) != 2) return 0.0;
  int16_t raw = (Wire.read() << 8) | Wire.read();
  return GYRO_SIGN * (raw / GYRO_LSB_PER_DPS) - gyroBiasZ;
}
void resetGyro() { gyroAngle = 0.0; lastGyroUs = micros(); }
void updateGyro() {
  unsigned long now = micros();
  float dt = (now - lastGyroUs) * 1e-6f; lastGyroUs = now;
  if (dt <= 0 || dt > 0.2f) return;
  lastGyroZ = readGyroZ();
  gyroAngle += lastGyroZ * dt;
}
void calibrateGyro() {
  Serial.println(F("Calibrating gyro - keep the mouse completely still..."));
  double sum = 0; gyroBiasZ = 0;
  for (int i = 0; i < GYRO_CAL_SAMPLES; i++) {
    Wire.beginTransmission(MPU_ADDR); Wire.write(MPU_GYRO_ZOUT_H); Wire.endTransmission(false);
    Wire.requestFrom((int)MPU_ADDR, 2);
    int16_t raw = (Wire.read() << 8) | Wire.read();
    sum += GYRO_SIGN * (raw / GYRO_LSB_PER_DPS); delay(2);
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
// Average a few reads while stopped, for a trustworthy wall decision.
int readDistStable(int i) {
  long sum = 0; int n = 0;
  for (int k = 0; k < 5; k++) { sum += readDist(i); n++; delay(6); }
  return (int)(sum / n);
}
void readAll() { distL = readDist(S_LEFT); distF = readDist(S_FRONT); distR = readDist(S_RIGHT); }

void startSensors() {
  for (int i = 0; i < 3; i++) { pinMode(XSHUT[i], OUTPUT); digitalWrite(XSHUT[i], LOW); }
  delay(20);
  for (int i = 0; i < 3; i++) {
    digitalWrite(XSHUT[i], HIGH); delay(20);
    laser[i].setTimeout(200);
    if (!laser[i].init()) { char m[80]; snprintf(m, sizeof(m), "VL53L0X %s init failed: check XSHUT/SDA/SCL/VIN/GND", SENSOR_NAME[i]); halt(m); }
    laser[i].setAddress(SENSOR_ADDR[i]);
    if (!laser[i].setMeasurementTimingBudget(33000)) halt("VL53L0X timing budget rejected");
    laser[i].startContinuous();
    Serial.printf("Sensor %-5s initialized OK at 0x%02X\n", SENSOR_NAME[i], SENSOR_ADDR[i]);
  }
  if (!mpuWrite(MPU_PWR_MGMT_1, 0x00)) halt("MPU-6050 not responding: check SDA/SCL/VIN/GND");
  delay(50);
  Serial.println(F("IMU (MPU-6050) initialized OK at 0x68"));
  calibrateGyro();
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
  Serial.printf("cell (%d,%d) dir %d | L%4d F%4d R%4d | walls %c%c%c\n",
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

// Drive forward one cell. Returns true if it advanced a full cell (or reached a
// wall ahead), false if it stalled and backed off to where it started.
bool forwardOneCell() {
  long startL = countL, startR = countR;
  resetGyro();
  unsigned long t0 = millis(), lastProg = t0; long best = 0;
  showLED(LED_EXPLORING);

  while (true) {
    updateGyro(); readAll();
    long dL = labs(countL - startL), dR = labs(countR - startR), avg = (dL + dR) / 2;

    if (distF < FRONT_STOP_MM) { stopMotors(); return true; }   // pinned by front wall
    if (avg >= TICKS_PER_CELL) { stopMotors(); return true; }   // full cell by odometry

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
      stopMotors(); return false;
    }
    delay(5);
  }
}

void turnInPlace(float degrees) {
  showLED(LED_TURNING);
  resetGyro();
  unsigned long t0 = millis();
  while (millis() - t0 < TURN_TIMEOUT_MS) {
    updateGyro();
    float remaining = degrees - gyroAngle;
    if (fabs(remaining) < 2.0) break;
    int pwm = TURN_PWM;
    if (fabs(remaining) < TURN_SLOW_ZONE_DEG)
      pwm = MIN_MOVE_PWM + (int)((TURN_PWM - MIN_MOVE_PWM) * (fabs(remaining) / TURN_SLOW_ZONE_DEG));
    if (remaining > 0) setMotors(-pwm, +pwm); else setMotors(+pwm, -pwm);
    delay(3);
  }
  stopMotors(); delay(120);
}

// Turn to an absolute cardinal direction by the shortest rotation.
void turnToHeading(int target) {
  int diff = (target - headingDir) & 3;
  if (diff == 1)      turnInPlace(-90.0);   // target is to our right (CW)
  else if (diff == 3) turnInPlace(+90.0);   // to our left (CCW)
  else if (diff == 2) turnInPlace(180.0);
  headingDir = target;
}

// ============================================================================
//  MAP PRINTOUT (matches the simulator's rendering)
// ============================================================================
void printMap() {
  Serial.println(F("\n--- discovered map (M=mouse, G=goal) ---"));
  for (int y = maze.H - 1; y >= 0; y--) {
    for (int x = 0; x < maze.W; x++) { Serial.print('+'); Serial.print(maze.hasWall(x, y, DIR_N) ? "---" : "   "); }
    Serial.println('+');
    for (int x = 0; x < maze.W; x++) {
      Serial.print(maze.hasWall(x, y, DIR_W) ? '|' : ' ');
      if (x == posX && y == posY) Serial.print(" M ");
      else if (maze.isGoal(x, y))  Serial.print(" G ");
      else                          Serial.print("   ");
    }
    Serial.println(maze.hasWall(maze.W - 1, 0, DIR_E) ? '|' : ' ');
  }
  for (int x = 0; x < maze.W; x++) { Serial.print('+'); Serial.print(maze.hasWall(x, 0, DIR_S) ? "---" : "   "); }
  Serial.println('+');
}

// ============================================================================
//  ARDUINO ENTRY POINTS
// ============================================================================
void setup() {
  Serial.begin(115200); delay(400);
  Serial.println(F("\n=== Micromouse flood-fill mapping - booting ==="));

  if (PIN_STATUS_LED >= 0) pinMode(PIN_STATUS_LED, OUTPUT);
  showLED(LED_BOOT);

  pinMode(PIN_L_DIR, OUTPUT); pinMode(PIN_R_DIR, OUTPUT);
  ledcAttach(PIN_L_PWM, PWM_FREQ_HZ, PWM_BITS);
  ledcAttach(PIN_R_PWM, PWM_FREQ_HZ, PWM_BITS);
  stopMotors();

  pinMode(PIN_L_ENC_A, INPUT_PULLUP); pinMode(PIN_L_ENC_B, INPUT_PULLUP);
  pinMode(PIN_R_ENC_A, INPUT_PULLUP); pinMode(PIN_R_ENC_B, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(PIN_L_ENC_A), isrLeft,  CHANGE);
  attachInterrupt(digitalPinToInterrupt(PIN_R_ENC_A), isrRight, CHANGE);

  Wire.begin(PIN_SDA, PIN_SCL); Wire.setClock(400000);
  startSensors();

  maze.begin(MAZE_W, MAZE_H);
  posX = START_X; posY = START_Y; headingDir = START_DIR;

  Serial.printf("Ticks per cell = %ld. Goal = centre 2x2. Start (%d,%d) dir %d\n",
                TICKS_PER_CELL, posX, posY, headingDir);
  Serial.println(F("Mapping starts in 2 s..."));
  delay(2000);
  resetGyro();
}

void loop() {
  if (mappedDone) blinkForever(1000, 200);   // solved: slow heartbeat, never returns
  if (gaveUp)     blinkForever(400, 400);

  // 1) Look around from a standstill and record walls into the map.
  recordWalls();

  // 2) Reached the centre? Then we've mapped a route - show it and stop.
  if (maze.isGoal(posX, posY)) {
    Serial.println(F("\n*** REACHED GOAL - maze route mapped. ***"));
    printMap();
    showLED(LED_DONE);
    mappedDone = true;
    return;
  }

  // 3) Flood fill and pick the next cell to step into.
  maze.flood();
  int d = maze.bestDir(posX, posY, headingDir);
  if (d < 0) {
    Serial.println(F("STOP: no route to goal from here with the walls seen so far."));
    Serial.println(F("(Check for a mis-read wall, or that the start pose is right.)"));
    printMap();
    showLED(LED_BLOCKED);
    gaveUp = true;
    return;
  }

  // 4) Face that direction and drive one cell, with self-correcting odometry.
  turnToHeading(d);
  if (forwardOneCell()) {
    posX += DIR_DX[headingDir];
    posY += DIR_DY[headingDir];
    recoveryAttempts = 0;
  } else {
    recoveryAttempts++;
    Serial.printf("Recovery attempt %d/%d (stalled crossing a cell)\n", recoveryAttempts, MAX_RECOVERY);
    showLED(LED_RECOVER);
    if (recoveryAttempts >= MAX_RECOVERY) {
      Serial.println(F("STOP: gave up after 3 recovery attempts. Reposition and RESET."));
      showLED(LED_BLOCKED);
      gaveUp = true;
    }
  }
}
