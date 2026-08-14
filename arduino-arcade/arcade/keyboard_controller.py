"""Keyboard backend - lets the whole arcade run with no hardware attached.

Analog axes ramp instead of snapping so keyboard play still feels like turning
a knob (and so keyboard testing exercises the same smoothing code path).
"""

from __future__ import annotations

from typing import Optional

import pygame

from .controller import POT_MAX, Controller, RawState

#: Full-scale sweep time in seconds when a direction key is held.
RAMP_TIME = 0.9
#: How fast an un-driven axis returns to centre (0 = stays put).
RETURN_RATE = 0.0


class KeyboardController(Controller):
    kind = "keyboard"

    #: (decrease keys, increase keys) for pot 1 and pot 2.
    AXIS_KEYS = (
        ((pygame.K_a, pygame.K_s), (pygame.K_d, pygame.K_w)),
        ((pygame.K_LEFT, pygame.K_DOWN), (pygame.K_RIGHT, pygame.K_UP)),
    )
    BUTTON_KEYS = (
        (pygame.K_1, pygame.K_KP1, pygame.K_SPACE),
        (pygame.K_2, pygame.K_KP2, pygame.K_LSHIFT),
        (pygame.K_3, pygame.K_KP3),
        (pygame.K_4, pygame.K_KP4),
    )

    def __init__(self, calibration=None):
        # Keyboard axes are already clean and always cover the full range, so
        # the saved pot calibration is deliberately ignored here.
        super().__init__(None, smoothing=0.15)
        self.axes = [0.5, 0.5]

    def _poll(self, dt: float, events) -> Optional[RawState]:
        try:
            keys = pygame.key.get_pressed()
        except pygame.error:  # display not initialised yet
            return None

        for i, (down_keys, up_keys) in enumerate(self.AXIS_KEYS):
            direction = 0.0
            if any(keys[k] for k in down_keys):
                direction -= 1.0
            if any(keys[k] for k in up_keys):
                direction += 1.0
            if direction:
                self.axes[i] += direction * dt / RAMP_TIME
            elif RETURN_RATE:
                self.axes[i] += (0.5 - self.axes[i]) * min(1.0, RETURN_RATE * dt)
            self.axes[i] = max(0.0, min(1.0, self.axes[i]))

        buttons = [any(keys[k] for k in group) for group in self.BUTTON_KEYS]
        return RawState(
            int(self.axes[0] * POT_MAX),
            int(self.axes[1] * POT_MAX),
            buttons,
        )

    @property
    def status_text(self) -> str:
        return "Keyboard mode (A/D + Left/Right, keys 1-4)"


#: Shown on the keyboard-mode help panels.
KEYBOARD_HINTS = [
    ("POT 1", "A / D"),
    ("POT 2", "LEFT / RIGHT"),
    ("BUTTON 1", "1  or SPACE"),
    ("BUTTON 2", "2  or SHIFT"),
    ("BUTTON 3", "3"),
    ("BUTTON 4", "4"),
]
