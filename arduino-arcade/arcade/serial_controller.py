"""PySerial backend.  This is the only module allowed to import ``serial``."""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass
from typing import List, Optional

from .controller import Controller, RawState, parse_packet

BAUD_RATE = 115200
#: Vendor IDs of common Arduino Uno / clone USB-serial bridges.
KNOWN_VIDS = {
    0x2341: "Arduino",
    0x2A03: "Arduino (org)",
    0x1A86: "CH340 clone",
    0x0403: "FTDI",
    0x10C4: "CP210x",
    0x1B4F: "SparkFun",
    0x239A: "Adafruit",
}
KEYWORDS = ("arduino", "ch340", "ch341", "usb serial", "usb-serial", "cp210", "ftdi", "wch")

try:  # pragma: no cover - import guard exercised only without pyserial
    import serial
    from serial.tools import list_ports

    SERIAL_AVAILABLE = True
except Exception:  # pragma: no cover
    serial = None
    list_ports = None
    SERIAL_AVAILABLE = False


@dataclass
class PortInfo:
    device: str
    description: str = ""
    hwid: str = ""
    score: int = 0

    @property
    def likely(self) -> bool:
        return self.score > 0


def score_port(device: str, description: str, vid) -> int:
    """Heuristic likelihood that a port is our Arduino controller."""
    score = 0
    if vid in KNOWN_VIDS:
        score += 10
    text = f"{device} {description}".lower()
    if any(word in text for word in KEYWORDS):
        score += 5
    if "bluetooth" in text or "virtual" in text:
        score -= 20
    return score


def list_serial_ports() -> List[PortInfo]:
    """All serial ports, best Arduino candidates first."""
    if not SERIAL_AVAILABLE:
        return []
    found = []
    try:
        ports = list(list_ports.comports())
    except Exception:
        return []
    for port in ports:
        description = getattr(port, "description", "") or ""
        info = PortInfo(
            device=port.device,
            description=description,
            hwid=getattr(port, "hwid", "") or "",
            score=score_port(port.device, description, getattr(port, "vid", None)),
        )
        found.append(info)
    found.sort(key=lambda p: (-p.score, p.device))
    return found


def likely_ports() -> List[PortInfo]:
    return [p for p in list_serial_ports() if p.likely]


class SerialController(Controller):
    """Reads controller packets on a background thread and reconnects itself.

    The render loop never blocks on serial I/O: it just reads the most recent
    decoded packet.
    """

    kind = "arduino"

    #: Seconds without a valid packet before we declare the link dead.
    TIMEOUT = 1.2
    #: Delay between reconnection attempts.
    RETRY_DELAY = 1.5

    def __init__(self, port: str, calibration=None, auto_reconnect: bool = True, open_serial=None):
        super().__init__(calibration)
        self.port = port
        self.auto_reconnect = auto_reconnect
        self._open_serial = open_serial or self._default_open
        self._serial = None
        self._lock = threading.Lock()
        self._latest: Optional[RawState] = None
        self._last_packet_time = 0.0
        self._connected = False
        self._stop = threading.Event()
        self.error = ""
        self.packets_received = 0
        self.bad_packets = 0
        self._thread = threading.Thread(target=self._run, name="arcade-serial", daemon=True)
        self._thread.start()

    # ------------------------------------------------------------ internals

    def _default_open(self, port: str):  # pragma: no cover - needs hardware
        if not SERIAL_AVAILABLE:
            raise RuntimeError("pyserial is not installed")
        return serial.Serial(port, BAUD_RATE, timeout=0.2)

    def _run(self) -> None:
        buffer = b""
        while not self._stop.is_set():
            if self._serial is None:
                try:
                    self._serial = self._open_serial(self.port)
                    self.error = ""
                    buffer = b""
                except Exception as exc:
                    self.error = f"{exc.__class__.__name__}: {exc}"
                    self._connected = False
                    if not self.auto_reconnect:
                        return
                    self._stop.wait(self.RETRY_DELAY)
                    continue
            try:
                chunk = self._serial.read(256)
                if not chunk:
                    # No data is not an error by itself; the timeout check
                    # below decides whether the link is really gone.
                    if time.monotonic() - self._last_packet_time > self.TIMEOUT:
                        self._connected = False
                    continue
                buffer += chunk
                if len(buffer) > 4096:  # runaway garbage guard
                    buffer = buffer[-1024:]
                while b"\n" in buffer:
                    line, buffer = buffer.split(b"\n", 1)
                    state = parse_packet(line)
                    if state is None:
                        self.bad_packets += 1
                        continue
                    with self._lock:
                        self._latest = state
                    self.packets_received += 1
                    self._last_packet_time = time.monotonic()
                    self._connected = True
            except Exception as exc:
                # Device unplugged, driver hiccup, decode failure - drop the
                # handle and let the reconnect loop take over.
                self.error = f"{exc.__class__.__name__}: {exc}"
                self._close_serial()
                self._connected = False
                if not self.auto_reconnect:
                    return
                self._stop.wait(self.RETRY_DELAY)

    def _close_serial(self) -> None:
        if self._serial is not None:
            try:
                self._serial.close()
            except Exception:
                pass
            self._serial = None

    # ----------------------------------------------------------------- API

    def _poll(self, dt: float, events) -> Optional[RawState]:
        with self._lock:
            state = self._latest
        if state is None:
            return None
        if time.monotonic() - self._last_packet_time > self.TIMEOUT:
            self._connected = False
        return state.copy()

    @property
    def connected(self) -> bool:
        return self._connected

    @property
    def status_text(self) -> str:
        if self._connected:
            return f"{self.port} connected"
        if self.error:
            return f"{self.port}: {self.error}"
        return f"{self.port}: waiting for data"

    def close(self) -> None:
        self._stop.set()
        if self._thread.is_alive():
            self._thread.join(timeout=1.0)
        self._close_serial()


def autodetect(calibration=None, preferred: str = "") -> tuple[Optional[SerialController], List[PortInfo]]:
    """Connect automatically when the choice is unambiguous.

    Returns ``(controller, candidates)``.  When ``controller`` is ``None`` the
    caller should show the device-selection screen (or fall back to keyboard).
    """
    candidates = likely_ports()
    if preferred:
        for info in candidates or list_serial_ports():
            if info.device == preferred:
                return SerialController(preferred, calibration), candidates
    if len(candidates) == 1:
        return SerialController(candidates[0].device, calibration), candidates
    return None, candidates
