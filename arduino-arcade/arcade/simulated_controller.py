"""Scripted controller used by smoke tests and the attract-mode demo.

Nothing here touches pygame or serial, so tests can drive whole games headless.
"""

from __future__ import annotations

import math
from typing import Callable, List, Optional

from .controller import POT_MAX, Controller, RawState


class SimulatedController(Controller):
    """A controller driven by code instead of hardware.

    Two ways to drive it:

    * imperatively - :meth:`set_pot`, :meth:`press`, :meth:`release`
    * declaratively - :meth:`sweep`, :meth:`tap`, :meth:`wait` queue timed
      actions that play back as :meth:`update` is called.
    """

    kind = "simulated"

    def __init__(self, calibration=None, smoothing: float = 0.0):
        super().__init__(calibration, smoothing=smoothing)
        self._raw = RawState(POT_MAX // 2, POT_MAX // 2, [False] * 4)
        self._script: List[tuple] = []  # (end_time, callable(t01) -> None)
        self._time = 0.0
        self._script_time = 0.0

    # ------------------------------------------------------- imperative API

    def set_pot(self, index: int, value: float) -> None:
        """``value`` is normalised 0..1."""
        raw = int(max(0.0, min(1.0, value)) * POT_MAX)
        if index == 1:
            self._raw.pot1 = raw
        else:
            self._raw.pot2 = raw

    def set_pot_raw(self, index: int, raw: int) -> None:
        raw = max(0, min(POT_MAX, int(raw)))
        if index == 1:
            self._raw.pot1 = raw
        else:
            self._raw.pot2 = raw

    def press(self, index: int) -> None:
        self._raw.buttons[index - 1] = True

    def release(self, index: int) -> None:
        self._raw.buttons[index - 1] = False

    def release_all(self) -> None:
        self._raw.buttons = [False] * 4

    def feed_packet(self, line: str) -> bool:
        """Inject a raw serial line, exactly as the Arduino would send it."""
        from .controller import parse_packet

        state = parse_packet(line)
        if state is None:
            return False
        self._raw = state
        return True

    # ------------------------------------------------------ declarative API

    def _queue(self, duration: float, action: Callable[[float], None]) -> "SimulatedController":
        self._script.append((self._script_time, self._script_time + duration, action))
        self._script_time += duration
        return self

    def wait(self, duration: float) -> "SimulatedController":
        return self._queue(duration, lambda t: None)

    def sweep(self, index: int, start: float, end: float, duration: float) -> "SimulatedController":
        return self._queue(duration, lambda t: self.set_pot(index, start + (end - start) * t))

    def wiggle(self, index: int, duration: float, cycles: float = 2.0) -> "SimulatedController":
        return self._queue(
            duration,
            lambda t: self.set_pot(index, 0.5 + 0.45 * math.sin(t * cycles * math.tau)),
        )

    def tap(self, index: int, hold: float = 0.08, gap: float = 0.08) -> "SimulatedController":
        self._queue(hold, lambda t: self.press(index))
        return self._queue(gap, lambda t: self.release(index))

    def hold(self, index: int, duration: float) -> "SimulatedController":
        self._queue(duration, lambda t: self.press(index))
        return self._queue(0.05, lambda t: self.release(index))

    @property
    def script_finished(self) -> bool:
        return not self._script or self._time >= self._script[-1][1]

    # -------------------------------------------------------------- polling

    def _poll(self, dt: float, events) -> Optional[RawState]:
        self._time += dt
        for start, end, action in self._script:
            if start <= self._time < end or (end == start and abs(self._time - start) < 1e-9):
                span = max(1e-6, end - start)
                action(max(0.0, min(1.0, (self._time - start) / span)))
        return self._raw.copy()

    @property
    def status_text(self) -> str:
        return "Simulated controller"
