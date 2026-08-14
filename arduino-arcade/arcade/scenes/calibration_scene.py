"""Calibration screen: sweep both pots, store the observed range."""

from __future__ import annotations

import pygame

from .. import ui
from ..calibration import CalibrationRecorder
from ..scene import Scene

SWEEP = "sweep"
CONFIRM = "confirm"
DONE = "done"


class CalibrationScene(Scene):
    name = "calibration"

    def __init__(self, app, on_finish=None):
        super().__init__(app)
        self.on_finish = on_finish
        self.recorder = CalibrationRecorder()
        self.stage = SWEEP
        self.time = 0.0
        self.invert = [False, False]
        self.result = None

    @property
    def state_name(self) -> str:
        return self.stage

    def on_enter(self) -> None:
        self.recorder = CalibrationRecorder()
        self.stage = SWEEP
        self.result = None

    def handle_event(self, event) -> None:
        if event.type != pygame.KEYDOWN:
            return
        if event.key == pygame.K_ESCAPE:
            self._finish(save=False)
        elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
            self._advance()
        elif event.key == pygame.K_1:
            self.invert[0] = not self.invert[0]
        elif event.key == pygame.K_2:
            self.invert[1] = not self.invert[1]

    def _advance(self) -> None:
        if self.stage == SWEEP:
            if self.recorder.complete:
                self.stage = CONFIRM
                self.app.audio.play("success")
            else:
                self.app.audio.play("fail", 0.5)
        elif self.stage == CONFIRM:
            self._finish(save=True)

    def _finish(self, save: bool) -> None:
        if save:
            calibration = self.recorder.build(self.invert[0], self.invert[1])
            self.app.settings.calibration = calibration
            self.app.apply_calibration()
            self.app.toast("CALIBRATION SAVED", color=ui.LIME)
            self.app.audio.play("menu_select")
        else:
            self.app.audio.play("back")
        if self.on_finish:
            self.on_finish()
        else:
            self.app.pop_scene()

    def update(self, dt: float, controller) -> None:
        self.time += dt
        if self.stage == SWEEP:
            self.recorder.feed(controller.pot1_raw, controller.pot2_raw)
            if controller.button_pressed(1):
                self._advance()
            if controller.button_pressed(2):
                self._finish(save=False)
        elif self.stage == CONFIRM:
            if controller.button_pressed(1):
                self._finish(save=True)
            elif controller.button_pressed(2):
                self.stage = SWEEP
            elif controller.button_pressed(3):
                self.invert[0] = not self.invert[0]
            elif controller.button_pressed(4):
                self.invert[1] = not self.invert[1]

    def draw(self, surface: pygame.Surface) -> None:
        width, height = surface.get_size()
        ui.draw_grid_background(surface, self.time * 10)
        ui.draw_text(surface, "CONTROLLER CALIBRATION", (width // 2, 40), 40, ui.LIME,
                     align="midtop", bold=True, glow=0.6)

        if self.stage == SWEEP:
            ui.draw_text(surface, "TURN BOTH KNOBS FULLY LEFT, THEN FULLY RIGHT",
                         (width // 2, 100), 24, ui.TEXT, align="midtop", bold=True)
        else:
            ui.draw_text(surface, "CHECK THE DIRECTION, THEN SAVE",
                         (width // 2, 100), 24, ui.TEXT, align="midtop", bold=True)

        controller = self.app.controller
        for index, colour in ((1, ui.CYAN), (2, ui.MAGENTA)):
            top = int(height * (0.24 if index == 1 else 0.5))
            rect = pygame.Rect(int(width * 0.15), top, int(width * 0.7), int(height * 0.2))
            ui.draw_panel(surface, rect, border=colour, alpha=200)
            raw = controller.pot_raw(index)
            low = self.recorder.low[index - 1]
            high = self.recorder.high[index - 1]
            ui.draw_text(surface, f"POT {index}", (rect.x + 22, rect.y + 16), 26, colour, bold=True)
            ui.draw_text(surface, f"raw {raw:4d}", (rect.right - 22, rect.y + 16), 24, ui.TEXT,
                         align="topright")

            # Range bar: the shaded region is what we have observed so far.
            bar = pygame.Rect(rect.x + 22, rect.y + 58, rect.width - 44, 26)
            pygame.draw.rect(surface, (20, 22, 46), bar, border_radius=8)
            if high > low:
                covered = pygame.Rect(int(bar.x + bar.width * low / 1023.0), bar.y,
                                      max(4, int(bar.width * (high - low) / 1023.0)), bar.height)
                pygame.draw.rect(surface, tuple(c // 2 for c in colour), covered, border_radius=8)
            marker = bar.x + bar.width * raw / 1023.0
            pygame.draw.line(surface, ui.WHITE, (marker, bar.y - 6), (marker, bar.bottom + 6), 3)
            pygame.draw.rect(surface, colour, bar, 2, border_radius=8)

            progress = self.recorder.progress(index)
            status = "OK" if progress >= 1.0 else f"{int(progress * 100)}%"
            ui.draw_text(surface, f"observed {low} - {high}   sweep {status}",
                         (rect.x + 22, rect.bottom - 30), 19,
                         ui.LIME if progress >= 1.0 else ui.TEXT_DIM)
            if self.invert[index - 1]:
                ui.draw_text(surface, "INVERTED", (rect.right - 22, rect.bottom - 30), 19, ui.AMBER,
                             align="topright", bold=True)

        if self.stage == SWEEP:
            ready = self.recorder.complete
            ui.draw_text(surface,
                         "[B1] CONTINUE" if ready else "KEEP TURNING BOTH KNOBS...",
                         (width // 2, height - 72), 26, ui.LIME if ready else ui.AMBER,
                         align="center", bold=True,
                         glow=ui.pulse(self.time, 5.0) if ready else 0.0)
            ui.draw_text(surface, "[B2] or ESC cancel", (width // 2, height - 40), 18, ui.TEXT_DIM,
                         align="center")
        else:
            ui.draw_text(surface, "[B1] SAVE     [B2] REDO SWEEP", (width // 2, height - 78), 26,
                         ui.TEXT, align="center", bold=True)
            ui.draw_text(surface, "[B3] invert pot 1     [B4] invert pot 2   (or keys 1 / 2)",
                         (width // 2, height - 44), 18, ui.TEXT_DIM, align="center")
