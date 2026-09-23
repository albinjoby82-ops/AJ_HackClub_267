/*
 * ============================================================================
 *  STEP 1 - I2C REACHABILITY SCANNER  (run this FIRST, on its own)
 * ============================================================================
 *
 *  Dublin Micromouse Open 2026 - ESP32-C6 mouse.
 *
 *  This sketch does ONE job: prove that all four I2C devices on the mouse are
 *  actually wired up and talking. It changes nothing about how the mouse drives.
 *  If a device shows MISSING here, that is your root cause - no amount of
 *  tweaking the exploration code will fix a wire that is not connected.
 *
 *  The four devices:
 *      - VL53L0X LEFT   distance sensor  -> reassigned to 0x30
 *      - VL53L0X FRONT  distance sensor  -> reassigned to 0x31
 *      - VL53L0X RIGHT  distance sensor  -> reassigned to 0x32
 *      - MPU-6050 (SEN0142) IMU          -> lives at 0x68
 *
 *  Why not just scan the bus once? All three VL53L0X power up at the SAME
 *  address (0x29), so a plain scan cannot tell them apart or tell you which
 *  one is missing. So we bring them up one at a time using their XSHUT pins,
 *  exactly the way the mouse does, and report each by name.
 *
 *  HOW TO USE:
 *      1. Set the pin numbers below to match YOUR wiring.
 *      2. Flash this sketch alone.
 *      3. Open Serial Monitor at 115200 baud.
 *      4. Read the report. Every "MISSING" line names the sensor and the
 *         wires to check for that specific device.
 *      5. Do NOT move on to the mouse sketch until all four show FOUND.
 *
 *  Depends only on <Wire.h> (built in). No libraries to install.
 * ============================================================================
 */

#include <Wire.h>

// --- I2C bus pins (ESP32-C6). Set these to your board's SDA/SCL. -----------
const int PIN_SDA = 6;
const int PIN_SCL = 7;

// --- XSHUT pins, one per VL53L0X. Set these to your wiring. -----------------
//     Order here MUST match the names/addresses arrays below.
const int   XSHUT[3]        = {   2,        3,        10   };
const char *SENSOR_NAME[3]  = { "LEFT",   "FRONT",  "RIGHT" };
const uint8_t NEW_ADDR[3]   = { 0x30,     0x31,     0x32   };

// VL53L0X default (power-up) address, shared by all of them.
const uint8_t VL53_DEFAULT_ADDR = 0x29;
// VL53L0X register that stores the device's I2C address.
const uint8_t VL53_REG_I2C_ADDR = 0x8A;

// MPU-6050 (SEN0142) address and WHO_AM_I register.
const uint8_t MPU_ADDR    = 0x68;
const uint8_t MPU_WHO_AM_I = 0x75;

// ---------------------------------------------------------------------------
// Return true if a device ACKs at this 7-bit address.
bool deviceAcks(uint8_t addr) {
  Wire.beginTransmission(addr);
  return (Wire.endTransmission() == 0);
}

// Write one byte to a register on a device. Returns true on ACK.
bool writeReg(uint8_t addr, uint8_t reg, uint8_t value) {
  Wire.beginTransmission(addr);
  Wire.write(reg);
  Wire.write(value);
  return (Wire.endTransmission() == 0);
}

// Read one byte from a register. Returns true on success (value in *out).
bool readReg(uint8_t addr, uint8_t reg, uint8_t *out) {
  Wire.beginTransmission(addr);
  Wire.write(reg);
  if (Wire.endTransmission(false) != 0) return false;   // repeated start
  if (Wire.requestFrom((int)addr, 1) != 1) return false;
  *out = Wire.read();
  return true;
}

