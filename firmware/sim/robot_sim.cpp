/*
 * ============================================================================
 *  robot_sim  -  runs the REAL mouse_map.ino against a physics model
 * ============================================================================
 *
 *  maze_sim.cpp proves the flood-fill brain with perfect motion. This proves the
 *  whole sketch - motor control, turns, centring, wall reading, self-check -
 *  by compiling firmware/mouse_map/mouse_map.ino UNCHANGED against fake
 *  Arduino/Wire/VL53L0X/Preferences headers (fakehw/) backed by a simulation:
 *
 *    - motors: dead-band (sticks until enough PWM), lag, left/right mismatch,
 *      and extra drag when spinning in place (carpet scrub)
 *    - carpet: body rotates/moves a bit less than the wheels say (slip), more
 *      so along the pile, so encoders over-read and only the gyro knows the
 *      true rotation
 *    - gyro: mounted upside-down (reads negative turning left), bias, drift, noise
 *    - encoders: real A/B quadrature driving the sketch's own ISRs; the right
 *      encoder is wired backwards, like the real robot
 *    - VL53L0X: 3 rays per reading cast at real wall/post geometry, noise,
 *      drop-outs, and continuous-mode timing (a read waits for the next result)
 *    - body: 100 x 80 mm outline; any wall contact is counted
 *
 *  Each trial is a random 16x16 maze and randomised robot/carpet parameters.
 *  A trial passes only if it reaches the goal with zero wall contacts, knows
 *  where it really is, and has no walls in its map that don't exist.
 *
 *    ./build.sh                     build
 *    ./build/robot_sim 100          100 trials (seeds 1..100)
 *    ./build/robot_sim 100 500      100 trials starting at seed 500
 *    ./build/robot_sim -v 7         one trial, full serial output
 * ============================================================================
 */
#include "fakehw/Arduino.h"
#include "fakehw/Wire.h"
#include "fakehw/VL53L0X.h"
#include "fakehw/Preferences.h"
#include <random>
#include <vector>
#include <map>
#include <unistd.h>
#include <sys/wait.h>

#include MOUSE_SKETCH   // Arduino-prototyped copy of mouse_map.ino, made by build.sh

std::map<std::string, std::map<std::string, PrefValue>> g_prefs;
SimSerial Serial;
TwoWire Wire;

