/*
 * ============================================================================
 *  BENCH TEST 2 - CLOSED-LOOP STRAIGHT DRIVE + TELEMETRY
 *  (Layers 2-4: hit target speed, stay centred, stop before the wall)
 * ============================================================================
 *
 *  This is the sketch that makes the mouse *reliable*. It does NOT map anything.
 *  It drives straight down a corridor and proves the control loop works:
 *
 *    Layer 2  each wheel runs a closed-loop SPEED PID, so it actually hits the
 *             commanded speed instead of a raw PWM guess. This is what stops the
 *             mouse curving just because two cheap motors differ.
 *    Layer 3  an outer steering loop (gyro heading-hold + wall centring) sets
 *             the two wheel speeds, so it holds a straight, centred line.
 *    Layer 4  the front ToF cuts the speed to zero before it can touch a wall.
 *
 *  It streams CSV telemetry every control tick so you can watch it and tune:
 *  open Serial Monitor (or Serial Plotter) at 115200. Columns are printed once
 *  as a header. Send 'g' to drive, 'x' to stop.
 *
 *  TUNING ORDER (do it in this order, it converges fast):
 *    1. Layer 2 first, one wheel at a time in your head: with steering off
 *       (set STEER_* gains to 0), send 'g' and watch Lmeas track Ltgt and Rmeas
 *       track Rtgt. Raise KP_V until it responds quickly without buzzing, then
 *       add KI_V until the steady-state error is ~0. Set FF_PWM_PER_TPS so the
 *       PWM sits mid-range at cruise (less work for the PID).
 *    2. Then heading: raise STEER_KP_HEAD / STEER_KD_HEAD until it drives a
 *       straight line down an OPEN corridor (no side walls) without drifting.
 *    3. Then centring: add STEER_KP_CENTER / STEER_KP_SIDE until it sits in the
 *       middle between walls and recovers smoothly if you start it off-centre.
 *
 *  Run i2c_scanner and motor_encoder_test first. Needs the Pololu VL53L0X lib.
 * ============================================================================
 */

#include <Wire.h>
#include <VL53L0X.h>

// ============================================================================
//  CONFIG  (keep pins identical across all the sketches)
// ============================================================================
const int PIN_SDA = 6, PIN_SCL = 7;
const int     XSHUT[3]       = {   2,       3,       10   };
const char   *SENSOR_NAME[3] = { "LEFT",  "FRONT", "RIGHT" };
const uint8_t SENSOR_ADDR[3] = { 0x30,    0x31,    0x32   };
enum { S_LEFT = 0, S_FRONT = 1, S_RIGHT = 2 };

const int PIN_L_DIR = 19, PIN_L_PWM = 18;
const int PIN_R_DIR = 21, PIN_R_PWM = 20;
const int L_DIR_SIGN = +1, R_DIR_SIGN = +1;

const int PIN_L_ENC_A = 0, PIN_L_ENC_B = 1;
const int PIN_R_ENC_A = 22, PIN_R_ENC_B = 23;

const int PWM_FREQ_HZ = 20000, PWM_BITS = 8, PWM_MAX = 255, MIN_MOVE_PWM = 40;

// Geometry - MEASURE (use motor_encoder_test).
const float WHEEL_DIAMETER_MM = 44.0, ENC_TICKS_PER_REV = 210.0;
const float MM_PER_TICK = (PI * WHEEL_DIAMETER_MM) / ENC_TICKS_PER_REV;

// Target cruise speed. Slow on purpose.
const float TARGET_MM_S = 150.0;
const float CRUISE_TPS  = TARGET_MM_S / MM_PER_TICK;   // ticks/second

// --- Layer 2: per-wheel speed PID (TUNE - see tuning order above) ----------
const float FF_PWM_PER_TPS = 70.0 / CRUISE_TPS;  // feed-forward: ~70 PWM at cruise
const float KP_V = 0.05;                         // PWM per (tick/s) of error
const float KI_V = 0.20;                         // PWM per (tick/s)*s of error
const float INTEG_MAX = 4000.0;                  // anti-windup clamp on integral

