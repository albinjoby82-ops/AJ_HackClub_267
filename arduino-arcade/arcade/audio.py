"""Procedural arcade sound.

All effects are synthesised with the standard library at first run and cached
as WAV files under ``assets/sounds`` - the repo stays self-contained and no
copyrighted audio is involved.

If the machine has no audio device (common on CI and locked-down laptops)
every call here degrades to a silent no-op instead of raising.
"""

from __future__ import annotations

import array
import math
import os
import random
import wave
from typing import Callable, Dict, List

import pygame

SAMPLE_RATE = 22050
ASSET_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "sounds")


# --------------------------------------------------------------- synthesis

def _envelope(i: int, total: int, attack: float = 0.01, release: float = 0.4) -> float:
    t = i / max(1, total)
    a = max(1e-4, attack)
    if t < a:
        return t / a
    r = max(1e-4, release)
    tail = (1.0 - t) / r
    return max(0.0, min(1.0, tail))


def _tone(freq_start: float, freq_end: float, duration: float, wave_kind: str = "square", volume: float = 0.5,
          attack: float = 0.01, release: float = 0.5, noise: float = 0.0) -> List[float]:
    total = int(SAMPLE_RATE * duration)
    samples = []
    phase = 0.0
    for i in range(total):
        t = i / max(1, total)
        freq = freq_start + (freq_end - freq_start) * t
        phase += freq / SAMPLE_RATE
        cycle = phase % 1.0
        if wave_kind == "square":
            value = 1.0 if cycle < 0.5 else -1.0
        elif wave_kind == "saw":
            value = 2.0 * cycle - 1.0
        elif wave_kind == "tri":
            value = 4.0 * abs(cycle - 0.5) - 1.0
        elif wave_kind == "noise":
            value = random.uniform(-1.0, 1.0)
        else:
            value = math.sin(cycle * math.tau)
        if noise:
            value = value * (1.0 - noise) + random.uniform(-1.0, 1.0) * noise
        samples.append(value * volume * _envelope(i, total, attack, release))
    return samples


def _mix(*layers: List[float]) -> List[float]:
    length = max((len(layer) for layer in layers), default=0)
    out = [0.0] * length
    for layer in layers:
        for i, value in enumerate(layer):
            out[i] += value
    return out


def _write_wav(path: str, samples: List[float]) -> None:
    data = array.array("h")
    for value in samples:
        data.append(int(max(-1.0, min(1.0, value)) * 32000))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with wave.open(path, "wb") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(SAMPLE_RATE)
        handle.writeframes(data.tobytes())


# ---------------------------------------------------------------- recipes

RECIPES: Dict[str, Callable[[], List[float]]] = {
    "menu_move": lambda: _tone(520, 700, 0.07, "square", 0.28, release=0.6),
    "menu_select": lambda: _mix(_tone(440, 900, 0.16, "square", 0.32), _tone(880, 1320, 0.12, "sine", 0.18)),
    "back": lambda: _tone(600, 300, 0.12, "square", 0.26),
    "shoot": lambda: _mix(_tone(900, 260, 0.11, "saw", 0.3), _tone(1600, 400, 0.06, "sine", 0.14)),
    "missile": lambda: _mix(_tone(200, 700, 0.32, "saw", 0.3, release=0.7), _tone(90, 240, 0.32, "tri", 0.22)),
    "hit": lambda: _mix(_tone(300, 90, 0.14, "square", 0.3), _tone(0, 0, 0.14, "noise", 0.18)),
    "explosion": lambda: _mix(_tone(160, 40, 0.55, "noise", 0.42, release=0.8), _tone(120, 30, 0.5, "saw", 0.22)),
    "boost": lambda: _mix(_tone(240, 900, 0.34, "saw", 0.28), _tone(0, 0, 0.3, "noise", 0.1)),
    "collision": lambda: _mix(_tone(220, 60, 0.32, "square", 0.38), _tone(0, 0, 0.28, "noise", 0.22)),
    "score": lambda: _mix(_tone(880, 1200, 0.12, "sine", 0.24), _tone(1320, 1760, 0.1, "sine", 0.16)),
    "combo": lambda: _tone(700, 1500, 0.18, "square", 0.24),
    "powerup": lambda: _mix(_tone(500, 1000, 0.22, "square", 0.26), _tone(750, 1500, 0.2, "sine", 0.16)),
    "warning": lambda: _mix(_tone(700, 700, 0.22, "square", 0.26, release=0.3), _tone(520, 520, 0.22, "square", 0.16)),
    "alarm": lambda: _mix(_tone(880, 440, 0.4, "square", 0.3, release=0.4), _tone(220, 220, 0.4, "tri", 0.14)),
    "success": lambda: _mix(_tone(600, 900, 0.14, "sine", 0.26), _tone(900, 1350, 0.16, "sine", 0.2)),
    "fail": lambda: _tone(320, 90, 0.3, "saw", 0.3),
    "game_over": lambda: _mix(_tone(440, 110, 0.8, "saw", 0.3, release=0.7), _tone(220, 55, 0.8, "square", 0.18)),
    "bounce": lambda: _tone(520, 780, 0.07, "square", 0.3),
    "serve": lambda: _tone(300, 800, 0.2, "sine", 0.26),
    "shield": lambda: _mix(_tone(200, 520, 0.24, "sine", 0.24), _tone(400, 900, 0.2, "tri", 0.14)),
    "emp": lambda: _mix(_tone(1200, 120, 0.45, "saw", 0.3), _tone(0, 0, 0.4, "noise", 0.16)),
    "tick": lambda: _tone(1200, 1200, 0.04, "square", 0.2, release=0.8),
}