namespace sim {
const double CELL = 180, HW = 6;                   // cell pitch, half wall thickness
const double TRACK = 85;                           // wheel separation
const double BODY_FRONT = 55, BODY_BACK = 45, BODY_HALF_W = 40;
const double SUB_US = 50;                          // physics substep
const int    GRID = 16;

std::mt19937 rng;
double U(double a, double b) { return std::uniform_real_distribution<double>(a, b)(rng); }
double G() { return std::normal_distribution<double>(0, 1)(rng); }

bool wall[GRID][GRID][4];
struct Rect { double x0, y0, x1, y1; };
std::vector<Rect> rects;

double t = 0, limitUs = 0;
double x, y, th, vL, vR, eL, eR, snapX, snapY, snapTh;
int    dutyL, dutyR, pinLvl[64];
void (*isr[64])() = { nullptr };
double kvL, kvR, deadStL, deadStR, scrub, tau, rotEff, linEff, mmPerTick, pileDir, pileAmp;
double gyroBias, omegaDps;
double bootFrom = -1, bootTo = -1;
int    contacts = 0, subCount = 0;
bool   touching = false, started = false, verbose = false;
std::string out;
uint8_t txAddr, txBuf[8], reg68, rx[2];
int    txLen, rxPos, rxLen;

// ---------------------------------------------------------------- the maze
void removeWall(int cx, int cy, int d) {
  wall[cx][cy][d] = false;
  int nx = cx + DIR_DX[d], ny = cy + DIR_DY[d];
  if (nx >= 0 && nx < GRID && ny >= 0 && ny < GRID) wall[nx][ny][dirOpposite(d)] = false;
}
void addWall(int cx, int cy, int d) {
  wall[cx][cy][d] = true;
  int nx = cx + DIR_DX[d], ny = cy + DIR_DY[d];
  if (nx >= 0 && nx < GRID && ny >= 0 && ny < GRID) wall[nx][ny][dirOpposite(d)] = true;
}
bool truthWall(int cx, int cy, int d) {
  if (cx < 0 || cx >= GRID || cy < 0 || cy >= GRID) return true;
  return wall[cx][cy][d];
}
void genMaze() {   // backtracker + braid + open centre, like maze_sim.cpp
  for (int i = 0; i < GRID; i++) for (int j = 0; j < GRID; j++) for (int d = 0; d < 4; d++) wall[i][j][d] = true;
  bool vis[GRID][GRID] = {{false}};
  std::vector<std::pair<int, int>> st{{0, 0}};
  vis[0][0] = true;
  while (!st.empty()) {
    auto [cx, cy] = st.back();
    int order[4] = {0, 1, 2, 3};
    for (int i = 3; i > 0; i--) std::swap(order[i], order[rng() % (i + 1)]);
    bool adv = false;
    for (int d : order) {
      int nx = cx + DIR_DX[d], ny = cy + DIR_DY[d];
      if (nx < 0 || nx >= GRID || ny < 0 || ny >= GRID || vis[nx][ny]) continue;
      removeWall(cx, cy, d); vis[nx][ny] = true; st.push_back({nx, ny}); adv = true; break;
    }
    if (!adv) st.pop_back();
  }
  for (int i = 0; i < GRID; i++) for (int j = 0; j < GRID; j++) for (int d = 0; d < 2; d++) {
    int nx = i + DIR_DX[d], ny = j + DIR_DY[d];
    if (nx < GRID && ny < GRID && wall[i][j][d] && U(0, 1) < 0.15) removeWall(i, j, d);
  }
  int c = GRID / 2;
  removeWall(c - 1, c - 1, DIR_N); removeWall(c - 1, c - 1, DIR_E);
  removeWall(c, c, DIR_S);         removeWall(c, c, DIR_W);
  addWall(0, 0, DIR_E); removeWall(0, 0, DIR_N);    // competition start square
}
bool solvable() {
  bool seen[GRID][GRID] = {{false}};
  std::vector<std::pair<int, int>> q{{0, 0}};
  seen[0][0] = true;
  for (size_t h = 0; h < q.size(); h++) {
    auto [cx, cy] = q[h];
    if ((cx == 7 || cx == 8) && (cy == 7 || cy == 8)) return true;
    for (int d = 0; d < 4; d++) {
      if (truthWall(cx, cy, d)) continue;
      int nx = cx + DIR_DX[d], ny = cy + DIR_DY[d];
      if (!seen[nx][ny]) { seen[nx][ny] = true; q.push_back({nx, ny}); }
    }
  }
  return false;
}
void buildRects() {
  rects.clear();
  for (int i = 0; i <= GRID; i++) for (int j = 0; j <= GRID; j++)
    rects.push_back({i * CELL - HW, j * CELL - HW, i * CELL + HW, j * CELL + HW});   // posts
  for (int i = 0; i < GRID; i++) for (int j = 0; j < GRID; j++) {
    if (truthWall(i, j, DIR_N)) rects.push_back({i * CELL - HW, (j + 1) * CELL - HW, (i + 1) * CELL + HW, (j + 1) * CELL + HW});
    if (truthWall(i, j, DIR_E)) rects.push_back({(i + 1) * CELL - HW, j * CELL - HW, (i + 1) * CELL + HW, (j + 1) * CELL + HW});
    if (j == 0 && truthWall(i, j, DIR_S)) rects.push_back({i * CELL - HW, -HW, (i + 1) * CELL + HW, HW});
    if (i == 0 && truthWall(i, j, DIR_W)) rects.push_back({-HW, j * CELL - HW, HW, (j + 1) * CELL + HW});
  }
}

// ---------------------------------------------------------------- geometry
double castRay(double ox, double oy, double ang) {
  double dx = cos(ang), dy = sin(ang), best = 1e9;
  for (const Rect &r : rects) {
    double t0 = -1e9, t1 = 1e9;
    if (fabs(dx) < 1e-12) { if (ox < r.x0 || ox > r.x1) continue; }
    else { double a = (r.x0 - ox) / dx, b = (r.x1 - ox) / dx; t0 = max(t0, min(a, b)); t1 = min(t1, max(a, b)); }
    if (fabs(dy) < 1e-12) { if (oy < r.y0 || oy > r.y1) continue; }
    else { double a = (r.y0 - oy) / dy, b = (r.y1 - oy) / dy; t0 = max(t0, min(a, b)); t1 = min(t1, max(a, b)); }
    if (t1 >= t0 && t1 > 0) best = min(best, max(t0, 0.0));
  }
  return best;
}
bool bodyHitsWall(double px, double py, double pth) {
  double c = cos(pth), s = sin(pth);
  for (double fx = -BODY_BACK; fx <= BODY_FRONT + 0.1; fx += 12.5)
    for (double fy : {-BODY_HALF_W, BODY_HALF_W}) {
      double wx = px + fx * c - fy * s, wy = py + fx * s + fy * c;
      for (const Rect &r : rects)
        if (wx > r.x0 && wx < r.x1 && wy > r.y0 && wy < r.y1) return true;
    }
  for (double fy = -BODY_HALF_W; fy <= BODY_HALF_W + 0.1; fy += 10)
    for (double fx : {-BODY_BACK, BODY_FRONT}) {
      double wx = px + fx * c - fy * s, wy = py + fx * s + fy * c;
      for (const Rect &r : rects)
        if (wx > r.x0 && wx < r.x1 && wy > r.y0 && wy < r.y1) return true;
    }
  return false;
}

// ---------------------------------------------------------------- physics
void motor(double cmd, double kv, double deadStatic, double &v, double dt) {
  double mag = fabs(cmd), target = 0;
  if (mag > 0 && (fabs(v) > 3 || mag >= deadStatic))           // stuck until breakaway
    target = (cmd > 0 ? 1 : -1) * max(0.0, mag - 0.75 * deadStatic) * kv;
  v += (target - v) * min(1.0, dt / tau);
}
void setPin(int p, int lvl) {
  if (pinLvl[p] == lvl) return;
  pinLvl[p] = lvl;
  if (isr[p]) isr[p]();
}
void moveEncoder(double &e, double de, int c1, int c2, bool wiredBackwards) {
  e += de;
  double ph = wiredBackwards ? -e : e;
  setPin(c1, (int)floor(ph) & 1);
  setPin(c2, (int)floor(ph + 0.5) & 1);
}
void physStep(double dt) {
  int sL = pinLvl[PIN_L_DIR] ? +1 : -1;          // left motor: DIR HIGH = forward
  int sR = pinLvl[PIN_R_DIR] ? -1 : +1;          // right motor: DIR LOW = forward
  double cL = dutyL * sL, cR = dutyR * sR;
  bool spin = (cL > 0 && cR < 0) || (cL < 0 && cR > 0);
  motor(cL, kvL, deadStL + (spin ? scrub : 0), vL, dt);
  motor(cR, kvR, deadStR + (spin ? scrub : 0), vR, dt);
  double pile = 1.0 - pileAmp * 0.5 * (1.0 + cos(th - pileDir));   // carpet pile: slips more one way
  double v = 0.5 * (vL + vR) * linEff * pile, w = (vR - vL) / TRACK * rotEff;
  th += w * dt; x += v * cos(th) * dt; y += v * sin(th) * dt;
  omegaDps = w * 180.0 / PI;
  moveEncoder(eL, vL * dt / mmPerTick, 21, 22, false);
  moveEncoder(eR, vR * dt / mmPerTick, 11, 23, true);
  gyroBias += 0.003 * G() * sqrt(dt);
}
void summarizeAndExit(const char *why);
void advanceTo(double tt) {
  while (t < tt) {
    physStep(SUB_US * 1e-6);
    t += SUB_US;
    if (++subCount % 20 == 0) {                  // wall contact check every 1 ms
      if (bodyHitsWall(x, y, th)) {
        x = snapX; y = snapY; th = snapTh; vL = vR = 0;
        if (!touching) contacts++;
        touching = true;
      } else { touching = false; snapX = x; snapY = y; snapTh = th; }
    }
  }
  if (ledState == LED_ERROR) summarizeAndExit("HALT");
  if (t > limitUs) summarizeAndExit("TIMEOUT");
}

// ---------------------------------------------------------------- results
void summarizeAndExit(const char *why) {
  int tx = (int)floor(x / CELL), ty = (int)floor(y / CELL);
  bool poseOK = (tx == posX && ty == posY);
  int falseWalls = 0;
  for (int i = 0; i < GRID; i++) for (int j = 0; j < GRID; j++) for (int d = 0; d < 4; d++)
    if (maze.hasWall(i, j, d) && !truthWall(i, j, d)) falseWalls++;
  float maxTurnErr = 0; int turns = 0;
  for (size_t p = out.find("  turn "); p != std::string::npos; p = out.find("  turn ", p + 1)) {
    float want, got;
    if (sscanf(out.c_str() + p, "  turn %f -> %f", &want, &got) == 2) { turns++; maxTurnErr = max(maxTurnErr, fabsf(got - want)); }
  }
  bool goal = (ledState == LED_DONE);
  bool pass = goal && contacts == 0 && poseOK && falseWalls == 0;
  printf("%-4s %-7s %5.0fs | contacts %d | pose %s | false walls %d | %d turns, worst %.1f deg\n",
         pass ? "PASS" : "FAIL", goal ? "GOAL" : why, t / 1e6, contacts,
         poseOK ? "ok" : "LOST", falseWalls / 2, turns, maxTurnErr);
  if (!pass && !verbose) {                       // last lines of serial, to see why
    size_t p = out.size(), lines = 0;
    while (p > 0 && lines < 30) { p--; if (out[p] == '\n') lines++; }
    printf("      true cell (%d,%d) heading %.0f deg, belief (%d,%d) dir %d\n------\n%s\n------\n",
           tx, ty, fmod(th * 180 / PI + 720, 360), posX, posY, headingDir, out.c_str() + p);
  }
  fflush(stdout);
  _exit(pass ? 0 : 1);
}

void runTrial(uint32_t seed) {
  rng.seed(seed);
  do { genMaze(); } while (!solvable());
  buildRects();
  kvL = U(4.5, 6.0);  kvR = U(4.5, 6.0);         // mm/s per PWM once moving
  deadStL = U(45, 60); deadStR = U(38, 52);      // breakaway PWM on carpet
  scrub = U(5, 20);                              // extra drag spinning in place
  tau = U(0.04, 0.09);
  rotEff = U(0.80, 0.97); linEff = U(0.95, 1.0); // carpet slip
  pileDir = U(0, 2 * PI); pileAmp = U(0, 0.04);  // ...and up to 4% more in the pile direction
  mmPerTick = PI * U(43.3, 44.7) / 402.0;        // real wheel vs the 44 mm in code
  gyroBias = U(2.5, 4.0);
  if (U(0, 1) < 0.5) {                           // half the time: calibrate was run
    g_prefs["mousecal"]["ok"].b = true;
    g_prefs["mousecal"]["minL"].i = (int)(deadStL + 5);
    g_prefs["mousecal"]["minR"].i = (int)(deadStR + 5);
  }
  x = 90 + 4 * G(); y = 90 + 4 * G(); th = PI / 2 + 2 * G() * PI / 180;   // placed by hand
  snapX = x; snapY = y; snapTh = th;
  vL = vR = eL = eR = 0;
  limitUs = 20 * 60e6;

  setup();
  bootFrom = t + 200e3; bootTo = bootFrom + 150e3;                         // press BOOT
  while (true) {
    loop();
    if (running) started = true;
    if (started && !running) summarizeAndExit("STOPPED");
    if (t > limitUs) summarizeAndExit("TIMEOUT");
  }
}
}  // namespace sim

