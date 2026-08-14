"""CONTROLLER TEST - live view of all six inputs plus the expected wiring.

This is the screen to open first at a workshop: it makes a mis-wired button or
a dead potentiometer obvious in seconds.
"""

from __future__ import annotations

import pygame

from .. import ui
from ..keyboard_controller import KEYBOARD_HINTS
from ..scene import Scene
from .widgets import controller_status_line

WIRING_LINES = [
    "D2 -> Button 1 -> GND",
    "D3 -> Button 2 -> GND",
    "D4 -> Button 3 -> GND",
    "D5 -> Button 4 -> GND",
    "",
    "A0 -> Pot 1 wiper",
    "A1 -> Pot 2 wiper",
    "Pot outer pins -> 5V and GND",
]


class ControllerTest(Scene):
    name = "controller_test"

    def __init__(self, app):
        super().__init__(app)
        self.time = 0.0
        self.press_counts = [0, 0, 0, 0]
        self.seen_low = [1023, 1023]
        self.seen_high = [0, 0]

    def handle_event(self, event) -> None:
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_SPACE):
            self.app.audio.play("back")
            self.app.pop_scene()

    def update(self, dt: float, controller) -> None:
        self.time += dt
        for i in range(4):
            if controller.button_pressed(i + 1):
                self.press_counts[i] += 1
                self.app.audio.play("tick", 0.5)
        for i, raw in enumerate((controller.pot1_raw, controller.pot2_raw)):
            self.seen_low[i] = min(self.seen_low[i], raw)
            self.seen_high[i] = max(self.seen_high[i], raw)
        if controller.button_pressed(2) and controller.button(1):
            self.app.pop_scene()

    def draw(self, surface: pygame.Surface) -> None:
        width, height = surface.get_size()
        ui.draw_grid_background(surface, self.time * 12)
        controller = self.app.controller

        ui.draw_text(surface, "CONTROLLER TEST", (width // 2, 28), 40, ui.CYAN,
                     align="midtop", bold=True, glow=0.6)
        text, colour = controller_status_line(self.app)
        ui.draw_text(surface, text, (width // 2, 78), 20, colour, align="midtop", bold=True)

        left = pygame.Rect(int(width * 0.05), 118, int(width * 0.52), int(height * 0.62))
        ui.draw_panel(surface, left, border=ui.CYAN, alpha=205)

        y = left.y + 26
        for index, colour_ in ((1, ui.CYAN), (2, ui.MAGENTA)):
            value = controller.pot(index)
            raw = controller.pot_raw(index)
            ui.draw_text(surface, f"POT {index}", (left.x + 24, y), 26, colour_, bold=True)
            ui.draw_text(surface, f"{ui.ascii_bar(value)} {raw:4d}", (left.x + 130, y), 26, ui.TEXT)
            bar = pygame.Rect(left.x + 24, y + 34, left.width - 48, 22)
            ui.draw_bar(surface, bar, value, colour_)
            ui.draw_text(surface,
                         f"normalised {value:.3f}   observed {self.seen_low[index - 1]}-{self.seen_high[index - 1]}",
                         (left.x + 24, y + 62), 17, ui.TEXT_DIM)
            y += 108

        y += 4
        for i in range(4):
            pressed = controller.button(i + 1)
            marker = "●" if pressed else "○"
            colour_ = ui.LIME if pressed else ui.TEXT_DIM
            ui.draw_text(surface, f"BUTTON {i + 1}   {marker}", (left.x + 24, y), 24, colour_, bold=pressed)
            pygame.draw.circle(surface, colour_ if pressed else (44, 48, 74),
                               (left.x + 250, y + 11), 12)
            ui.draw_text(surface, f"presses {self.press_counts[i]}", (left.x + 290, y + 2), 18, ui.TEXT_DIM)
            y += 36

        right = pygame.Rect(int(width * 0.6), 118, int(width * 0.35), int(height * 0.62))
        ui.draw_panel(surface, right, border=ui.AMBER, alpha=205)
        ui.draw_text(surface, "EXPECTED WIRING", (right.centerx, right.y + 18), 22, ui.AMBER,
                     align="midtop", bold=True)
        y = right.y + 58
        for line in WIRING_LINES:
            ui.draw_text(surface, line, (right.x + 20, y), 18, ui.TEXT if line else ui.TEXT_DIM)
            y += 26
        y += 8
        ui.draw_text(surface, "Buttons use INPUT_PULLUP:", (right.x + 20, y), 16, ui.TEXT_DIM)
        ui.draw_text(surface, "pressed = LOW, no resistors needed.", (right.x + 20, y + 22), 16, ui.TEXT_DIM)

        if self.app.controller.kind == "keyboard":
            y += 60
            ui.draw_text(surface, "KEYBOARD MAPPING", (right.x + 20, y), 18, ui.AMBER, bold=True)
            for i, (label, keys) in enumerate(KEYBOARD_HINTS):
                ui.draw_text(surface, f"{label:<10} {keys}", (right.x + 20, y + 26 + i * 22), 16, ui.TEXT_DIM)

        ui.draw_text(surface, "ESC or ENTER to go back   (or hold B1 + press B2)",
                     (width // 2, height - 40), 19, ui.TEXT_DIM, align="center")
