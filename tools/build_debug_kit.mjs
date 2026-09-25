/** Publish the supplied debug kit without changing any sketch or its comments.
 * Run: node tools/build_debug_kit.mjs [path/to/micromouse-debug-kit]
 * With no argument, rebuild pages and ZIP from the checked-in website snapshot.
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { createHash } from 'node:crypto';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const published = path.join(root, 'downloads/micromouse-debug-kit');
const source = process.argv[2] ? path.resolve(process.argv[2]) : published;
const docs = path.join(root, 'content/docs/Micromouse2026/Debug');
const route = '#/docs/Micromouse2026/Debug/';
const download = '../../../../downloads/micromouse-debug-kit/';
const entries = [
  ['01_led_red', '01 — Check the onboard LED', 'USB only; no external wiring.', 'Solid red LED and an “alive” line every second.'],
  ['02_imu', '02 — Test the IMU', 'MPU-6050 / GY-521: VCC → 3V3, GND → GND, SDA → GPIO6, SCL → GPIO7. Leave XDA, XCL, AD0 and INT unconnected. Test the IMU alone on I²C first.', 'PASS, gyroZ near zero while still, and roughly 90° heading change for a quarter turn. Keep still during startup calibration.'],
  ['03_tof_1', '03 — Add the left distance sensor', 'Left ToF: VIN → 3V3, GND → GND, SDA → GPIO6, SCL → GPIO7, XSHUT → GPIO18. The IMU can stay connected. Leave front and right ToF disconnected.', '1/1 sensors OK; L at 0x30. The distance changes as your hand moves.'],
  ['04_tof_2', '04 — Add the front distance sensor', 'Keep the left sensor. Add front ToF to the shared 3V3/GND/GPIO6 SDA/GPIO7 SCL connections, with its XSHUT → GPIO19. Leave right ToF disconnected.', '2/2 sensors OK; L at 0x30 and F at 0x31. Cover each sensor in turn and check the matching column changes.'],
  ['05_tof_3', '05 — Add the right distance sensor', 'Keep left and front. Add right ToF to the shared power and I²C connections, with its XSHUT → GPIO20.', '3/3 sensors OK; L at 0x30, F at 0x31, R at 0x29. The right sensor keeps the default address.'],
  ['06_tof_3_imu', '06 — Test all sensors together', 'Use the wiring from steps 2–5. All four boards share 3V3/GND, SDA GPIO6 and SCL GPIO7. ToF XSHUT: left GPIO18, front GPIO19, right GPIO20. IMU XDA/XCL/AD0/INT stay unconnected.', 'Three ToF PASS messages plus IMU PASS; distance and heading values share one line. Keep still for gyro calibration.'],
  ['07_motor_1', '07 — Test the left motor', 'Driver DIR1 → GPIO0, PWM1 → GPIO2, VM → battery +. Join battery −, driver GND and ESP32 GND. Connect the left motor power pair to Motor A outputs. Driver VCC → 3V3 only if that pin exists; encoders are not needed.', 'After the red startup pause: green = forward 2 s, red = stop 1 s, blue = backward 2 s, red = stop 1 s; repeats.'],
  ['08_motors_2', '08 — Test both motors', 'Keep step 7 wiring; add DIR2 → GPIO3 and PWM2 → GPIO10, then right motor → Motor B outputs. PWM2 is GPIO10. Keep both wheels off the table.', 'Green = both forward, blue = both backward, yellow = spin left, purple = spin right; each lasts 2 s with a red 1 s stop between.'],
  ['tools/i2c_scan', 'Tool — Scan the I²C bus', 'Sensors: 3V3/GND, SDA → GPIO6, SCL → GPIO7. Connected ToF XSHUT pins → GPIO18/19/20.', 'Idle SDA=1 SCL=1. With IMU and ToF connected, expect 0x68 and 0x29. This tool wakes all ToFs at their default address: one 0x29 entry does not prove all three work.'],
  ['tools/pin_test', 'Tool — Check motor control pins', 'UNPLUG THE MOTOR FROM THE DRIVER FIRST. The test drives PWM fully HIGH, which would apply the whole 9V to a 6V motor. Meter on DC volts; black probe on GND, red probe on GPIO0 or GPIO2.', 'After blue startup: green = GPIO0/GPIO2 both 3.3V; yellow = 3.3V/0V; red = 0V/0V. Each stage lasts 2 s. No Serial output.'],
  ['tools/motor_sweep', 'Tool — Sweep motor power', 'Use step 7 wiring: DIR1 GPIO0, PWM1 GPIO2, VM battery + and common ground. Hold the wheel clear.', 'Blue startup, then a green forward ramp and a red backward ramp. Power rises to 170/255, holds, then stops. No Serial output.'],
  ['tools/encoder_test', 'Tool — Test the Motor A encoder', 'Use step 7 wiring plus encoder C1 → GPIO21, C2 → GPIO22, VCC → 3V3, GND → GND. Never connect encoder VCC to the motor battery. Hold the wheel clear: this sketch starts the motor automatically.', 'Counts change while the motor runs at PWM 85. Serial commands: s = stop, g = go, z = zero count. Green = running; red = stopped.'],
  ['imu_visualizer', 'Tool — Live IMU visualizer', 'Use step 2 wiring and upload this visualizer sketch. Close Arduino Serial Monitor before connecting the web page to the USB port.', 'A 3D board, heading, tilt and graphs follow your board. Keep still for calibration; the page can zero heading and recalibrate.'],
];

const relativeFiles = ['README.md', 'imu_visualizer/index.html', ...entries.map(([dir]) => `${dir}/${path.posix.basename(dir)}.ino`)];
// Validate the entire input before replacing any published assets.
const buffers = new Map(relativeFiles.map(rel => [rel, fs.readFileSync(path.join(source, rel))]));
fs.mkdirSync(published, { recursive: true });
fs.mkdirSync(docs, { recursive: true });
if (source !== published) {
  for (const [rel, data] of buffers) {
    const target = path.join(published, rel);
    fs.mkdirSync(path.dirname(target), { recursive: true });
    fs.writeFileSync(target, data);
  }
}

function page(title, order, body) {
  return `---\ntitle: ${title}\nlayout: default\nparent: Debug Kit\nnav_order: ${order}\n---\n\n# ${title}\n\n${body}\n`;
}
function link(entry) { return `[${entry[1]}](${route}${path.posix.basename(entry[0])}.md)`; }

for (const [i, entry] of entries.entries()) {
  const [dir, title, wiring, expected] = entry;
  const name = path.posix.basename(dir);
  const rel = `${dir}/${name}.ino`;
  const code = buffers.get(rel).toString('utf8').replace(/\r\n/g, '\n');
  const header = code.split(/^#include/m)[0].split('\n').filter(line => !/^\/\/ ={5,}/.test(line)).map(line => line.replace(/^\/\/ ?/, '')).join('\n').trim();
  const motor = /motor|encoder|pin_test/.test(name);
  const warning = name === 'pin_test'
    ? '{: .warning}\n> Disconnect the motor from the driver **before uploading**. This pin test drives PWM fully on; it does not use the 170/255 motor limit.\n\n'
    : motor ? '{: .warning}\n> Lift the wheels before uploading: motor tests start automatically and repeat. Disconnect motor power before rewiring. Keep the supplied SPEED_MAX limit of 170/255 for the kit’s 9V motor supply.\n\n' : '';
  const visualizer = name === 'imu_visualizer'
    ? `## Open the visualizer\n\n[Launch the IMU visualizer](${download}imu_visualizer/index.html). Use Chrome or Edge, close Serial Monitor, choose **Connect board**, and select the ESP32 port. Use the hosted HTTPS page or localhost for USB access. **Try demo** works without a board. The matching sketch below is required; step 2 does not send the visualizer’s data format.\n\nThe full-kit ZIP includes the page for local use.\n\n` : '';
  const tofNote = i >= 2 && i <= 5 ? 'Install **VL53L0X by Pololu** in Library Manager. `Adafruit_VL53L0X` is a different library. `---` means out of range or a read timeout in these sketches; `FAIL` means initialization failed. If `---` persists with a nearby wall, check wiring and rerun the previous step.\n\n' : '';
  const next = i < 8 ? `${i > 0 ? `Previous: ${link(entries[i - 1])}. ` : ''}${i < 7 ? `Next: ${link(entries[i + 1])}.` : 'All eight checks complete. Use the extra tools below when a subsystem needs more diagnosis.'}` : '[Back to all steps and tools](#/docs/Micromouse2026/Debug/index.md).';
  const body = `[Debug kit setup and all steps](${route}index.md) · [Event pin map](#/docs/Micromouse2026/Hardware/ESP32C6.md)\n\n${warning}## Connect\n\n${wiring}\n\n## Run and check\n\n${expected}\n\n${tofNote}Use **ESP32C6 Dev Module**, **USB CDC On Boot: Enabled**, and **115200 baud / No Line Ending**. Open this sketch in its own Arduino sketch folder, upload, then press RESET with Serial Monitor open to see startup messages. Motor LED tests also work without Serial Monitor.\n\n${visualizer}## Copy the code into Arduino IDE\n\n1. In Arduino IDE, choose **File → New Sketch**.\n2. Save it as <code>${name}</code>. Arduino IDE creates a folder named <code>${name}</code> containing <code>${name}.ino</code>.\n3. Expand **Show complete sketch** below and select **COPY**.\n4. Replace everything in the Arduino editor with the copied code.\n5. Save, choose **ESP32C6 Dev Module** and the correct port, then upload.\n\nKeep the folder and sketch names identical. Arduino requires this structure:\n\n\`\`\`text\n${name}/\n└── ${name}.ino\n\`\`\`\n\n<details>\n<summary>Show complete sketch — then select COPY</summary>\n\n\`\`\`cpp\n${code.trimEnd()}\n\`\`\`\n\n</details>\n\n## Original wiring notes and expected output\n\nThese are the comments supplied at the top of this sketch, with comment markers removed. They are the reference for this test.\n\n\`\`\`text\n${header}\n\`\`\`\n\n## Continue\n\n${next}\n\nIf a step fails, switch off, disconnect the part you just added, and rerun the last passing step. Check the wiring above before moving on. [Extra diagnostic tools](${route}index.md).`;
  fs.writeFileSync(path.join(docs, `${name}.md`), page(title, i + 1, body));
}

const overview = `---
title: Debug Kit
layout: default
parent: Micromouse 2026 Resources
nav_order: 4
---

# Test your mouse, one part at a time

Start with USB and the onboard LED. Add the IMU, one distance sensor at a time, then the motors. Each page has copyable code, its original wiring comments, expected output and exact folder instructions. Fix a failing step before adding the next part.

[Start step 1](${route}01_led_red.md) · [Event wiring map](#/docs/Micromouse2026/Hardware/ESP32C6.md)

## Arduino setup

1. In Arduino IDE, add <code>https://espressif.github.io/arduino-esp32/package_esp32_index.json</code> under File → Preferences → Additional Board Manager URLs.
2. In Boards Manager, install **esp32 by Espressif Systems, version 3.0.0 or newer**, as specified by the supplied kit.
3. Select **ESP32C6 Dev Module** and the board’s port. Set **Tools → USB CDC On Boot → Enabled**.
4. Set Serial Monitor to **115200 baud**, **No Line Ending**.
5. For steps 3–6, install **VL53L0X by Pololu**. Do not substitute <code>Adafruit_VL53L0X</code>. The IMU sketches need no extra library.
6. Open the chosen check, create a new Arduino sketch with the name shown, expand its complete code and select **COPY**. Replace the new sketch with that code, save and upload it. Each guide shows the required folder structure.

Power the controller from USB for these tests. Sensors and encoder VCC use **3V3**. Motor-driver VM uses the motor battery, with battery −, driver GND and ESP32 GND joined. The motor tests assume **9V** and cap PWM at **170/255**; keep that cap. Read [battery and power](#/docs/Micromouse2026/Hardware/BuckConverter.md) before step 7.

## The eight checks

| Step | Connect / test | Pass looks like |
|---|---|---|
${entries.slice(0,8).map(entry => `| ${link(entry)} | ${entry[2]} | ${entry[3]} |`).join('\n')}

Only connect the ToF sensors listed for the step you are running. An extra powered sensor with XSHUT unconnected wakes at <code>0x29</code> and can clash. Once added in step 2, the IMU can stay connected during the ToF steps.

When you rerun an earlier ToF step on an assembled mouse, disconnect power from ToF boards that step does not control. Step 3 controls only left; step 4 controls left and front.

## Extra tools

| Tool | When to use it |
|---|---|
${entries.slice(8).map(entry => `| ${link(entry)} | ${entry[3]} |`).join('\n')}

{: .warning}
> **Pin test: unplug the motor before uploading.** It drives PWM fully HIGH and would apply the whole 9V to a 6V motor. All moving-motor tests must run with the wheels raised.

## If something fails

| Symptom | First check |
|---|---|
| No upload port | Use a USB data cable, choose the COM port; if needed hold BOOT, tap RESET, then release BOOT and upload. |
| Red LED but Serial is blank | Enable USB CDC On Boot, upload again, use 115200 baud, open the monitor and press RESET. |
| Old behavior after copying a sketch | Confirm the intended code is in the active Arduino tab, save, then upload it. Copying alone does not flash the board. |
| No I²C devices | Check power, ground and GPIO6/7. Run the I²C scan; step 2 can also detect swapped SDA/SCL. Use MPU SDA/SCL, leave XDA/XCL/AD0/INT unconnected. |
| One ToF column fails or the wrong column changes | Check that sensor’s XSHUT wire: left 18, front 19, right 20. Recheck the last passing step with extra ToFs disconnected. |
| Motors stay still while LED cycles | Check PWM and DIR wires, common ground, battery on VM and battery charge. If present, VCC needs 3V3 and STBY/EN/SLP must be HIGH. |
| Motor hums without turning | Use motor sweep; check battery sag and a jammed wheel or gearbox. Do not raise SPEED_MAX. |
| Encoder stays at zero while turning | Check encoder 3V3/GND and C1 GPIO21, C2 GPIO22. Use the encoder test. |

## Source of these instructions

The embedded sketches and visualizer code are copied unchanged from the event’s <code>micromouse-debug-kit</code>. Wiring and expected results come from their top-of-file comments. Each page includes those original comments and the complete sketch, so you can compare the instructions directly with what you upload.
`;
fs.writeFileSync(path.join(docs, 'index.md'), overview);

// A dependency-free ZIP (stored entries) keeps Arduino's matching folder names.
const crcTable = Array.from({ length: 256 }, (_, n) => {
  for (let bit = 0; bit < 8; bit++) n = (n & 1) ? 0xedb88320 ^ (n >>> 1) : n >>> 1;
  return n >>> 0;
});
function crc32(data) {
  let crc = 0xffffffff;
  for (const byte of data) crc = crcTable[(crc ^ byte) & 255] ^ (crc >>> 8);
  return (crc ^ 0xffffffff) >>> 0;
}
const local = [], central = [];
let offset = 0;
for (const [rel, data] of buffers) {
  const name = Buffer.from(`micromouse-debug-kit/${rel}`);
  const checksum = crc32(data);
  const header = Buffer.alloc(30);
  header.writeUInt32LE(0x04034b50, 0); header.writeUInt16LE(20, 4);
  header.writeUInt16LE(0x21, 12); // 1980-01-01; deterministic archive
  header.writeUInt32LE(checksum, 14); header.writeUInt32LE(data.length, 18);
  header.writeUInt32LE(data.length, 22); header.writeUInt16LE(name.length, 26);
  local.push(header, name, data);
  const record = Buffer.alloc(46);
  record.writeUInt32LE(0x02014b50, 0); record.writeUInt16LE(20, 4); record.writeUInt16LE(20, 6);
  record.writeUInt16LE(0x21, 14); record.writeUInt32LE(checksum, 16);
  record.writeUInt32LE(data.length, 20); record.writeUInt32LE(data.length, 24);
  record.writeUInt16LE(name.length, 28); record.writeUInt32LE(offset, 42);
  central.push(record, name);
  offset += header.length + name.length + data.length;
}
const directory = Buffer.concat(central);
const end = Buffer.alloc(22);
end.writeUInt32LE(0x06054b50, 0); end.writeUInt16LE(buffers.size, 8); end.writeUInt16LE(buffers.size, 10);
end.writeUInt32LE(directory.length, 12); end.writeUInt32LE(offset, 16);
fs.writeFileSync(path.join(root, 'downloads/micromouse-debug-kit.zip'), Buffer.concat([...local, directory, end]));
fs.writeFileSync(path.join(root, 'downloads/micromouse-debug-kit-manifest.json'), JSON.stringify(Object.fromEntries([...buffers].map(([rel, data]) => [rel, createHash('sha256').update(data).digest('hex')])), null, 2) + '\n');
console.log(`Published ${buffers.size} original files, ${entries.length + 1} debug pages, and complete-kit ZIP.`);