// ---------------------------------------------------------------- fake hardware
void delay(unsigned long ms) { sim::advanceTo(sim::t + ms * 1000.0); }
unsigned long millis() { return (unsigned long)(sim::t / 1000.0); }
unsigned long micros() { return (unsigned long)sim::t; }
void pinMode(int, int) {}
void digitalWrite(int p, int v) { sim::pinLvl[p] = v; }
int digitalRead(int p) {
  if (p == PIN_BOOT_BTN) return (sim::t >= sim::bootFrom && sim::t < sim::bootTo) ? LOW : HIGH;
  return sim::pinLvl[p];
}
bool ledcAttach(int, int, int) { return true; }
bool ledcWrite(int p, uint32_t d) {
  if (p == PIN_L_PWM) sim::dutyL = d;
  else if (p == PIN_R_PWM) sim::dutyR = d;
  return true;
}
void attachInterrupt(int p, void (*fn)(), int) { sim::isr[p] = fn; }

int SimSerial::available() { return 0; }
int SimSerial::read() { return -1; }
void SimSerial::print(const char *s) { sim::out += s; if (sim::verbose) fputs(s, stdout); }
int SimSerial::printf(const char *fmt, ...) {
  char b[512]; va_list ap; va_start(ap, fmt); int n = vsnprintf(b, sizeof(b), fmt, ap); va_end(ap);
  print(b); return n;
}

