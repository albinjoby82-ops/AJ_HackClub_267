"""Shared game scaffolding.

Every game is a :class:`BaseGame`.  The base class owns the state machine,
pause menu, game-over screen, high score handling, screen shake and particle
systems, so the individual games only implement their own play logic.

State machine::

    INTRO -> COUNTDOWN -> PLAYING -> GAME_OVER -> (restart) COUNTDOWN
                              ^  |
                              |  v
                            PAUSED
"""

from __future__ import annotations

from typing import List, Sequence, Tuple

import pygame

from . import ui
from .effects import FloatingTextSystem, ParticleSystem, ScreenShake
from .scene import Scene

INTRO = "intro"
COUNTDOWN = "countdown"
PLAYING = "playing"
PAUSED = "paused"
GAME_OVER = "game_over"

COUNTDOWN_TIME = 3.0

PAUSE_ITEMS = ("RESUME", "RESTART", "QUIT TO ARCADE")


class BaseGame(Scene):
    """Common shell for the four arcade games."""

    #: Persistent high-score key; empty means "this game does not score".
    game_id = "game"
    title = "GAME"
    subtitle = ""
    accent = ui.CYAN
    #: (label, action) rows shown on the animated intro card.
    control_hints: Sequence[Tuple[str, str]] = ()
    #: Games that end in a win/lose result rather than a score set this False.
    tracks_high_score = True
    score_label = "SCORE"

    def __init__(self, app):
        super().__init__(app)
        self.state = INTRO
        self.time = 0.0
        self.state_time = 0.0
        self.score = 0
        self.particles = ParticleSystem()
        self.floaters = FloatingTextSystem()
        self.shake = ScreenShake()
        self.pause_index = 0
        self.new_high_score = False
        self.result_text = "GAME OVER"
        self._pot_menu_cooldown = 0.0
        self.size = app.screen.get_size()

    # ------------------------------------------------------------ lifecycle

    @property
    def name(self) -> str:
        return self.title

    @property
    def state_name(self) -> str:
        return self.state

    @property
    def high_score(self) -> int:
        return self.app.settings.high_score(self.game_id)

    def on_enter(self) -> None:
        self.size = self.app.screen.get_size()
        self.set_state(INTRO)

    def on_resize(self, size) -> None:
        self.size = size

    def on_controller_lost(self) -> None:
        if self.state == PLAYING:
            self.set_state(PAUSED)

    def set_state(self, state: str) -> None:
        self.state = state
        self.state_time = 0.0
        if state == PAUSED:
            self.pause_index = 0

    # ------------------------------------------------------------- hooks

    def reset_game(self) -> None:
        """Reset all play state.  Called before every countdown."""

    def update_play(self, dt: float, controller) -> None:
        """Per-frame gameplay.  Call :meth:`game_over` to finish."""
        raise NotImplementedError

    def draw_play(self, surface: pygame.Surface) -> None:
        """Draw the playfield (already shake-offset via ``self.shake``)."""
        raise NotImplementedError

    def draw_hud(self, surface: pygame.Surface) -> None:
        """Draw score/meters.  Not affected by screen shake."""
        self.draw_default_hud(surface)

    def draw_background(self, surface: pygame.Surface) -> None:
        surface.fill(ui.BG)

    def result_lines(self) -> List[Tuple[str, tuple]]:
        """Extra lines shown on the game-over card."""
        return []

    # ------------------------------------------------------------- helpers

    def game_over(self, result_text: str = "GAME OVER") -> None:
        if self.state == GAME_OVER:
            return
        self.result_text = result_text
        self.new_high_score = False
        if self.tracks_high_score and self.game_id:
            self.new_high_score = self.app.settings.submit_score(self.game_id, int(self.score))
        self.app.audio.play("game_over")
        self.set_state(GAME_OVER)

    def start_countdown(self) -> None:
        self.reset_game()
        self.particles.clear()
        self.floaters.clear()
        self.shake.reset()
        self.set_state(COUNTDOWN)

    def quit_to_launcher(self) -> None:
        self.app.audio.play("back")
        self.app.pop_scene()

    # --------------------------------------------------------------- frame

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN:
            return
        if event.key == pygame.K_ESCAPE:
            if self.state == PLAYING:
                self.set_state(PAUSED)
            elif self.state in (PAUSED, INTRO, GAME_OVER):
                self.quit_to_launcher()
        elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
            self._confirm()
        elif event.key == pygame.K_p and self.state == PLAYING:
            self.set_state(PAUSED)
        elif event.key in (pygame.K_UP, pygame.K_w) and self.state == PAUSED:
            self._move_pause(-1)
        elif event.key in (pygame.K_DOWN, pygame.K_s) and self.state == PAUSED:
            self._move_pause(1)

    def _move_pause(self, delta: int) -> None:
        self.pause_index = (self.pause_index + delta) % len(PAUSE_ITEMS)
        self.app.audio.play("menu_move")

    def _confirm(self) -> None:
        if self.state == INTRO:
            self.app.audio.play("menu_select")
            self.start_countdown()
        elif self.state == GAME_OVER:
            self.app.audio.play("menu_select")
            self.start_countdown()
        elif self.state == PAUSED:
            self._activate_pause_item()
        elif self.state == PLAYING:
            pass

    def _activate_pause_item(self) -> None:
        choice = PAUSE_ITEMS[self.pause_index]
        self.app.audio.play("menu_select")
        if choice == "RESUME":
            self.set_state(PLAYING)
        elif choice == "RESTART":
            self.start_countdown()
        else:
            self.quit_to_launcher()

    def update(self, dt: float, controller) -> None:
        self.time += dt
        self.state_time += dt
        self._pot_menu_cooldown = max(0.0, self._pot_menu_cooldown - dt)
        self.shake.update(dt)

        if self.state == INTRO:
            self._update_menu_state(controller, on_confirm=self.start_countdown)
        elif self.state == COUNTDOWN:
            if self.state_time >= COUNTDOWN_TIME:
                self.set_state(PLAYING)
                self.app.audio.play("menu_select")
            self.particles.update(dt)
        elif self.state == PLAYING:
            if controller.button_pressed(4) and controller.button(3):
                # Two-button "panic" chord pauses without a keyboard.
                self.set_state(PAUSED)
            else:
                self.update_play(dt, controller)
            self.particles.update(dt)
            self.floaters.update(dt)
        elif self.state == PAUSED:
            self._update_pause(dt, controller)
        elif self.state == GAME_OVER:
            self.particles.update(dt)
            self.floaters.update(dt)
            if self.state_time > 0.7:
                self._update_menu_state(
                    controller,
                    on_confirm=self.start_countdown,
                    on_back=self.quit_to_launcher,
                )

    def _update_menu_state(self, controller, on_confirm, on_back=None) -> None:
        if controller.button_pressed(1):
            self.app.audio.play("menu_select")
            on_confirm()
        elif controller.button_pressed(2) and on_back is not None:
            on_back()
        elif controller.button_pressed(2) and self.state == INTRO:
            self.quit_to_launcher()

    def _update_pause(self, dt: float, controller) -> None:
        # Pot 1 scrolls the pause menu so a player can escape without a keyboard.
        if self._pot_menu_cooldown <= 0.0:
            index = int(controller.pot1 * (len(PAUSE_ITEMS) - 0.001))
            if index != self.pause_index:
                self.pause_index = max(0, min(len(PAUSE_ITEMS) - 1, index))
                self.app.audio.play("menu_move")
                self._pot_menu_cooldown = 0.18
        if controller.button_pressed(1):
            self._activate_pause_item()
        elif controller.button_pressed(2):
            self.set_state(PLAYING)

    # ---------------------------------------------------------------- draw

    def draw(self, surface: pygame.Surface) -> None:
        self.size = surface.get_size()
        self.draw_background(surface)
        if self.state in (COUNTDOWN, PLAYING, PAUSED, GAME_OVER):
            self.draw_play(surface)
            self.particles.draw(surface, self.shake.offset)
            self.floaters.draw(surface, self.shake.offset)
            self.draw_hud(surface)
        if self.state == INTRO:
            self.draw_intro(surface)
        elif self.state == COUNTDOWN:
            self.draw_countdown(surface)
        elif self.state == PAUSED:
            self.draw_pause(surface)
        elif self.state == GAME_OVER:
            self.draw_game_over(surface)

    def draw_default_hud(self, surface: pygame.Surface) -> None:
        width = surface.get_width()
        ui.draw_text(surface, f"{self.score_label} {int(self.score):,}", (24, 20), 30, ui.TEXT, bold=True, glow=0.5)
        if self.tracks_high_score:
            ui.draw_text(surface, f"BEST {self.high_score:,}", (width - 24, 22), 22, ui.TEXT_DIM, align="topright")

    def draw_intro(self, surface: pygame.Surface) -> None:
        width, height = surface.get_size()
        overlay = pygame.Surface((width, height), pygame.SRCALPHA)
        overlay.fill((*ui.BG_DEEP, 215))
        surface.blit(overlay, (0, 0))
        glow = 0.6 + 0.5 * ui.pulse(self.time, 2.4)
        ui.draw_text(surface, self.title, (width // 2, height * 0.16), 68, self.accent,
                     align="center", bold=True, glow=glow)
        if self.subtitle:
            ui.draw_text(surface, self.subtitle, (width // 2, height * 0.16 + 56), 22, ui.TEXT_DIM, align="center")

        hints = list(self.control_hints)
        panel_h = min(int(height * 0.46), 52 * max(1, len(hints)) + 24)
        rect = pygame.Rect(0, 0, min(680, int(width * 0.72)), panel_h)
        rect.center = (width // 2, int(height * 0.55))
        ui.draw_control_hint(surface, rect, hints, self.time, self.accent)

        prompt_alpha = int(140 + 115 * ui.pulse(self.time, 4.0))
        ui.draw_text(surface, "[ BUTTON 1 ]  or  ENTER   to START", (width // 2, height * 0.86), 26,
                     ui.TEXT, align="center", bold=True, alpha=prompt_alpha)
        ui.draw_text(surface, "[ BUTTON 2 ]  or  ESC   back to arcade", (width // 2, height * 0.92), 19,
                     ui.TEXT_DIM, align="center")

    def draw_countdown(self, surface: pygame.Surface) -> None:
        width, height = surface.get_size()
        remaining = COUNTDOWN_TIME - self.state_time
        label = "GO!" if remaining <= 1.0 else str(int(remaining))
        phase = 1.0 - (remaining % 1.0)
        size = int(120 + 90 * (1.0 - phase))
        alpha = int(255 * min(1.0, phase * 3.0))
        color = ui.LIME if label == "GO!" else self.accent
        ui.draw_text(surface, label, (width // 2, height // 2), size, color,
                     align="center", bold=True, glow=1.2, alpha=alpha)

    def draw_pause(self, surface: pygame.Surface) -> None:
        width, height = surface.get_size()
        overlay = pygame.Surface((width, height), pygame.SRCALPHA)
        overlay.fill((*ui.BG_DEEP, 200))
        surface.blit(overlay, (0, 0))
        ui.draw_text(surface, "PAUSED", (width // 2, height * 0.28), 60, ui.AMBER,
                     align="center", bold=True, glow=0.8)
        for i, item in enumerate(PAUSE_ITEMS):
            selected = i == self.pause_index
            y = height * 0.46 + i * 56
            color = ui.TEXT if selected else ui.TEXT_DIM
            if selected:
                marker = pygame.Rect(0, 0, 420, 46)
                marker.center = (width // 2, int(y))
                ui.draw_panel(surface, marker, border=self.accent, alpha=120)
            ui.draw_text(surface, item, (width // 2, y), 30, color, align="center", bold=selected)
        ui.draw_text(surface, "POT 1 to choose   BUTTON 1 select   BUTTON 2 resume",
                     (width // 2, height * 0.82), 19, ui.TEXT_DIM, align="center")

    def draw_game_over(self, surface: pygame.Surface) -> None:
        width, height = surface.get_size()
        fade = min(1.0, self.state_time * 1.6)
        overlay = pygame.Surface((width, height), pygame.SRCALPHA)
        overlay.fill((*ui.BG_DEEP, int(210 * fade)))
        surface.blit(overlay, (0, 0))

        pop = ui.ease_out(min(1.0, self.state_time * 2.2))
        ui.draw_text(surface, self.result_text, (width // 2, height * 0.24), int(40 + 32 * pop),
                     ui.MAGENTA, align="center", bold=True, glow=1.2)
        if self.tracks_high_score:
            ui.draw_text(surface, f"{self.score_label} {int(self.score):,}", (width // 2, height * 0.42),
                         46, ui.TEXT, align="center", bold=True)
            if self.new_high_score:
                ui.draw_text(surface, "NEW HIGH SCORE!", (width // 2, height * 0.5), 28, ui.LIME,
                             align="center", bold=True, glow=ui.pulse(self.time, 6.0))
            else:
                ui.draw_text(surface, f"BEST {self.high_score:,}", (width // 2, height * 0.5), 24,
                             ui.TEXT_DIM, align="center")
        y = height * 0.58
        for text, color in self.result_lines():
            ui.draw_text(surface, text, (width // 2, y), 22, color, align="center")
            y += 30
        alpha = int(140 + 115 * ui.pulse(self.time, 4.0))
        ui.draw_text(surface, "[ BUTTON 1 ] PLAY AGAIN", (width // 2, height * 0.8), 26, ui.TEXT,
                     align="center", bold=True, alpha=alpha)
        ui.draw_text(surface, "[ BUTTON 2 ] BACK TO ARCADE", (width // 2, height * 0.87), 22, ui.TEXT_DIM,
                     align="center")


def clamp(value: float, low: float, high: float) -> float:
    return low if value < low else high if value > high else value


def approach(current: float, target: float, rate: float, dt: float) -> float:
    """Frame-rate independent move towards ``target``."""
    return current + (target - current) * min(1.0, rate * dt)


def scaled(surface: pygame.Surface, base: float) -> float:
    """Design-space (1280x720) measurement scaled to the live surface."""
    return base * surface.get_height() / 720.0