def generate_assets(force: bool = False) -> List[str]:
    """Write any missing WAV files.  Returns the paths that were created."""
    created = []
    random.seed(1337)  # deterministic noise so assets do not churn in git
    for name, recipe in RECIPES.items():
        path = os.path.join(ASSET_DIR, f"{name}.wav")
        if force or not os.path.exists(path):
            try:
                _write_wav(path, recipe())
                created.append(path)
            except OSError:
                pass
    return created


# -------------------------------------------------------------- the mixer

class Audio:
    """Thin wrapper over ``pygame.mixer`` that is safe when audio is missing."""

    def __init__(self, volume: float = 0.7, muted: bool = False):
        self.available = False
        self.error = ""
        self.volume = max(0.0, min(1.0, volume))
        self.muted = bool(muted)
        self._sounds: Dict[str, pygame.mixer.Sound] = {}
        try:
            pygame.mixer.pre_init(SAMPLE_RATE, -16, 1, 512)
            pygame.mixer.init()
            self.available = True
        except Exception as exc:
            self.error = f"{exc.__class__.__name__}: {exc}"
            return
        generate_assets()
        self._load()

    def _load(self) -> None:
        for name in RECIPES:
            path = os.path.join(ASSET_DIR, f"{name}.wav")
            try:
                self._sounds[name] = pygame.mixer.Sound(path)
            except Exception:
                continue
        self._apply_volume()

    def _apply_volume(self) -> None:
        level = 0.0 if self.muted else self.volume
        for sound in self._sounds.values():
            try:
                sound.set_volume(level)
            except Exception:
                pass

    def set_volume(self, volume: float) -> None:
        self.volume = max(0.0, min(1.0, volume))
        self._apply_volume()

    def set_muted(self, muted: bool) -> None:
        self.muted = bool(muted)
        self._apply_volume()

    def toggle_mute(self) -> bool:
        self.set_muted(not self.muted)
        return self.muted

    def play(self, name: str, volume_scale: float = 1.0) -> None:
        if not self.available or self.muted:
            return
        sound = self._sounds.get(name)
        if sound is None:
            return
        try:
            sound.set_volume(max(0.0, min(1.0, self.volume * volume_scale)))
            sound.play()
        except Exception:
            pass

    def stop_all(self) -> None:
        if self.available:
            try:
                pygame.mixer.stop()
            except Exception:
                pass


class NullAudio(Audio):
    """Explicitly silent audio - used by headless tests."""

    def __init__(self):  # noqa: D107 - deliberately skips Audio.__init__
        self.available = False
        self.error = "disabled"
        self.volume = 0.0
        self.muted = True
        self._sounds = {}
