/*
 * ARDUINO ARCADE - shared controller firmware
 * -------------------------------------------
 * One sketch for all four games.  Upload once and leave it on the board.
 *
 * WIRING (see WIRING.md for the full diagram)
 *   D2 -> button 1 -> GND        A0 -> pot 1 wiper
 *   D3 -> button 2 -> GND        A1 -> pot 2 wiper
 *   D4 -> button 3 -> GND        pot outer pins -> 5V and GND
 *   D5 -> button 4 -> GND
 *
 * Buttons use INPUT_PULLUP, so no external resistors are needed and a
 * pressed button reads LOW.
 *
 * SERIAL PROTOCOL - 115200 baud, one newline-terminated packet at ~80 Hz:
 *
 *   POT1,POT2,B1,B2,B3,B4\n      e.g.  512,831,0,1,0,0
 *
 *   POT1/POT2 : 0-1023
 *   B1..B4    : 1 = physically pressed, 0 = released
 *
 * Do not change the field order or count - the Python side parses it
 * strictly and will reject anything else as a malformed packet.
 */

const uint8_t BUTTON_PINS[4] = {2, 3, 4, 5};
const uint8_t POT_PINS[2] = {A0, A1};

// ~80 Hz.  Fast enough to feel instant, slow enough not to flood the port.
const unsigned long SEND_INTERVAL_MS = 12;

// Debounce: a button must hold its new level this long before we report it.
const unsigned long DEBOUNCE_MS = 8;

bool buttonState[4] = {false, false, false, false};
bool lastReading[4] = {false, false, false, false};
unsigned long lastChange[4] = {0, 0, 0, 0};

// Light exponential smoothing on the pots kills the last bit of ADC jitter
// without adding perceptible lag.  The Python side smooths further.
int potFiltered[2] = {0, 0};

unsigned long lastSend = 0;

void setup() {
  Serial.begin(115200);
  for (uint8_t i = 0; i < 4; i++) {
    pinMode(BUTTON_PINS[i], INPUT_PULLUP);
  }
  for (uint8_t i = 0; i < 2; i++) {
    potFiltered[i] = analogRead(POT_PINS[i]);
  }
  lastSend = millis();
}

void loop() {
  unsigned long now = millis();

  // --- buttons: active LOW because of INPUT_PULLUP ---
  for (uint8_t i = 0; i < 4; i++) {
    bool reading = (digitalRead(BUTTON_PINS[i]) == LOW);
    if (reading != lastReading[i]) {
      lastReading[i] = reading;
      lastChange[i] = now;
    }
    if ((now - lastChange[i]) >= DEBOUNCE_MS) {
      buttonState[i] = reading;
    }
  }

  // --- pots ---
  for (uint8_t i = 0; i < 2; i++) {
    int raw = analogRead(POT_PINS[i]);
    potFiltered[i] += (raw - potFiltered[i]) / 3;
    if (potFiltered[i] < 0) potFiltered[i] = 0;
    if (potFiltered[i] > 1023) potFiltered[i] = 1023;
  }

  if ((now - lastSend) >= SEND_INTERVAL_MS) {
    lastSend = now;
    Serial.print(potFiltered[0]);
    Serial.print(',');
    Serial.print(potFiltered[1]);
    for (uint8_t i = 0; i < 4; i++) {
      Serial.print(',');
      Serial.print(buttonState[i] ? 1 : 0);
    }
    Serial.print('\n');
  }
}
