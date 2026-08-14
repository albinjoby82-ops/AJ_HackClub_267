"""Device selection: pick a serial port, or play without an Arduino."""

from __future__ import annotations

import pygame

from .. import ui
from ..keyboard_controller import KeyboardController
from ..scene import Scene
from ..serial_controller import SERIAL_AVAILABLE, SerialController, list_serial_ports

KEYBOARD_ROW = "PLAY WITHOUT ARDUINO  (keyboard)"
RESCAN_ROW = "RESCAN PORTS"


class DeviceSelect(Scene):
    name = "device_select"

    def __init__(self, app, on_done=None):
        super().__init__(app)
        self.on_done = on_done
        self.index = 0
        self.time = 0.0
        self._cooldown = 0.0
        self.ports = []
        self.rects: list[pygame.Rect] = []
        self.rescan()

    def rescan(self) -> None:
        self.ports = list_serial_ports()
        self.index = 0

    @property
    def rows(self):
        return [f"{p.device}   {p.description[:38]}" for p in self.ports] + [KEYBOARD_ROW, RESCAN_ROW]

    def handle_event(self, event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self._move(-1)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self._move(1)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self._activate()
            elif event.key == pygame.K_ESCAPE:
                self._done()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, rect in enumerate(self.rects):
                if rect.collidepoint(event.pos):
                    self.index = i
                    self._activate()

    def _move(self, delta: int) -> None:
        self.index = (self.index + delta) % len(self.rows)
        self.app.audio.play("menu_move")

    def _done(self) -> None:
        if self.on_done:
            self.on_done()
        else:
            self.app.pop_scene()

    def _activate(self) -> None:
        rows = self.rows
        choice = rows[self.index]
        self.app.audio.play("menu_select")
        if choice == RESCAN_ROW:
            self.rescan()
            return
        if choice == KEYBOARD_ROW:
            self.app.replace_controller(KeyboardController())
            self.app.settings.set("preferred_port", "")
            self.app.toast("KEYBOARD MODE", color=ui.AMBER)
        else:
            port = self.ports[self.index].device
            self.app.replace_controller(SerialController(port, self.app.settings.calibration))
            self.app.settings.set("preferred_port", port)
            self.app.toast(f"CONNECTING TO {port}", color=ui.CYAN)
        self._done()

    def update(self, dt: float, controller) -> None:
        self.time += dt
        self._cooldown = max(0.0, self._cooldown - dt)
        count = len(self.rows)
        if self._cooldown <= 0.0:
            target = max(0, min(count - 1, int(controller.pot1 * (count - 0.001))))
            if target != self.index:
                self.index = target
                self.app.audio.play("menu_move")
                self._cooldown = 0.16
        if controller.button_pressed(1):
            self._activate()
        elif controller.button_pressed(2):
            self._done()

    def draw(self, surface: pygame.Surface) -> None:
        width, height = surface.get_size()
        ui.draw_grid_background(surface, self.time * 8)
        ui.draw_text(surface, "SELECT CONTROLLER", (width // 2, 44), 42, ui.CYAN,
                     align="midtop", bold=True, glow=0.6)
        if not SERIAL_AVAILABLE:
            ui.draw_text(surface, "pyserial not installed - keyboard mode only",
                         (width // 2, 96), 20, ui.AMBER, align="midtop")
        elif not self.ports:
            ui.draw_text(surface, "no serial ports found - plug in the Arduino and rescan",
                         (width // 2, 96), 20, ui.AMBER, align="midtop")
        else:
            ui.draw_text(surface, "likely Arduino devices are listed first",
                         (width // 2, 96), 19, ui.TEXT_DIM, align="midtop")

        self.rects = []
        rows = self.rows
        top = int(height * 0.24)
        for i, label in enumerate(rows):
            rect = pygame.Rect(0, 0, int(width * 0.7), 48)
            rect.center = (width // 2, top + i * 58)
            self.rects.append(rect)
            selected = i == self.index
            likely = i < len(self.ports) and self.ports[i].likely
            accent = ui.LIME if likely else ui.VIOLET
            if selected:
                ui.draw_panel(surface, rect, border=accent, alpha=140)
            ui.draw_text(surface, label, rect.center, 23 if selected else 21,
                         ui.TEXT if selected else ui.TEXT_DIM, align="center", bold=selected)
            if likely:
                ui.draw_text(surface, "LIKELY", (rect.right - 14, rect.centery), 15, ui.LIME,
                             align="midright", bold=True)

        ui.draw_text(surface, "POT 1 move   B1 select   B2 / ESC back",
                     (width // 2, height - 44), 19, ui.TEXT_DIM, align="center")
