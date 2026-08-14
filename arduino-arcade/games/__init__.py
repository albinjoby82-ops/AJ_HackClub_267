"""The four arcade games, exposed through a single registry."""

from __future__ import annotations

from typing import Dict, Type

from arcade.game import BaseGame

from .neon_drift import NeonDrift
from .orbital_defender import OrbitalDefender
from .reactor_sync import ReactorSync
from .twin_pong import TwinPong

GAMES: Dict[str, Type[BaseGame]] = {
    "neon_drift": NeonDrift,
    "orbital_defender": OrbitalDefender,
    "reactor_sync": ReactorSync,
    "twin_pong": TwinPong,
}

__all__ = ["GAMES", "NeonDrift", "OrbitalDefender", "ReactorSync", "TwinPong"]