// --- Layer 3: outer steering loop, OUTPUT IS A SPEED DIFFERENCE (tps) -------
const float STEER_KP_HEAD  = 6.0;    // tps per degree of yaw error
const float STEER_KD_HEAD  = 0.8;    // tps per (deg/s) of yaw rate
const float STEER_KP_CENTER = 1.5;   // tps per mm of left-right imbalance
const float STEER_KP_SIDE   = 2.0;   // tps per mm off a single-wall setpoint
const float STEER_MAX_FRAC  = 0.6;   // clamp steer to this fraction of cruise
const int   WALL_TRUST_MM   = 90, SIDE_SETPOINT_MM = 70, MAX_VALID_MM = 1200;

// --- Layer 4: wall stop -----------------------------------------------------
const int FRONT_STOP_MM = 65;

// MPU-6050.
const uint8_t MPU_ADDR = 0x68, MPU_PWR_MGMT_1 = 0x6B, MPU_GYRO_ZOUT_H = 0x47;
const float   GYRO_LSB_PER_DPS = 131.0;
const int     GYRO_SIGN = +1, GYRO_CAL_SAMPLES = 800;

// ============================================================================
//  STATE
// ============================================================================
VL53L0X laser[3];
volatile long countL = 0, countR = 0;
long lastCountL = 0, lastCountR = 0;
unsigned long lastTickUs = 0;

float gyroBiasZ = 0, gyroAngle = 0, lastGyroZ = 0;
unsigned long lastGyroUs = 0;

int distL = MAX_VALID_MM, distF = MAX_VALID_MM, distR = MAX_VALID_MM;
float integL = 0, integR = 0;
bool running = false;

