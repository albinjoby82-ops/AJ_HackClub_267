/*
 * ============================================================================
 *  BENCH TEST 1 - MOTORS & ENCODERS  (Layer 1: prove the electrics)
 * ============================================================================
 *
 *  Nothing above this matters until the motors spin the way you think and the
 *  encoders count the way you think. This sketch is a serial-driven bench tool
 *  to verify and MEASURE exactly that. Wheels OFF the table.
 *
 *  What it gives you (the numbers the other sketches need):
 *    - L_DIR_SIGN / R_DIR_SIGN : does "forward" actually drive each wheel
 *      forward, and does its own encoder count UP when it does?
 *    - ENC_TICKS_PER_REV       : how many encoder ticks = one wheel turn.
 *
 *  Open Serial Monitor at 115200, send single letters:
 *    h : print this help
 *    z : zero both encoder counts
 *    e : both wheels FORWARD at test PWM        x : stop
 *    l : left wheel forward pulse (1 s), report its own encoder delta
 *    r : right wheel forward pulse (1 s), report its own encoder delta
 *    o : motors OFF and stream counts - turn a wheel BY HAND to measure
 *    + / - : raise / lower the test PWM
 *    d : direction self-check (pulses each wheel, tells you what to fix)
 *
 *  It streams the live encoder counts a few times a second the whole time,
 *  plus the raw A/B pin levels. Turning a wheel slowly, BOTH its A and B must
 *  flip between 0 and 1. If one never changes, that wire isn't reaching the pin.
 * ============================================================================
 */

#include <Arduino.h>

// --- Pins: match your wiring (same as the other sketches) ------------------
const int PIN_L_DIR = 0, PIN_L_PWM = 2;
const int PIN_R_DIR = 3, PIN_R_PWM = 10;
const int PIN_L_ENC_A = 21,  PIN_L_ENC_B = 22;
const int PIN_R_ENC_A = 11, PIN_R_ENC_B = 23;

// Start with both +1; this tool tells you if either needs flipping.
int L_DIR_SIGN = +1, R_DIR_SIGN = -1;

const int PWM_FREQ_HZ = 20000, PWM_BITS = 8, PWM_MAX = 255, MIN_MOVE_PWM = 45;
int testPWM = 90;

volatile long countL = 0, countR = 0;

void IRAM_ATTR isrLeft()  { if (digitalRead(PIN_L_ENC_A) == digitalRead(PIN_L_ENC_B)) countL++; else countL--; }
void IRAM_ATTR isrRight() { if (digitalRead(PIN_R_ENC_A) == digitalRead(PIN_R_ENC_B)) countR++; else countR--; }

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

void help() {
  Serial.println(F("\n--- motor & encoder bench test ---"));
  Serial.println(F("h help | z zero | e both fwd | x stop | l left pulse | r right pulse"));
  Serial.println(F("o motors off (hand-turn to measure) | + / - PWM | d direction self-check"));
  Serial.printf ("test PWM = %d,  L_DIR_SIGN = %+d,  R_DIR_SIGN = %+d\n", testPWM, L_DIR_SIGN, R_DIR_SIGN);
}

// Pulse one wheel forward for 1 s and report how its OWN encoder moved.
void pulseWheel(bool left) {
  long s = left ? countL : countR;
  Serial.printf("Pulsing %s wheel forward at PWM %d for 1 s...\n", left ? "LEFT" : "RIGHT", testPWM);
  if (left) setMotors(testPWM, 0); else setMotors(0, testPWM);
  delay(1000);
  stopMotors();
  long delta = (left ? countL : countR) - s;
  Serial.printf("  %s encoder delta = %+ld\n", left ? "LEFT" : "RIGHT", delta);
  if (delta > 0)      Serial.println(F("  OK: this wheel counts UP when driven forward."));
  else if (delta < 0) Serial.println(F("  FLIP: counts DOWN -> swap this encoder's A/B pins (or invert in software)."));
  else                Serial.println(F("  ZERO: no counts -> check encoder power/wiring, or the motor didn't move."));
}

void directionCheck() {
  Serial.println(F("\nDirection self-check (watch the wheels AND the numbers):"));
  pulseWheel(true);  delay(300);
  pulseWheel(false);
  Serial.println(F("If a wheel physically spun BACKWARD, swap that motor's two wires"));
  Serial.println(F("or set its *_DIR_SIGN to -1. If its encoder delta was negative,"));
  Serial.println(F("swap that encoder's A/B. Goal: forward => wheel forward => count up."));
}

// Motors off; stream counts so you can turn a wheel by hand exactly one turn
// and read ENC_TICKS_PER_REV straight off the delta.
void handMeasure() {
  stopMotors();
  Serial.println(F("\nMotors OFF. Zeroing. Turn ONE wheel slowly by hand exactly"));
  Serial.println(F("one full revolution, then read that wheel's count = ticks/rev."));
  countL = countR = 0;
}

void setup() {
  Serial.begin(115200); delay(400);

  pinMode(PIN_L_DIR, OUTPUT); pinMode(PIN_R_DIR, OUTPUT);
  ledcAttach(PIN_L_PWM, PWM_FREQ_HZ, PWM_BITS);
  ledcAttach(PIN_R_PWM, PWM_FREQ_HZ, PWM_BITS);
  stopMotors();

  pinMode(PIN_L_ENC_A, INPUT_PULLUP); pinMode(PIN_L_ENC_B, INPUT_PULLUP);
  pinMode(PIN_R_ENC_A, INPUT_PULLUP); pinMode(PIN_R_ENC_B, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(PIN_L_ENC_A), isrLeft,  CHANGE);
  attachInterrupt(digitalPinToInterrupt(PIN_R_ENC_A), isrRight, CHANGE);

  help();
}

void loop() {
  if (Serial.available()) {
    char c = Serial.read();
    switch (c) {
      case 'h': help(); break;
      case 'z': countL = countR = 0; Serial.println(F("counts zeroed")); break;
      case 'e': setMotors(testPWM, testPWM); Serial.println(F("both forward")); break;
      case 'x': stopMotors(); Serial.println(F("stop")); break;
      case 'l': pulseWheel(true); break;
      case 'r': pulseWheel(false); break;
      case 'o': handMeasure(); break;
      case 'd': directionCheck(); break;
      case '+': testPWM = min(PWM_MAX, testPWM + 10); Serial.printf("test PWM = %d\n", testPWM); break;
      case '-': testPWM = max(0,       testPWM - 10); Serial.printf("test PWM = %d\n", testPWM); break;
      default: break;
    }
  }

  static unsigned long last = 0;
  if (millis() - last > 250) {
    last = millis();
    Serial.printf("counts  L=%+8ld  R=%+8ld   raw pins  LA=%d LB=%d  RA=%d RB=%d\n",
                  countL, countR,
                  digitalRead(PIN_L_ENC_A), digitalRead(PIN_L_ENC_B),
                  digitalRead(PIN_R_ENC_A), digitalRead(PIN_R_ENC_B));
  }
}