// ---------------------------------------------------------------------------
void setup() {
  Serial.begin(115200);
  delay(400);
  Serial.println();
  Serial.println(F("=========================================="));
  Serial.println(F("  Micromouse I2C reachability scanner"));
  Serial.println(F("=========================================="));

  Wire.begin(PIN_SDA, PIN_SCL);
  Wire.setClock(100000);   // slow and safe for bring-up

  int found = 0;

  // --- Put every VL53L0X to sleep first (all XSHUT LOW) ---------------------
  for (int i = 0; i < 3; ++i) {
    pinMode(XSHUT[i], OUTPUT);
    digitalWrite(XSHUT[i], LOW);
  }
  delay(20);

  // --- Bring the ToF sensors up one at a time ------------------------------
  for (int i = 0; i < 3; ++i) {
    Serial.println();
    Serial.printf("Checking VL53L0X %-5s (XSHUT on GPIO%d)...\n",
                  SENSOR_NAME[i], XSHUT[i]);

    digitalWrite(XSHUT[i], HIGH);   // wake ONLY this sensor
    delay(20);

    if (!deviceAcks(VL53_DEFAULT_ADDR)) {
      Serial.printf("  MISSING: %s did not answer at 0x29.\n", SENSOR_NAME[i]);
      Serial.printf("  -> Check %s: XSHUT (GPIO%d), SDA, SCL, VIN(3V3), GND.\n",
                    SENSOR_NAME[i], XSHUT[i]);
      Serial.println(F("  -> Some 4-pin boards do not break out XSHUT and cannot be used."));
      continue;
    }

    // Move it off 0x29 so the next sensor gets a clean 0x29 to itself.
    writeReg(VL53_DEFAULT_ADDR, VL53_REG_I2C_ADDR, NEW_ADDR[i] & 0x7F);
    delay(10);

    if (deviceAcks(NEW_ADDR[i])) {
      Serial.printf("  FOUND: %s answering at 0x%02X.\n",
                    SENSOR_NAME[i], NEW_ADDR[i]);
      found++;
    } else {
      Serial.printf("  MISSING: %s took 0x29 but would not move to 0x%02X.\n",
                    SENSOR_NAME[i], NEW_ADDR[i]);
      Serial.println(F("  -> Usually a flaky VIN/GND or a shared-bus wiring fault."));
    }
    // Leave it awake and at its new address for the rest of the scan.
  }

  // --- Check the IMU -------------------------------------------------------
  Serial.println();
  Serial.println(F("Checking MPU-6050 / SEN0142 IMU..."));
  if (deviceAcks(MPU_ADDR)) {
    uint8_t who = 0;
    readReg(MPU_ADDR, MPU_WHO_AM_I, &who);
    Serial.printf("  FOUND: IMU answering at 0x%02X (WHO_AM_I = 0x%02X).\n",
                  MPU_ADDR, who);
    found++;
  } else {
    Serial.printf("  MISSING: IMU did not answer at 0x%02X.\n", MPU_ADDR);
    Serial.println(F("  -> Check IMU: SDA, SCL, VIN(3V3), GND. AD0 low keeps it at 0x68."));
  }

  // --- Raw bus dump for reference ------------------------------------------
  Serial.println();
  Serial.println(F("Raw bus scan (everything currently answering):"));
  int rawCount = 0;
  for (uint8_t a = 1; a < 127; ++a) {
    if (deviceAcks(a)) {
      Serial.printf("  0x%02X\n", a);
      rawCount++;
    }
  }
  if (rawCount == 0) Serial.println(F("  (nothing found - check SDA/SCL/pull-ups/GND to the whole bus)"));

  // --- Summary -------------------------------------------------------------
  Serial.println();
  Serial.println(F("------------------------------------------"));
  Serial.printf("RESULT: %d of 4 expected devices reachable.\n", found);
  if (found == 4) {
    Serial.println(F("All good. You can move on to the mouse_explore sketch."));
  } else {
    Serial.println(F("Fix the MISSING device(s) above before flashing the mouse."));
  }
  Serial.println(F("------------------------------------------"));
}

void loop() {
  // Nothing to do - the report above is printed once at boot. Press RESET to
  // run it again after fixing a wire.
}