bool TwoWire::begin(int, int) { return true; }
void TwoWire::setClock(uint32_t) {}
void TwoWire::beginTransmission(uint8_t a) { sim::txAddr = a; sim::txLen = 0; }
size_t TwoWire::write(uint8_t b) { if (sim::txLen < 8) sim::txBuf[sim::txLen++] = b; return 1; }
uint8_t TwoWire::endTransmission(bool) {
  sim::advanceTo(sim::t + 100.0 * (sim::txLen + 1));          // ~100 us per byte at 100 kHz
  if (sim::txAddr == MPU_ADDR && sim::txLen >= 1) sim::reg68 = sim::txBuf[0];
  bool known = sim::txAddr == MPU_ADDR || sim::txAddr == 0x30 || sim::txAddr == 0x31 || sim::txAddr == 0x32;
  return known ? 0 : 2;
}
uint8_t TwoWire::requestFrom(int a, int n) {
  sim::advanceTo(sim::t + 100.0 * (n + 1));
  sim::rxPos = sim::rxLen = 0;
  if (a == MPU_ADDR && sim::reg68 == MPU_GYRO_ZOUT_H && n == 2) {
    double dps = -sim::omegaDps + sim::gyroBias + 0.15 * sim::G();   // chip mounted upside-down
    long raw = lround(dps * GYRO_LSB_PER_DPS);
    raw = max(-32768L, min(32767L, raw));
    uint16_t u = (uint16_t)(int16_t)raw;
    sim::rx[0] = u >> 8; sim::rx[1] = u & 0xFF; sim::rxLen = 2;
    return 2;
  }
  return 0;
}
int TwoWire::read() { return sim::rxPos < sim::rxLen ? sim::rx[sim::rxPos++] : -1; }

