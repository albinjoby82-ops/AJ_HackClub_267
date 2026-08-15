---
id: A6
title: Laptop setup
section: competitor
priority: P0
audience: competitors
status: draft
---

# Laptop setup

> ## Do this before the day
>
> **Time estimate: 60 to 90 minutes**, including downloads. Do not start this at
> the Dublin Micromouse Open 2026. The build window is six hours. A laptop that
> is not ready costs your team an hour you cannot get back.
>
> Finish every step, then work through [You are ready if...](#you-are-ready-if)
> at the bottom of this page. If something fails, email
> eleceng@ucdsocieties.ie before the event, not on the day.

[DECISION REQUIRED: confirm exact ESP32 board model shipped in the kit. This page
is written for the ESP32-C6 using the ESP32-C6-DevKitC-1 as the reference layout.
Board name, pinout and USB arrangement may differ.]

## The verification chain

Every step depends on the one before it. Do not skip ahead: a green tick at the
end only means something if each earlier link passed.

```mermaid
flowchart LR
    A[INSTALL] --> B[COMPILE]
    B --> C[CONNECT]
    C --> D[FLASH]
    D --> E[SERIAL OUTPUT]
    E --> F[READY]
```

## 0. Before you install anything

| Check | Why it matters |
|---|---|
| You can install software on this laptop | You need administrator or `sudo` rights for the IDE, drivers and Git. |
| The laptop is not a locked-down work or college managed device | Managed laptops commonly block driver installation, USB serial devices, unsigned binaries and outbound developer traffic. |
| You have about 5 GB free disk space | The Arduino IDE plus the ESP32 core and toolchain is large. |
| You have a working charger | Six hours of compiling flattens a battery. |

**Managed laptop warning.** If your laptop is issued by an employer, a placement
company or a college IT department, assume it will block something. Device
management can silently prevent USB serial drivers from loading, quarantine the
ESP32 toolchain, or refuse the network access the AI coding agent CLI needs.
Test the whole chain on that exact machine well in advance. If it fails, bring a
personal laptop instead. There is no time to argue with an IT helpdesk on the
day.

## 1. Install Arduino IDE 2

Download from the official Arduino site and install for your operating system.

- <https://www.arduino.cc/en/software>
- Step by step guide: <https://docs.arduino.cc/software/ide-v2/tutorials/getting-started/ide-v2-downloading-and-installing/>

| | Windows | macOS | Linux |
|---|---|---|---|
| **File** | `.exe` installer | `.dmg` | AppImage or `.zip` |
| **Install** | Run the installer, accept the driver prompts it shows. | Drag Arduino IDE into Applications. | Make the AppImage executable (`chmod +x`), then run it. |
| **First run** | Allow it through Windows Defender Firewall. | Right click, Open, if Gatekeeper blocks it. | If the AppImage will not start, install `libfuse2`. |

Open the IDE once and let it finish its first-run setup before continuing.

## 2. Add ESP32-C6 board support

1. Open **File > Preferences** (**Arduino IDE > Settings** on macOS).
2. In **Additional boards manager URLs**, paste the official Espressif stable
   index URL:

   ```text
   https://espressif.github.io/arduino-esp32/package_esp32_index.json
   ```

3. Click **OK**.
4. Open **Tools > Board > Boards Manager** (or the boards icon in the sidebar).
5. Search for `esp32`.
6. Select the package **esp32 by Espressif Systems**.

### Required core version

| Item | Value |
|---|---|
| Package name | esp32 by Espressif Systems |
| **Minimum version for ESP32-C6** | **3.0.0** |
| Recommended | The latest 3.x release offered in Boards Manager |

ESP32-C6 support arrived in the Arduino ESP32 core 3.0.0, which is based on
ESP-IDF v5.1.4. The 3.0.0 release notes state that it introduces "breaking
changes and support for new SoCs, ESP32-H2 and ESP32-C6"
(<https://github.com/espressif/arduino-esp32/releases/tag/3.0.0>). Core 2.x
cannot build for the ESP32-C6. If the ESP32-C6 boards do not appear in the board
list, you are on a 2.x core.

Installation takes several minutes and downloads a large toolchain. Do it on
good wifi, not on the venue network.

## 3. USB drivers

Which driver you need depends on how the board reaches your laptop. Two boards
that both say "ESP32-C6" can differ here.

| Board USB path | Driver needed? | Where it comes from |
|---|---|---|
| **Native USB Serial/JTAG** on the chip itself | Normally none | Class driver already in Windows 10 and 11, macOS and Linux. |
| **CP210x** USB-to-UART bridge | Yes on Windows, usually yes on older macOS | Silicon Labs CP210x VCP drivers. |
| **CH340 / CH34x** USB-to-UART bridge | Yes on Windows, often on macOS | WCH, the chip vendor. |
| **FTDI** bridge | Usually automatic on Windows 10 and 11 | FTDI VCP drivers if not. |

The ESP32-C6 has a USB peripheral, so a board wired to it can be flashed with no
external bridge and no vendor driver. The ESP32-C6-DevKitC-1 exposes **both** a
native USB Type-C port and a separate USB-to-UART bridge port, so on that board
your driver need depends on which socket you plug into. Espressif's serial
connection guide lists the CP210x and FTDI VCP drivers as the ones to install
when a bridge is used
(<https://docs.espressif.com/projects/esp-idf/en/stable/esp32c6/get-started/establish-serial-connection.html>).

| | Windows | macOS | Linux |
|---|---|---|---|
| **Native USB** | Works out of the box. | Works out of the box. | Works out of the box. |
| **Bridge chip** | Install the vendor VCP driver, then reboot. | Install the vendor VCP driver, then approve it in **System Settings > Privacy & Security**. | Driver is in the kernel. No download. |
| **Extra step** | None. | None. | Add yourself to the serial group, see below. |

### Linux serial permissions

Serial ports on Linux are owned by a group. Until your user is in it, the IDE
sees the port but cannot open it.

```bash
sudo usermod -a -G dialout $USER
```

On Arch Linux use the `uucp` group instead. **Log out and log back in** for the
change to apply. Do not work around this with `sudo arduino-ide`.

## 4. USB cable: data or charge only

This wastes more competitor time than any other single item. Many USB cables
sold with phones, power banks and battery packs carry power only. The board will
light up and look alive, and no serial port will ever appear.

| How to tell | What you see |
|---|---|
| Plug the board in | A data cable makes a new port appear (see step 6). A charge-only cable does not. |
| Cable markings | Charge-only cables are often marked "charge only", "power only", or with a battery icon. |
| Where it came from | Cables bundled with power banks, vape kits and cheap chargers are frequently charge only. |
| Substitution test | Try a second cable that you know has synced a phone to a computer. |

Bring **two** known-good data cables of the right connector type. Label them.
Cable type for the kit is confirmed in the packing list,
[A8 Venue, travel and what to bring](08-venue-and-what-to-bring.md).

## 5. Select the board

1. Connect the board with a data cable.
2. **Tools > Board > esp32**.
3. Choose the entry that matches your exact board. If your board is not listed
   by name, **ESP32C6 Dev Module** is the generic fallback.
4. Leave the remaining Tools options at their defaults for now.

Do not select a plain "ESP32 Dev Module": that targets the original ESP32, not
the C6, and the upload will fail.

## 6. Select the port

| | Windows | macOS | Linux |
|---|---|---|---|
| **Port looks like** | `COM3`, `COM7` | `/dev/cu.usbmodem…` or `/dev/cu.usbserial…` | `/dev/ttyACM0` or `/dev/ttyUSB0` |
| **Native USB** | `COM` port appears | `usbmodem` | `ttyACM0` |
| **Bridge chip** | `COM` port appears | `usbserial` | `ttyUSB0` |
| **Nothing listed** | Check Device Manager for a yellow warning icon. | Check **System Information > USB**. | Run `dmesg \| tail` right after plugging in. |

Identify the port by unplugging the board, looking at **Tools > Port**,
replugging, and looking again. The entry that appears is yours.

Some ESP32-C6 boards expose more than one serial connection. Choose the port
associated with the program you uploaded.

## 7. The verification sketch

This is the shortest sketch that proves the whole chain. Copy it into a new
sketch and save it as `micromouse_check`.

```cpp
// Dublin Micromouse Open 2026: laptop setup verification sketch.
// Proves compile, flash and serial output on an ESP32-C6.

// CHECK THIS PIN AGAINST YOUR BOARD'S PINOUT BEFORE RUNNING.
// Example only. Pick a free, exposed GPIO on your board and change this line.
// Avoid strapping pins (GPIO8, GPIO9 and GPIO15 on the ESP32-C6-DevKitC-1).
// Do not assume LED_BUILTIN exists or matches on every ESP32-C6 board.
// Some boards fit an addressable RGB LED, which will not respond to
// digitalWrite. If nothing lights up, wire a plain LED and resistor to this
// pin, or just trust the serial output below.
const int LED_PIN = 7;

unsigned long ticks = 0;

void setup() {
  Serial.begin(115200);
  delay(1000);              // Give native USB serial time to enumerate.
  pinMode(LED_PIN, OUTPUT);
  Serial.println("Micromouse laptop check: setup complete");
}

void loop() {
  digitalWrite(LED_PIN, HIGH);
  delay(500);
  digitalWrite(LED_PIN, LOW);
  delay(500);

  ticks++;
  Serial.print("tick ");
  Serial.println(ticks);
}
```

## 8. Compile

1. Click **Verify** (the tick icon).
2. Wait. The first compile for a new core downloads and builds a lot, and can
   take several minutes. Later compiles are much faster.
3. Success looks like a size report in the output pane, for example
   `Sketch uses ... bytes`.

If Verify fails, stop here. Do not try to flash. A compile error is a toolchain
problem, not a cable problem.

## 9. Flash the board

1. Confirm the board and port are still selected.
2. Click **Upload** (the arrow icon).
3. Watch for `Connecting...` then a percentage, then `Hard resetting...`.

If upload stalls on `Connecting...`, hold the board's **BOOT** button, start the
upload, and release BOOT once the percentage starts moving. Press **RESET**
afterwards if the board does not restart on its own.

## 10. Serial monitor

1. Open **Tools > Serial Monitor**, or the monitor icon at the top right.
2. Set the baud rate to **115200**. This must match `Serial.begin(115200)` in
   the sketch.
3. You should see:

   ```text
   Micromouse laptop check: setup complete
   tick 1
   tick 2
   tick 3
   ```

4. The LED should blink once per second, in step with the ticks.

Both together mean the chain is intact: INSTALL, COMPILE, CONNECT, FLASH,
SERIAL OUTPUT, READY.

## 11. Install and configure Git

Install Git, then set your identity so your commits are attributable.

| | Windows | macOS | Linux |
|---|---|---|---|
| **Get it** | <https://git-scm.com/downloads/win> (Git for Windows, includes Git Bash) | <https://git-scm.com/downloads/mac>, or `brew install git` | `sudo apt install git` on Debian and Ubuntu, or your distribution's package manager |
| **Check** | `git --version` in Git Bash | `git --version` in Terminal | `git --version` in a terminal |

Then, on any operating system:

```bash
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
git config --global init.defaultBranch main
```

Use the same email address as your GitHub account.

## 12. GitHub account and authentication

1. Create a GitHub account at <https://github.com> if you do not have one.
2. Turn on two-factor authentication. GitHub requires it for contributors.
3. Set up authentication so you can push without typing a password every time.
   Pick one:

| Method | Best for | Notes |
|---|---|---|
| **GitHub CLI** (<https://cli.github.com>) | Most people | Install, then `gh auth login` and follow the browser prompts. Handles credentials for you. |
| **SSH key** | Anyone comfortable with a terminal | Generate a key, add the public key to GitHub, test with `ssh -T git@github.com`. |
| **HTTPS with a personal access token** | Fallback | Your GitHub password will not work for pushing. Generate a token in GitHub settings. |

4. **Prove it works before the day.** Create a scratch repository on GitHub,
   clone it, commit a change, and push:

```bash
git clone <your-repo-url>
cd <your-repo>
echo "setup check" > check.txt
git add check.txt
git commit -m "Laptop setup check"
git push
```

A successful push is the test. A successful clone alone is not, because clones
of public repositories need no credentials.

## 13. AI coding agent CLI

AI coding agents are allowed and encouraged. See
[A4 AI coding agent policy](04-ai-agent-policy.md). Anthropic is the technical
partner for the Open, so Claude Code is the relevant CLI here.

Install and log in **before the day**, following the official documentation
rather than a command copied from anywhere else. Install commands change.

- Install and setup: <https://code.claude.com/docs/en/setup>
- Quickstart: <https://code.claude.com/docs/en/quickstart>

Notes that matter for the day:

| Item | Detail |
|---|---|
| Account | Claude Code requires a paid or Console account. The free Claude.ai plan does not include access. |
| Login | Run `claude` in a terminal and follow the browser prompts. |
| Verify | `claude --version` prints a version. `claude doctor` prints diagnostics. |
| Windows | Git for Windows is recommended alongside it, which you installed in step 11. |
| Network | An internet connection is required. Log in in advance so you are not fighting a login on venue wifi. |

Credits and how to redeem them are covered in
[A7 Sponsors and credits](07-sponsor-credits.md).

## Troubleshooting

Only the failures that actually happen. Work down the table in order.

| Symptom | Most likely cause | Fix |
|---|---|---|
| ESP32-C6 boards not listed under Tools > Board | Core is 2.x, or the boards manager URL was not saved | Boards Manager, confirm **esp32 by Espressif Systems** is **3.0.0 or later**. Re-check the URL in Preferences. |
| No serial port appears at all | Charge-only cable | Swap to a known data cable. See step 4. This is the most common cause by a wide margin. |
| Port still missing with a good cable | Missing bridge driver | Windows: check Device Manager for an unknown device, install the CP210x or CH34x driver, reboot. macOS: install the vendor driver and approve it in Privacy & Security. |
| `Permission denied` on `/dev/ttyUSB0` or `/dev/ttyACM0` | User not in the serial group (Linux) | `sudo usermod -a -G dialout $USER`, then log out and back in. `uucp` on Arch. |
| Upload times out on `Connecting...` | Board not in bootloader, or wrong port | Hold **BOOT**, start upload, release BOOT when it moves. Confirm the port and board selection. Close any other program holding the port. |
| Serial monitor shows nothing or garbage | Wrong baud rate, or wrong port on a multi-port board | Set the monitor to **115200**. Try the other port the board exposes. |

# You are ready if...

Tick every box on the laptop you are bringing. Every one of these is a link in
the chain.

- [ ] I can install software on this laptop, and it is not a locked-down managed device
- [ ] Arduino IDE 2 is installed and opens
- [ ] The Espressif boards manager URL is saved in Preferences
- [ ] **esp32 by Espressif Systems 3.0.0 or later** is installed
- [ ] The correct USB driver is installed, or my board needs none
- [ ] Linux only: my user is in the `dialout` (or `uucp`) group and I have logged back in
- [ ] I have two known-good USB **data** cables, tested and labelled
- [ ] My ESP32-C6 board appears under Tools > Board and is selected
- [ ] A serial port appears under Tools > Port when I plug the board in
- [ ] The verification sketch **compiles** with no errors
- [ ] The verification sketch **flashes** to the board successfully
- [ ] The onboard LED **blinks** once per second
- [ ] The serial monitor at 115200 shows `Micromouse laptop check: setup complete` and counting ticks
- [ ] Git is installed and `git --version` works
- [ ] `git config --global user.name` and `user.email` are set
- [ ] I have a GitHub account with two-factor authentication on
- [ ] I have **cloned** a repository successfully
- [ ] I have **pushed** a commit to GitHub successfully
- [ ] My AI coding agent CLI is installed and `claude --version` works
- [ ] I have **logged in** to the AI coding agent CLI successfully
- [ ] I did all of the above on the exact laptop I am bringing on the day

---

[Competitor documentation home](index.md) · Previous: [A5 Registration and FAQ](05-registration-and-faq.md) · Next: [A7 Sponsors and credits](07-sponsor-credits.md)

Related: [A7 Sponsors and credits](07-sponsor-credits.md) · [A8 Venue, travel and what to bring](08-venue-and-what-to-bring.md)
