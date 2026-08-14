"""HOW TO PLAY - wiring, controls per game and keyboard fallback, on one screen."""

from __future__ import annotations

import pygame

from .. import ui
from ..keyboard_controller import KEYBOARD_HINTS
from ..scene import Scene

PAGES = [
    (
        "WIRE IT UP",
        [
            ("D2 / D3 / D4 / D5", "buttons 1-4, other leg to GND"),
            ("A0 / A1", "pot 1 / pot 2 wiper (centre pin)"),
            ("5V and GND", "pot outer pins and breadboard rails"),
            ("USB", "Arduino stays plugged into the laptop"),
            ("NO RESISTORS", "buttons use INPUT_PULLUP"),
        ],
    ),
    (
        "NEON DRIFT",
        [
            ("POT 1", "steer"),
            ("POT 2", "throttle"),
            ("B1 / B2", "boost / drift"),
            ("B3 / B4", "power-up / recentre"),
            ("GOAL", "chase near-miss combos, avoid 3 crashes"),
        ],
    ),
    (
        "ORBITAL DEFENDER",
        [
            ("POT 1", "orbit around the station"),
            ("POT 2", "aim the gun"),
            ("B1 / B2", "fire / shield"),
            ("B3 / B4", "missile / EMP"),
            ("GOAL", "survive the waves, protect the hull"),
        ],
    ),
    (
        "REACTOR SYNC",
        [
            ("POT 1 / POT 2", "hold both channels in their safe zones"),
            ("B1 / B3", "lock channel A / B"),
            ("B2 / B4", "vent coolant / discharge core"),
            ("ALARMS", "hit the button the alarm names, fast"),
            ("GOAL", "keep stability above zero"),
        ],
    ),
    (
        "TWIN PONG",
        [
            ("P1", "POT 1 paddle, B1 blast, B2 serve"),
            ("P2", "POT 2 paddle, B3 blast, B4 serve"),
            ("PICKUPS", "hit the hexagons with the ball"),
            ("GOAL", "first to 7 points wins"),
            ("TIP", "grab the board and fight for it"),
        ],
    ),
]


class HowToPlay(Scene):
    name = "how_to_play"

    def __init__(self, app):
        super().__init__(app)
        self.page = 0
        self.time = 0.0
        self._cooldown = 0.0

    @property
    def state_name(self) -> str:
        return f"page{self.page}"

    def handle_event(self, event) -> None:
        if event.type != pygame.KEYDOWN:
            return
        if event.key in (pygame.K_ESCAPE,):
            self._back()
        elif event.key in (pygame.K_RIGHT, pygame.K_d, pygame.K_SPACE, pygame.K_RETURN):
            self._turn(1)
        elif event.key in (pygame.K_LEFT, pygame.K_a):
            self._turn(-1)

    def _turn(self, delta: int) -> None:
        self.page = (self.page + delta) % len(PAGES)
        self.app.audio.play("menu_move")

    def _back(self) -> None:
        self.app.audio.play("back")
        self.app.pop_scene()

    def update(self, dt: float, controller) -> None:
        self.time += dt
        self._cooldown = max(0.0, self._cooldown - dt)
        if self._cooldown <= 0.0:
            target = max(0, min(len(PAGES) - 1, int(controller.pot1 * (len(PAGES) - 0.001))))
            if target != self.page:
                self.page = target
                self.app.audio.play("menu_move")
                self._cooldown = 0.18
        if controller.button_pressed(1):
            self._turn(1)
        elif controller.button_pressed(2):
            self._back()

    def draw(self, surface: pygame.Surface) -> None:
        width, height = surface.get_size()
        ui.draw_grid_background(surface, self.time * 8)
        title, rows = PAGES[self.page]
        ui.draw_text(surface, "HOW TO PLAY", (width // 2, 34), 34, ui.AMBER, align="midtop", bold=True)
        ui.draw_text(surface, title, (width // 2, 80), 46, ui.CYAN, align="midtop", bold=True, glow=0.7)

        panel = pygame.Rect(int(width * 0.12), int(height * 0.24), int(width * 0.76), int(height * 0.5))
        ui.draw_panel(surface, panel, border=ui.CYAN, alpha=200)
        row_h = panel.height / max(1, len(rows))
        for i, (label, value) in enumerate(rows):
            y = panel.y + row_h * (i + 0.5)
            ui.draw_text(surface, label, (panel.x + 28, y), 24, ui.AMBER, align="midleft", bold=True)
            ui.draw_text(surface, value, (panel.right - 28, y), 22, ui.TEXT, align="midright")

        for i in range(len(PAGES)):
            colour = ui.CYAN if i == self.page else (52, 56, 86)
            pygame.draw.circle(surface, colour, (width // 2 - (len(PAGES) - 1) * 12 + i * 24,
                                                 int(height * 0.79)), 7)

        if self.app.controller.kind == "keyboard":
            keys = "   ".join(f"{label}: {keys}" for label, keys in KEYBOARD_HINTS[:2])
            ui.draw_text(surface, f"KEYBOARD  {keys}   buttons 1-4", (width // 2, height - 74), 18,
                         ui.TEXT_DIM, align="center")
        ui.draw_text(surface, "POT 1 or ARROWS to browse   B1 next   B2 / ESC back",
                     (width // 2, height - 44), 19, ui.TEXT_DIM, align="center")