bool VL53L0X::init(bool) { delay(2); return true; }
void VL53L0X::startContinuous(uint32_t) { ranging = true; phaseUs = sim::t + sim::U(0, budgetUs); consumedUs = -1; }
uint16_t VL53L0X::readRangeContinuousMillimeters() {
  double latest = phaseUs + floor((sim::t - phaseUs) / budgetUs) * budgetUs;   // newest result so far
  double ready = (latest > consumedUs && latest >= phaseUs) ? latest : max(latest, consumedUs) + budgetUs;
  if (ready > sim::t) sim::advanceTo(ready);                                  // wait for it
  consumedUs = ready;
  sim::advanceTo(sim::t + 400);                                               // I2C transfer
  double fx, fy, fa;                                                          // mounting (mm, rad)
  if (address == 0x30)      { fx = 30; fy = 35;  fa = PI / 2; }
  else if (address == 0x32) { fx = 30; fy = -35; fa = -PI / 2; }
  else                      { fx = 50; fy = 0;   fa = 0; }
  double c = cos(sim::th), s = sin(sim::th);
  double ox = sim::x + fx * c - fy * s, oy = sim::y + fx * s + fy * c, base = sim::th + fa;
  double d = 1e9;
  for (double off : {-0.17, 0.0, 0.17}) d = min(d, sim::castRay(ox, oy, base + off));
  d += sim::G() * (1.5 + 0.01 * d);
  if (d > 1200 || sim::U(0, 1) < 0.003) return 8190;                         // out of range / drop-out
  return (uint16_t)max(0.0, round(d));
}

// ---------------------------------------------------------------- main
int main(int argc, char **argv) {
  if (argc >= 3 && std::string(argv[1]) == "-v") {
    sim::verbose = true;
    sim::runTrial((uint32_t)atoi(argv[2]));
  }
  int n = argc >= 2 ? atoi(argv[1]) : 50, first = argc >= 3 ? atoi(argv[2]) : 1, passed = 0;
  for (int s = first; s < first + n; s++) {
    printf("seed %4d: ", s); fflush(stdout);
    pid_t pid = fork();
    if (pid == 0) sim::runTrial((uint32_t)s);
    int st = 0; waitpid(pid, &st, 0);
    if (WIFEXITED(st) && WEXITSTATUS(st) == 0) passed++;
  }
  printf("\n%d / %d trials passed (goal reached, no wall contact, pose correct, no false walls)\n", passed, n);
  return passed == n ? 0 : 1;
}
