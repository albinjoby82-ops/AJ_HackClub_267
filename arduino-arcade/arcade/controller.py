"""Shared controller API for Arduino Arcade.

Every game and screen in the arcade talks to a :class:`Controller`.  Nothing
outside :mod:`arcade.serial_controller` is allowed to touch PySerial.

The interface is deliberately tiny::

    controller.pot1          # calibrated float, 0.0 .. 1.0
    controller.pot2
    controller.pot1_raw      # int, 0 .. 1023
    controller.button1       # bool, currently held
    controller.button1_pressed   # bool, went down this frame
    controller.button1_released  # bool, went up this frame

Backends implement :meth:`Controller._poll` and return a :class:`RawState`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from .calibration import Calibration

NUM_BUTTONS = 4
POT_MAX = 1023


@dataclass
class RawState:
    """Un-processed snapshot of the physical controller."""

    pot1: int = 0
    pot2: int = 0
    buttons: List[bool] = field(default_factory=lambda: [False] * NUM_BUTTONS)

    def copy(self) -> "RawState":
        return RawState(self.pot1, self.pot2, list(self.buttons))


class Controller:
    """Base class providing smoothing, calibration and button edge detection."""

    #: Human readable backend name, shown in the dev overlay and launcher.
    kind = "none"

    def __init__(self, calibration: Optional[Calibration] = None, smoothing: float = 0.45):
        self.calibration = calibration or Calibration()
        # Exponential smoothing factor for the *normalised* pot values.  Kept
        # low enough that steering still feels immediate at 60 FPS.
        self.smoothing = smoothing
        self._raw = RawState()
        self._prev_buttons = [False] * NUM_BUTTONS
        self._pressed = [False] * NUM_BUTTONS
        self._released = [False] * NUM_BUTTONS
        self._norm = [0.0, 0.0]
        self._norm_ready = False
        self.status_message = ""

    # ------------------------------------------------------------------ API

    def update(self, dt: float, events=None) -> None:
        """Refresh controller state.  Call exactly once per frame."""
        new = self._poll(dt, events or [])
        if new is not None:
            self._raw = new

        target = (
            self.calibration.normalize(1, self._raw.pot1),
            self.calibration.normalize(2, self._raw.pot2),
        )
        if not self._norm_ready:
            self._norm = list(target)
            self._norm_ready = True
        else:
            # Frame-rate independent exponential smoothing.
            alpha = 1.0 - pow(max(0.0, min(0.99, self.smoothing)), max(dt, 1e-4) * 60.0)
            for i in range(2):
                self._norm[i] += (target[i] - self._norm[i]) * alpha

        for i in range(NUM_BUTTONS):
            now = bool(self._raw.buttons[i])
            self._pressed[i] = now and not self._prev_buttons[i]
            self._released[i] = (not now) and self._prev_buttons[i]
            self._prev_buttons[i] = now

    def _poll(self, dt: float, events) -> Optional[RawState]:  # pragma: no cover - abstract
        raise NotImplementedError

    def close(self) -> None:
        """Release any hardware resources."""

    # -------------------------------------------------------------- helpers

    @property
    def connected(self) -> bool:
        return True

    @property
    def pot1_raw(self) -> int:
        return self._raw.pot1

    @property
    def pot2_raw(self) -> int:
        return self._raw.pot2

    @property
    def pot1(self) -> float:
        return self._norm[0]

    @property
    def pot2(self) -> float:
        return self._norm[1]

    def pot(self, index: int) -> float:
        return self._norm[0] if index == 1 else self._norm[1]

    def pot_raw(self, index: int) -> int:
        return self._raw.pot1 if index == 1 else self._raw.pot2

    def button(self, index: int) -> bool:
        """``index`` is 1-based."""
        return bool(self._raw.buttons[index - 1])

    def button_pressed(self, index: int) -> bool:
        return self._pressed[index - 1]

    def button_released(self, index: int) -> bool:
        return self._released[index - 1]

    def any_pressed(self) -> bool:
        return any(self._pressed)

    @property
    def buttons(self) -> List[bool]:
        return list(self._raw.buttons)

    def reset_edges(self) -> None:
        """Swallow pending edges (used when switching scenes)."""
        self._pressed = [False] * NUM_BUTTONS
        self._released = [False] * NUM_BUTTONS
        self._prev_buttons = list(self._raw.buttons)


def _make_button_properties():
    for i in range(1, NUM_BUTTONS + 1):
        setattr(Controller, f"button{i}", property(lambda self, i=i: self.button(i)))
        setattr(Controller, f"button{i}_pressed", property(lambda self, i=i: self.button_pressed(i)))
        setattr(Controller, f"button{i}_released", property(lambda self, i=i: self.button_released(i)))


_make_button_properties()


def parse_packet(line) -> Optional[RawState]:
    """Parse one ``POT1,POT2,B1,B2,B3,B4`` packet.

    Returns ``None`` for anything malformed - garbage during an Arduino reset,
    partial lines, wrong field counts, out-of-range values.  Never raises.
    """
    if isinstance(line, (bytes, bytearray)):
        try:
            line = line.decode("ascii", errors="ignore")
        except Exception:
            return None
    if not isinstance(line, str):
        return None
    line = line.strip().strip("\x00")
    if not line:
        return None
    parts = line.split(",")
    if len(parts) != 6:
        return None
    values = []
    for part in parts:
        part = part.strip()
        if not part or not part.lstrip("-").isdigit():
            return None
        values.append(int(part))
    pot1, pot2 = values[0], values[1]
    if not (0 <= pot1 <= POT_MAX) or not (0 <= pot2 <= POT_MAX):
        return None
    buttons = []
    for value in values[2:]:
        if value not in (0, 1):
            return None
        buttons.append(bool(value))
    return RawState(pot1, pot2, buttons)
