"""Small shared widgets used across the non-game screens."""

from __future__ import annotations

import pygame

from .. import ui


def controller_status_line(app) -> tuple:
    """(text, colour) describing the current controller link."""
    controller = app.controller
    if controller.kind == "arduino":
        if controller.connected:
            return (f"ARDUINO CONNECTED  {getattr(controller, 'port', '?')}", ui.LIME)
        return (f"ARDUINO SEARCHING  {getattr(controller, 'port', '?')}", ui.RED)
    if controller.kind == "keyboard":
        return ("KEYBOARD MODE  (no Arduino needed)", ui.AMBER)
    return (f"{controller.kind.upper()} CONTROLLER", ui.VIOLET)


def draw_status_bar(surface: pygame.Surface, app, y: int | None = None) -> None:
    """Connection indicator plus a live mirror of the six inputs."""
    width, height = surface.get_size()
    y = height - 54 if y is None else y
    rect = pygame.Rect(16, y, width - 32, 42)
    ui.draw_panel(surface, rect, border=None, alpha=150)

    text, colour = controller_status_line(app)
    pygame.draw.circle(surface, colour, (rect.x + 22, rect.centery), 8)
    ui.draw_text(surface, text, (rect.x + 40, rect.centery), 18, colour, align="midleft", bold=True)

    controller = app.controller
    bar_w = 120
    x = rect.right - 24
    for index in (4, 3, 2, 1):
        pressed = controller.button(index)
        pygame.draw.circle(surface, ui.LIME if pressed else (48, 52, 78), (x - 14, rect.centery), 9)
        ui.draw_text(surface, str(index), (x - 14, rect.centery), 14,
                     ui.BG if pressed else ui.TEXT_DIM, align="center", bold=True)
        x -= 32
    for index, colour_ in ((2, ui.MAGENTA), (1, ui.CYAN)):
        x -= bar_w + 12
        bar = pygame.Rect(x, rect.centery - 7, bar_w, 14)
        ui.draw_bar(surface, bar, controller.pot(index), colour_)
        ui.draw_text(surface, f"P{index}", (x - 10, rect.centery), 15, colour_, align="midright", bold=True)


class MenuList:
    """Keyboard/mouse/pot navigable vertical menu."""

    def __init__(self, items, on_select, app):
        self.items = list(items)
        self.on_select = on_select
        self.app = app
        self.index = 0
        self.rects: list[pygame.Rect] = []
        self._cooldown = 0.0

    def move(self, delta: int) -> None:
        if not self.items:
            return
        self.index = (self.index + delta) % len(self.items)
        self.app.audio.play("menu_move")

    def select(self) -> None:
        if self.items:
            self.app.audio.play("menu_select")
            self.on_select(self.index)

    def handle_event(self, event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self.move(-1)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.move(1)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.select()
        elif event.type == pygame.MOUSEMOTION:
            for i, rect in enumerate(self.rects):
                if rect.collidepoint(event.pos) and i != self.index:
                    self.index = i
                    self.app.audio.play("menu_move")
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, rect in enumerate(self.rects):
                if rect.collidepoint(event.pos):
                    self.index = i
                    self.select()

    def update(self, dt: float, controller) -> None:
        self._cooldown = max(0.0, self._cooldown - dt)
        if self.items and self._cooldown <= 0.0:
            target = int(controller.pot1 * (len(self.items) - 0.001))
            if target != self.index:
                self.index = max(0, min(len(self.items) - 1, target))
                self.app.audio.play("menu_move")
                self._cooldown = 0.16
        if controller.button_pressed(1):
            self.select()

    def draw(self, surface: pygame.Surface, top: int, width: int = 460, row_h: int = 52,
             accent=ui.CYAN) -> None:
        self.rects = []
        centre_x = surface.get_width() // 2
        for i, item in enumerate(self.items):
            rect = pygame.Rect(0, 0, width, row_h - 8)
            rect.center = (centre_x, top + i * row_h)
            self.rects.append(rect)
            selected = i == self.index
            if selected:
                ui.draw_panel(surface, rect, border=accent, alpha=130)
            ui.draw_text(surface, item, rect.center, 26 if selected else 24,
                         ui.TEXT if selected else ui.TEXT_DIM, align="center", bold=selected)