void IRAM_ATTR isrLeft()  { if (digitalRead(PIN_L_ENC_A) == digitalRead(PIN_L_ENC_B)) countL++; else countL--; }
void IRAM_ATTR isrRight() { if (digitalRead(PIN_R_ENC_A) == digitalRead(PIN_R_ENC_B)) countR++; else countR--; }

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
void setMotorsPWM(int l, int r) {
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
  if (Wire.endTransmission(false) != 0) return 0;
  if (Wire.requestFrom((int)MPU_ADDR, 2) != 2) return 0;
  int16_t raw = (Wire.read() << 8) | Wire.read();
  return GYRO_SIGN * (raw / GYRO_LSB_PER_DPS) - gyroBiasZ;
}
void updateGyro() {
  unsigned long now = micros();
  float dt = (now - lastGyroUs) * 1e-6f; lastGyroUs = now;
  if (dt <= 0 || dt > 0.2f) return;
  lastGyroZ = readGyroZ();
  gyroAngle += lastGyroZ * dt;
}
void calibrateGyro() {
  Serial.println(F("Calibrating gyro - hold still..."));
  double sum = 0;
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
void readAll() { distL = readDist(S_LEFT); distF = readDist(S_FRONT); distR = readDist(S_RIGHT); }

void startSensors() {
  for (int i = 0; i < 3; i++) { pinMode(XSHUT[i], OUTPUT); digitalWrite(XSHUT[i], LOW); }
  delay(20);
  for (int i = 0; i < 3; i++) {
    digitalWrite(XSHUT[i], HIGH); delay(20);
    laser[i].setTimeout(200);
    if (!laser[i].init()) { Serial.printf("HALT: VL53L0X %s init failed\n", SENSOR_NAME[i]); while (1) delay(100); }
    laser[i].setAddress(SENSOR_ADDR[i]);
    laser[i].setMeasurementTimingBudget(20000);   // 20 ms: fast enough for the loop
    laser[i].startContinuous();
    Serial.printf("Sensor %-5s OK at 0x%02X\n", SENSOR_NAME[i], SENSOR_ADDR[i]);
  }
  if (!mpuWrite(MPU_PWR_MGMT_1, 0x00)) { Serial.println(F("HALT: MPU-6050 not responding")); while (1) delay(100); }
  delay(50);
  Serial.println(F("IMU OK at 0x68"));
  calibrateGyro();
}

// ============================================================================
//  CONTROL
// ============================================================================
// Outer loop: turn heading + centring errors into a left/right speed split.
float steerTPS() {
  float steer = STEER_KP_HEAD * gyroAngle + STEER_KD_HEAD * lastGyroZ;   // hold heading 0
  bool tl = (distL < WALL_TRUST_MM), tr = (distR < WALL_TRUST_MM);
  if (tl && tr)      steer += STEER_KP_CENTER * (distR - distL);
  else if (tl)       steer += STEER_KP_SIDE * (SIDE_SETPOINT_MM - distL);
  else if (tr)       steer -= STEER_KP_SIDE * (SIDE_SETPOINT_MM - distR);
  float lim = STEER_MAX_FRAC * CRUISE_TPS;
  if (steer >  lim) steer =  lim;
  if (steer < -lim) steer = -lim;
  return steer;
}

// Inner loop: one wheel, speed PID -> PWM.
int wheelPID(float target_tps, float meas_tps, float &integ, float dt) {
  float err = target_tps - meas_tps;
  integ += err * dt;
  if (integ >  INTEG_MAX) integ =  INTEG_MAX;
  if (integ < -INTEG_MAX) integ = -INTEG_MAX;
  float pwm = FF_PWM_PER_TPS * target_tps + KP_V * err + KI_V * integ;
  if (pwm >  PWM_MAX) pwm =  PWM_MAX;
  if (pwm < -PWM_MAX) pwm = -PWM_MAX;
  return (int)pwm;
}

void setup() {
  Serial.begin(115200); delay(400);
  Serial.println(F("\n=== Closed-loop straight-drive test ==="));

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

  Serial.printf("Cruise = %.0f mm/s = %.0f ticks/s. Send 'g' to drive, 'x' to stop.\n",
                TARGET_MM_S, CRUISE_TPS);
  Serial.println(F("ms,Ltgt,Lmeas,Lpwm,Rtgt,Rmeas,Rpwm,angle,rate,dL,dF,dR,steer"));

  lastTickUs = micros(); lastGyroUs = micros();
}

void loop() {
  if (Serial.available()) {
    char c = Serial.read();
    if (c == 'g') { running = true; gyroAngle = 0; integL = integR = 0; lastGyroUs = micros(); Serial.println(F("# GO")); }
    if (c == 'x') { running = false; stopMotors(); Serial.println(F("# STOP")); }
  }

  // Fixed-ish control tick, but we use the ACTUAL elapsed time for the maths so
  // sensor jitter can't corrupt the speed estimate.
  unsigned long now = micros();
  float dt = (now - lastTickUs) * 1e-6f;
  if (dt < 0.020f) return;              // ~50 Hz max
  lastTickUs = now;

  updateGyro();
  readAll();

  // Measure each wheel's speed from its ticks over this interval.
  long dLt = countL - lastCountL, dRt = countR - lastCountR;
  lastCountL = countL; lastCountR = countR;
  float measL = dLt / dt, measR = dRt / dt;   // ticks/second

  float baseTPS = 0.0, steer = 0.0;
  if (running) {
    if (distF < FRONT_STOP_MM) {               // Layer 4: wall ahead -> stop
      running = false;
      Serial.println(F("# WALL AHEAD - stopping"));
    } else {
      baseTPS = CRUISE_TPS;
      steer   = steerTPS();                    // Layer 3
    }
  }

  int pwmL = 0, pwmR = 0;
  if (running || baseTPS != 0.0) {
    float tgtL = baseTPS + steer, tgtR = baseTPS - steer;   // + = steer right
    pwmL = wheelPID(tgtL, measL, integL, dt);               // Layer 2
    pwmR = wheelPID(tgtR, measR, integR, dt);
    setMotorsPWM(pwmL, pwmR);

    Serial.printf("%lu,%.0f,%.0f,%d,%.0f,%.0f,%d,%.1f,%.1f,%d,%d,%d,%.0f\n",
                  millis(), baseTPS + steer, measL, pwmL, baseTPS - steer, measR, pwmR,
                  gyroAngle, lastGyroZ, distL, distF, distR, steer);
  } else {
    stopMotors();
  }
}
