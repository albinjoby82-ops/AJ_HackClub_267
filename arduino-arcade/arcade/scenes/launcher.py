"""The main arcade launcher: four animated game cards plus utility options."""

from __future__ import annotations

import math
from typing import List

import pygame

from .. import ui
from ..effects import Starfield
from ..scene import Scene
from .widgets import draw_status_bar

#: (id, title, tagline, accent, factory-path)
GAME_CARDS = [
    ("neon_drift", "NEON DRIFT", "ENDLESS NEON HIGHWAY", ui.MAGENTA),
    ("orbital_defender", "ORBITAL DEFENDER", "HOLD THE STATION", ui.CYAN),
    ("reactor_sync", "REACTOR SYNC", "TWIST TO SURVIVE", ui.LIME),
    ("twin_pong", "TWIN PONG", "TWO PLAYERS, ONE BOARD", ui.AMBER),
]

OPTIONS = ["CONTROLLER TEST", "CALIBRATION", "SETTINGS", "HOW TO PLAY", "EXIT"]
EVENT_OPTIONS = ["CONTROLLER TEST", "HOW TO PLAY"]


class Launcher(Scene):
    name = "launcher"

    def __init__(self, app, launch_game, open_screen):
        super().__init__(app)
        self.launch_game = launch_game
        self.open_screen = open_screen
        self.row = 0            # 0 = game cards, 1 = options
        self.card_index = 0
        self.option_index = 0
        self.stars = Starfield(app.screen.get_size(), count=120, speed=16.0)
        self.time = 0.0
        self._cooldown = 0.0
        self.card_rects: List[pygame.Rect] = []
        self.option_rects: List[pygame.Rect] = []

    @property
    def options(self) -> List[str]:
        return EVENT_OPTIONS if self.app.event_mode else OPTIONS

    @property
    def state_name(self) -> str:
        return f"row{self.row}"

    def on_enter(self) -> None:
        self.app.audio.play("back", 0.5)

    def on_resize(self, size) -> None:
        self.stars.resize(size)

    # ------------------------------------------------------------ controls

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_LEFT, pygame.K_a):
                self._move(-1)
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                self._move(1)
            elif event.key in (pygame.K_UP, pygame.K_DOWN, pygame.K_TAB, pygame.K_w, pygame.K_s):
                self._switch_row()
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self._select()
            elif event.key == pygame.K_ESCAPE and not self.app.event_mode:
                self.app.quit()
        elif event.type == pygame.MOUSEMOTION:
            self._hover(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self._hover(event.pos):
                self._select()

    def _hover(self, pos) -> bool:
        for i, rect in enumerate(self.card_rects):
            if rect.collidepoint(pos):
                if (self.row, self.card_index) != (0, i):
                    self.app.audio.play("menu_move")
                self.row, self.card_index = 0, i
                return True
        for i, rect in enumerate(self.option_rects):
            if rect.collidepoint(pos):
                if (self.row, self.option_index) != (1, i):
                    self.app.audio.play("menu_move")
                self.row, self.option_index = 1, i
                return True
        return False

    def _move(self, delta: int) -> None:
        if self.row == 0:
            self.card_index = (self.card_index + delta) % len(GAME_CARDS)
        else:
            self.option_index = (self.option_index + delta) % len(self.options)
        self.app.audio.play("menu_move")

    def _switch_row(self) -> None:
        self.row = 1 - self.row
        self.app.audio.play("menu_move")

    def _select(self) -> None:
        self.app.audio.play("menu_select")
        if self.row == 0:
            self.launch_game(GAME_CARDS[self.card_index][0])
        else:
            self.open_screen(self.options[self.option_index])

    def update(self, dt: float, controller) -> None:
        self.time += dt
        self.stars.update(dt)
        self._cooldown = max(0.0, self._cooldown - dt)

        count = len(GAME_CARDS) if self.row == 0 else len(self.options)
        if self._cooldown <= 0.0:
            target = int(controller.pot1 * (count - 0.001))
            target = max(0, min(count - 1, target))
            current = self.card_index if self.row == 0 else self.option_index
            if target != current:
                if self.row == 0:
                    self.card_index = target
                else:
                    self.option_index = target
                self.app.audio.play("menu_move")
                self._cooldown = 0.16

        if controller.button_pressed(1):
            self._select()
        elif controller.button_pressed(2):
            if self.row == 1:
                self._switch_row()
        elif controller.button_pressed(3):
            self._switch_row()
        elif controller.button_pressed(4) and not self.app.event_mode:
            self.open_screen("CONTROLLER TEST")

    # -------------------------------------------------------------- render

    def draw(self, surface: pygame.Surface) -> None:
        width, height = surface.get_size()
        surface.fill(ui.BG_DEEP)
        self.stars.draw(surface)
        self._draw_header(surface)
        self._draw_cards(surface)
        self._draw_options(surface)
        draw_status_bar(surface, self.app)
        hint = "POT 1 MOVE   B1 SELECT   B3 SWITCH ROW   B4 CONTROLLER TEST"
        ui.draw_text(surface, hint, (width // 2, height - 74), 17, ui.TEXT_DIM, align="center")

    def _draw_header(self, surface: pygame.Surface) -> None:
        width, height = surface.get_size()
        glow = 0.7 + 0.5 * ui.pulse(self.time, 1.6)
        ui.draw_text(surface, "ARDUINO ARCADE", (width // 2, int(height * 0.07)), 62, ui.CYAN,
                     align="center", bold=True, glow=glow)
        subtitle = "EVENT MODE" if self.app.event_mode else "FOUR GAMES - ONE BREADBOARD"
        ui.draw_text(surface, subtitle, (width // 2, int(height * 0.135)), 20,
                     ui.AMBER if self.app.event_mode else ui.TEXT_DIM, align="center")

    def _draw_cards(self, surface: pygame.Surface) -> None:
        width, height = surface.get_size()
        self.card_rects = []
        margin = width * 0.04
        card_w = (width - margin * 2 - 3 * 18) / 4
        card_h = height * 0.42
        top = height * 0.19
        for i, (game_id, title, tagline, accent) in enumerate(GAME_CARDS):
            selected = self.row == 0 and self.card_index == i
            lift = 14 * (1.0 + math.sin(self.time * 2.2 + i)) * 0.5 if selected else 0.0
            rect = pygame.Rect(int(margin + i * (card_w + 18)), int(top - lift), int(card_w), int(card_h))
            self.card_rects.append(rect)
            ui.draw_panel(surface, rect, color=(14, 16, 34), border=accent if selected else (46, 50, 80),
                          alpha=225, width=3 if selected else 2)
            if selected:
                halo = pygame.Surface((rect.width + 24, rect.height + 24))
                pygame.draw.rect(halo, tuple(c // 7 for c in accent), halo.get_rect(),
                                 border_radius=18, width=12)
                surface.blit(halo, (rect.x - 12, rect.y - 12), special_flags=pygame.BLEND_ADD)

            self._draw_card_art(surface, rect, i, accent, selected)
            ui.draw_text(surface, str(i + 1), (rect.x + 14, rect.y + 10), 20,
                         accent if selected else ui.TEXT_DIM, bold=True)
            ui.draw_text(surface, title, (rect.centerx, rect.bottom - 62), 24 if len(title) < 14 else 21,
                         ui.TEXT if selected else ui.TEXT_DIM, align="center", bold=True,
                         glow=0.7 if selected else 0.0)
            ui.draw_text(surface, tagline, (rect.centerx, rect.bottom - 36), 15, ui.TEXT_DIM, align="center")
            best = self.app.settings.high_score(game_id)
            if best:
                ui.draw_text(surface, f"BEST {best:,}", (rect.centerx, rect.bottom - 18), 15, accent,
                             align="center")

    def _draw_card_art(self, surface, rect: pygame.Rect, index: int, accent, selected: bool) -> None:
        """Tiny animated illustration so each card reads at a glance."""
        art = pygame.Rect(rect.x + 12, rect.y + 40, rect.width - 24, rect.height - 118)
        pygame.draw.rect(surface, (8, 9, 22), art, border_radius=8)
        t = self.time * (1.8 if selected else 0.6)
        if index == 0:   # Neon Drift - perspective road
            for i in range(6):
                k = (i + (t * 0.6) % 1.0) / 6.0
                y = art.bottom - k * art.height
                half = art.width * 0.5 * (0.12 + 0.88 * k)
                pygame.draw.line(surface, accent, (art.centerx - half, y), (art.centerx + half, y), 2)
            pygame.draw.polygon(surface, ui.CYAN, [
                (art.centerx, art.bottom - 24), (art.centerx - 12, art.bottom - 8),
                (art.centerx + 12, art.bottom - 8)])
        elif index == 1:  # Orbital Defender - station + orbiting turret
            radius = min(art.width, art.height) * 0.3
            pygame.draw.circle(surface, (60, 70, 110), art.center, int(radius), 1)
            pygame.draw.circle(surface, accent, art.center, int(radius * 0.35))
            angle = t
            pos = (art.centerx + math.cos(angle) * radius, art.centery + math.sin(angle) * radius)
            pygame.draw.circle(surface, ui.WHITE, (int(pos[0]), int(pos[1])), 5)
        elif index == 2:  # Reactor Sync - two waveforms
            for row, colour in ((0.35, ui.CYAN), (0.68, ui.MAGENTA)):
                points = []
                freq = 3.0 if row < 0.5 else 5.0
                for i in range(28):
                    x = art.x + art.width * i / 27
                    y = art.y + art.height * row + math.sin(i * 0.5 + t * freq) * art.height * 0.12
                    points.append((x, y))
                pygame.draw.lines(surface, colour, False, points, 2)
        else:            # Twin Pong - two paddles and a ball
            pygame.draw.rect(surface, ui.CYAN, (art.x + 8, art.centery - 18 + math.sin(t) * 14, 6, 36))
            pygame.draw.rect(surface, ui.MAGENTA, (art.right - 14, art.centery - 18 - math.sin(t) * 14, 6, 36))
            bx = art.centerx + math.sin(t * 1.7) * art.width * 0.3
            pygame.draw.circle(surface, ui.WHITE, (int(bx), int(art.centery)), 6)

    def _draw_options(self, surface: pygame.Surface) -> None:
        width, height = surface.get_size()
        self.option_rects = []
        options = self.options
        total = width * 0.86
        button_w = total / len(options)
        y = height * 0.68
        for i, label in enumerate(options):
            rect = pygame.Rect(int(width * 0.07 + i * button_w + 6), int(y), int(button_w - 12), 46)
            self.option_rects.append(rect)
            selected = self.row == 1 and self.option_index == i
            ui.draw_panel(surface, rect, color=(16, 18, 38),
                          border=ui.VIOLET if selected else (46, 50, 80), alpha=220,
                          width=3 if selected else 2)
            ui.draw_text(surface, label, rect.center, 19 if selected else 18,
                         ui.TEXT if selected else ui.TEXT_DIM, align="center", bold=selected)
