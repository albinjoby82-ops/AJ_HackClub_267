"""Settings: volume, mute, fullscreen, controller source, recalibration."""

from __future__ import annotations

import pygame

from .. import ui
from ..scene import Scene
from .widgets import controller_status_line


class SettingsScene(Scene):
    name = "settings"

    def __init__(self, app, on_recalibrate, on_choose_device):
        super().__init__(app)
        self.on_recalibrate = on_recalibrate
        self.on_choose_device = on_choose_device
        self.index = 0
        self.time = 0.0
        self._cooldown = 0.0
        self.rects: list[pygame.Rect] = []

    @property
    def items(self):
        settings = self.app.settings
        volume = int(settings.get("volume", 0.7) * 100)
        return [
            (f"VOLUME  {volume}%", "volume"),
            (f"AUDIO  {'MUTED' if self.app.audio.muted else 'ON'}", "mute"),
            (f"FULLSCREEN  {'ON' if settings.get('fullscreen') else 'OFF'}", "fullscreen"),
            ("RECALIBRATE POTENTIOMETERS", "calibrate"),
            ("SELECT ARDUINO / CONTROLLER", "device"),
            ("RESET HIGH SCORES", "reset"),
            ("BACK", "back"),
        ]

    def handle_event(self, event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self._move(-1)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self._move(1)
            elif event.key in (pygame.K_LEFT, pygame.K_a):
                self._adjust(-1)
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                self._adjust(1)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self._activate()
            elif event.key == pygame.K_ESCAPE:
                self._back()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, rect in enumerate(self.rects):
                if rect.collidepoint(event.pos):
                    self.index = i
                    self._activate()
        elif event.type == pygame.MOUSEMOTION:
            for i, rect in enumerate(self.rects):
                if rect.collidepoint(event.pos) and i != self.index:
                    self.index = i

    def _move(self, delta: int) -> None:
        self.index = (self.index + delta) % len(self.items)
        self.app.audio.play("menu_move")

    def _back(self) -> None:
        self.app.audio.play("back")
        self.app.pop_scene()

    def _adjust(self, delta: int) -> None:
        key = self.items[self.index][1]
        if key == "volume":
            volume = round(min(1.0, max(0.0, self.app.settings.get("volume", 0.7) + delta * 0.1)), 2)
            self.app.settings.set("volume", volume)
            self.app.audio.set_volume(volume)
            self.app.audio.play("menu_move")
        else:
            self._activate()

    def _activate(self) -> None:
        key = self.items[self.index][1]
        audio = self.app.audio
        if key == "volume":
            self._adjust(1)
            return
        audio.play("menu_select")
        if key == "mute":
            self.app.settings.set("muted", audio.toggle_mute())
        elif key == "fullscreen":
            self.app.toggle_fullscreen()
        elif key == "calibrate":
            self.on_recalibrate()
        elif key == "device":
            self.on_choose_device()
        elif key == "reset":
            self.app.settings.data["high_scores"] = {}
            self.app.settings.save()
            self.app.toast("HIGH SCORES CLEARED", color=ui.AMBER)
        else:
            self._back()

    def update(self, dt: float, controller) -> None:
        self.time += dt
        self._cooldown = max(0.0, self._cooldown - dt)
        count = len(self.items)
        if self._cooldown <= 0.0:
            target = max(0, min(count - 1, int(controller.pot1 * (count - 0.001))))
            if target != self.index:
                self.index = target
                self.app.audio.play("menu_move")
                self._cooldown = 0.16
        if controller.button_pressed(1):
            self._activate()
        elif controller.button_pressed(2):
            self._back()
        elif controller.button_pressed(3):
            self._adjust(-1)
        elif controller.button_pressed(4):
            self._adjust(1)

    def draw(self, surface: pygame.Surface) -> None:
        width, height = surface.get_size()
        ui.draw_grid_background(surface, self.time * 8)
        ui.draw_text(surface, "SETTINGS", (width // 2, 44), 44, ui.VIOLET, align="midtop",
                     bold=True, glow=0.6)
        text, colour = controller_status_line(self.app)
        ui.draw_text(surface, text, (width // 2, 96), 19, colour, align="midtop")
        if not self.app.audio.available:
            ui.draw_text(surface, "no audio device detected - running silently",
                         (width // 2, 120), 17, ui.AMBER, align="midtop")

        self.rects = []
        top = int(height * 0.26)
        for i, (label, _key) in enumerate(self.items):
            rect = pygame.Rect(0, 0, int(width * 0.55), 46)
            rect.center = (width // 2, top + i * 56)
            self.rects.append(rect)
            selected = i == self.index
            if selected:
                ui.draw_panel(surface, rect, border=ui.VIOLET, alpha=140)
            ui.draw_text(surface, label, rect.center, 25 if selected else 23,
                         ui.TEXT if selected else ui.TEXT_DIM, align="center", bold=selected)

        ui.draw_text(surface, "POT 1 move   B1 select   B3/B4 adjust   B2 back",
                     (width // 2, height - 44), 19, ui.TEXT_DIM, align="center")
