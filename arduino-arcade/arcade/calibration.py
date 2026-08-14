"""Potentiometer calibration: normalisation, dead zones, inversion."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict

POT_MAX = 1023
#: Minimum usable travel.  Anything narrower is treated as an un-calibrated pot
#: so a stuck/miswired knob can never produce wild full-scale jumps.
MIN_SPAN = 60


@dataclass
class PotCalibration:
    low: int = 0
    high: int = POT_MAX
    invert: bool = False
    #: Fraction of travel ignored at each end so cheap pots can still reach
    #: a solid 0.0 and 1.0.
    dead_zone: float = 0.03

    def to_dict(self) -> dict:
        return {
            "low": int(self.low),
            "high": int(self.high),
            "invert": bool(self.invert),
            "dead_zone": float(self.dead_zone),
        }

    @classmethod
    def from_dict(cls, data) -> "PotCalibration":
        pot = cls()
        if isinstance(data, dict):
            try:
                pot.low = int(data.get("low", 0))
                pot.high = int(data.get("high", POT_MAX))
                pot.invert = bool(data.get("invert", False))
                pot.dead_zone = float(data.get("dead_zone", 0.03))
            except (TypeError, ValueError):
                return cls()
        pot.sanitize()
        return pot

    def sanitize(self) -> None:
        self.low = max(0, min(POT_MAX, self.low))
        self.high = max(0, min(POT_MAX, self.high))
        if self.high - self.low < MIN_SPAN:
            self.low, self.high = 0, POT_MAX
        self.dead_zone = max(0.0, min(0.25, self.dead_zone))

    def normalize(self, raw: float) -> float:
        span = self.high - self.low
        if span < MIN_SPAN:
            span = POT_MAX
            low = 0
        else:
            low = self.low
        value = (raw - low) / float(span)
        dz = self.dead_zone
        if dz > 0.0:
            value = (value - dz) / max(1e-6, 1.0 - 2.0 * dz)
        value = max(0.0, min(1.0, value))
        if self.invert:
            value = 1.0 - value
        return value


@dataclass
class Calibration:
    """Calibration for both pots, plus (de)serialisation."""

    pot1: PotCalibration = field(default_factory=PotCalibration)
    pot2: PotCalibration = field(default_factory=PotCalibration)
    calibrated: bool = False

    def get(self, index: int) -> PotCalibration:
        return self.pot1 if index == 1 else self.pot2

    def normalize(self, index: int, raw: float) -> float:
        return self.get(index).normalize(raw)

    def to_dict(self) -> Dict:
        return {
            "pot1": self.pot1.to_dict(),
            "pot2": self.pot2.to_dict(),
            "calibrated": bool(self.calibrated),
        }

    @classmethod
    def from_dict(cls, data) -> "Calibration":
        if not isinstance(data, dict):
            return cls()
        return cls(
            pot1=PotCalibration.from_dict(data.get("pot1")),
            pot2=PotCalibration.from_dict(data.get("pot2")),
            calibrated=bool(data.get("calibrated", False)),
        )


class CalibrationRecorder:
    """Accumulates observed extremes while the player sweeps both knobs."""

    def __init__(self, required_span: int = 300):
        self.required_span = required_span
        self.low = [POT_MAX, POT_MAX]
        self.high = [0, 0]
        self.samples = 0

    def feed(self, pot1_raw: int, pot2_raw: int) -> None:
        for i, raw in enumerate((pot1_raw, pot2_raw)):
            raw = max(0, min(POT_MAX, int(raw)))
            self.low[i] = min(self.low[i], raw)
            self.high[i] = max(self.high[i], raw)
        self.samples += 1

    def span(self, index: int) -> int:
        return max(0, self.high[index - 1] - self.low[index - 1])

    def progress(self, index: int) -> float:
        return max(0.0, min(1.0, self.span(index) / float(self.required_span)))

    @property
    def complete(self) -> bool:
        return self.samples > 10 and all(self.progress(i) >= 1.0 for i in (1, 2))

    def build(self, invert1: bool = False, invert2: bool = False) -> Calibration:
        cal = Calibration(calibrated=True)
        for index, (pot, invert) in enumerate(((cal.pot1, invert1), (cal.pot2, invert2)), start=1):
            # Nudge inwards slightly: real pots rarely repeat their exact
            # extremes, so this guarantees the ends are reachable.
            margin = max(2, int(self.span(index) * 0.02))
            pot.low = self.low[index - 1] + margin
            pot.high = self.high[index - 1] - margin
            pot.invert = invert
            pot.sanitize()
        return cal
