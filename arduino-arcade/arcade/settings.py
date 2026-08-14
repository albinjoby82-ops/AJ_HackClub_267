"""Persistent settings, calibration and high scores (single JSON file)."""

from __future__ import annotations

import json
import os
import tempfile
from typing import Any, Dict

from .calibration import Calibration

DEFAULTS: Dict[str, Any] = {
    "volume": 0.7,
    "muted": False,
    "fullscreen": False,
    "preferred_port": "",
    "window_size": [1280, 720],
    "calibration": {},
    "high_scores": {},
}


def default_path() -> str:
    """Per-user settings location, overridable for tests."""
    override = os.environ.get("ARCADE_SETTINGS_PATH")
    if override:
        return override
    base = os.environ.get("APPDATA") or os.path.expanduser("~/.config")
    return os.path.join(base, "ArduinoArcade", "settings.json")


class Settings:
    """Dict-backed settings store that never raises on bad input."""

    def __init__(self, path: str | None = None):
        self.path = path or default_path()
        self.data: Dict[str, Any] = json.loads(json.dumps(DEFAULTS))
        self.load_error = ""
        self.load()

    # ------------------------------------------------------------ load/save

    def load(self) -> None:
        try:
            with open(self.path, "r", encoding="utf-8") as handle:
                data = json.load(handle)
        except FileNotFoundError:
            return
        except (json.JSONDecodeError, OSError, UnicodeDecodeError) as exc:
            # Corrupt or unreadable file: keep defaults, tell the user, and
            # park the damaged file so the next save can succeed.
            self.load_error = f"Settings unreadable ({exc.__class__.__name__}); defaults restored."
            try:
                os.replace(self.path, self.path + ".corrupt")
            except OSError:
                pass
            return
        if not isinstance(data, dict):
            self.load_error = "Settings file was not an object; defaults restored."
            return
        for key, value in data.items():
            if key in DEFAULTS:
                self.data[key] = value
        self._coerce()

    def _coerce(self) -> None:
        """Force every value back into its expected type."""
        try:
            self.data["volume"] = max(0.0, min(1.0, float(self.data.get("volume", 0.7))))
        except (TypeError, ValueError):
            self.data["volume"] = DEFAULTS["volume"]
        self.data["muted"] = bool(self.data.get("muted", False))
        self.data["fullscreen"] = bool(self.data.get("fullscreen", False))
        port = self.data.get("preferred_port", "")
        self.data["preferred_port"] = port if isinstance(port, str) else ""
        size = self.data.get("window_size")
        if (
            not isinstance(size, (list, tuple))
            or len(size) != 2
            or not all(isinstance(v, int) and v >= 480 for v in size)
        ):
            self.data["window_size"] = list(DEFAULTS["window_size"])
        else:
            self.data["window_size"] = [int(size[0]), int(size[1])]
        if not isinstance(self.data.get("calibration"), dict):
            self.data["calibration"] = {}
        scores = self.data.get("high_scores")
        if not isinstance(scores, dict):
            self.data["high_scores"] = {}
        else:
            self.data["high_scores"] = {
                str(k): int(v) for k, v in scores.items() if isinstance(v, (int, float))
            }

    def save(self) -> bool:
        """Atomic write; returns False instead of raising if it fails."""
        try:
            directory = os.path.dirname(self.path)
            if directory:
                os.makedirs(directory, exist_ok=True)
            fd, tmp = tempfile.mkstemp(dir=directory or ".", suffix=".tmp")
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                json.dump(self.data, handle, indent=2)
            os.replace(tmp, self.path)
            return True
        except OSError:
            return False

    # ------------------------------------------------------------ accessors

    def get(self, key: str, default: Any = None) -> Any:
        return self.data.get(key, DEFAULTS.get(key, default))

    def set(self, key: str, value: Any) -> None:
        self.data[key] = value
        self._coerce()
        self.save()

    @property
    def calibration(self) -> Calibration:
        return Calibration.from_dict(self.data.get("calibration"))

    @calibration.setter
    def calibration(self, cal: Calibration) -> None:
        self.data["calibration"] = cal.to_dict()
        self.save()

    def high_score(self, game_id: str) -> int:
        try:
            return int(self.data["high_scores"].get(game_id, 0))
        except (KeyError, TypeError, ValueError):
            return 0

    def submit_score(self, game_id: str, score: int) -> bool:
        """Store ``score`` if it beats the record.  Returns True if it did."""
        score = int(score)
        if score <= self.high_score(game_id):
            return False
        self.data.setdefault("high_scores", {})[game_id] = score
        self.save()
        return True
