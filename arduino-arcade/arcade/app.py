"""Application shell: window, scene stack, controller ownership, overlays."""

from __future__ import annotations

import time
from typing import List, Optional

import pygame

from . import ui
from .audio import Audio, NullAudio
from .controller import Controller
from .effects import Transition
from .keyboard_controller import KeyboardController
from .scene import Scene
from .settings import Settings

TARGET_FPS = 60
#: Seconds of no input before Event Mode bounces back to the launcher.
EVENT_IDLE_TIMEOUT = 75.0


class App:
    """Owns the window, the controller and the scene stack.

    Games never create controllers or open ports themselves; they read
    ``app.controller``, which conforms to the shared Controller API.
    """

    def __init__(
        self,
        settings: Optional[Settings] = None,
        controller: Optional[Controller] = None,
        event_mode: bool = False,
        audio: Optional[Audio] = None,
        size=None,
        headless: bool = False,
    ):
        self.settings = settings or Settings()
        self.event_mode = event_mode
        self.headless = headless
        self.running = False
        self.scenes: List[Scene] = []
        self.transition: Optional[Transition] = None
        self._pending_scene = None
        self._pending_mode = "set"
        self.show_dev_overlay = False
        self.fps = 0.0
        self.idle_timer = 0.0
        self.time = 0.0
        self.messages: List[tuple] = []  # (text, expiry, color)
        #: Set by main(); Event Mode uses it to rebuild the launcher.
        self.launcher_factory = None

        size = tuple(size or self.settings.get("window_size", [1280, 720]))
        self.size = (max(640, size[0]), max(400, size[1]))

        if not headless:
            flags = pygame.RESIZABLE
            if self.event_mode or self.settings.get("fullscreen"):
                flags |= pygame.FULLSCREEN
            try:
                self.screen = pygame.display.set_mode(self.size, flags)
            except pygame.error:
                # Requested mode unsupported (odd resolution, no GPU): fall
                # back to a plain window rather than dying.
                self.screen = pygame.display.set_mode((1280, 720))
            self.size = self.screen.get_size()
            pygame.display.set_caption("ARDUINO ARCADE")
        else:
            self.screen = pygame.Surface(self.size)

        self.audio = audio or (
            NullAudio() if headless else Audio(self.settings.get("volume"), self.settings.get("muted"))
        )
        self.controller: Controller = controller or KeyboardController(self.settings.calibration)
        self.clock = pygame.time.Clock()
        self._controller_was_connected = True

    # ------------------------------------------------------------- scenes

    @property
    def scene(self) -> Optional[Scene]:
        return self.scenes[-1] if self.scenes else None

    def set_scene(self, scene: Scene, transition: bool = True) -> None:
        self._queue_scene(scene, "set", transition)

    def push_scene(self, scene: Scene, transition: bool = True) -> None:
        self._queue_scene(scene, "push", transition)

    def pop_scene(self, transition: bool = True) -> None:
        self._queue_scene(None, "pop", transition)

    def _queue_scene(self, scene, mode: str, transition: bool) -> None:
        self._pending_scene = scene
        self._pending_mode = mode
        if transition and not self.headless:
            self.transition = Transition(closing=True)
        else:
            self._apply_pending()

    def _apply_pending(self) -> None:
        mode, scene = self._pending_mode, self._pending_scene
        self._pending_scene = None
        if mode == "pop":
            if self.scenes:
                self.scenes.pop().on_exit()
            if self.scene:
                self.scene.on_enter()
        elif mode == "push":
            self.scenes.append(scene)
            scene.on_enter()
        else:
            while self.scenes:
                self.scenes.pop().on_exit()
            self.scenes.append(scene)
            scene.on_enter()
        self.controller.reset_edges()

    # ---------------------------------------------------------- controller

    def replace_controller(self, controller: Controller) -> None:
        old = self.controller
        self.controller = controller
        if old is not controller:
            old.close()
        self._controller_was_connected = True

    def use_keyboard_controller(self) -> None:
        """Fallback when the Arduino is unavailable (also bound to K)."""
        if self.controller.kind == "keyboard":
            return
        self.replace_controller(KeyboardController(self.settings.calibration))
        self.toast("KEYBOARD MODE", color=ui.AMBER)

    def apply_calibration(self) -> None:
        self.controller.calibration = self.settings.calibration

    # ------------------------------------------------------------ messages

    def toast(self, text: str, duration: float = 2.5, color=ui.CYAN) -> None:
        self.messages.append((text, self.time + duration, color))
        del self.messages[:-4]

    # ---------------------------------------------------------------- loop

    def quit(self) -> None:
        self.running = False

    def run(self) -> None:
        self.running = True
        while self.running and self.scene is not None:
            dt = min(0.05, self.clock.tick(TARGET_FPS) / 1000.0)
            self.step(dt, pygame.event.get())
            pygame.display.flip()
        self.shutdown()

    def step(self, dt: float, events) -> None:
        """One frame.  Split out from :meth:`run` so tests can drive it."""
        self.time += dt
        self.fps = self.clock.get_fps()
        scene = self.scene
        if scene is None:
            return

        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
                return
            if event.type == pygame.VIDEORESIZE and not self.headless:
                self._handle_resize(event)
                continue
            if event.type == pygame.KEYDOWN:
                self.idle_timer = 0.0
                if event.key == pygame.K_F3:
                    self.show_dev_overlay = not self.show_dev_overlay
                    continue
                if event.key == pygame.K_F11:
                    self.toggle_fullscreen()
                    continue
                if event.key == pygame.K_k and not self.controller.connected:
                    self.use_keyboard_controller()
                    continue
                if event.key == pygame.K_m and (event.mod & pygame.KMOD_CTRL):
                    muted = self.audio.toggle_mute()
                    self.settings.set("muted", muted)
                    self.toast("AUDIO MUTED" if muted else "AUDIO ON")
                    continue
            elif event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEMOTION):
                self.idle_timer = 0.0
            scene.handle_event(event)

        self.controller.update(dt, events)
        if self.controller.any_pressed() or abs(self.controller.pot1 - 0.5) > 0.02:
            self.idle_timer = 0.0
        self.idle_timer += dt

        self._check_controller_link()
        self._check_event_idle()

        if self.transition is not None:
            self.transition.update(dt)
            if self.transition.closing and self.transition.done:
                if self._pending_scene is not None or self._pending_mode == "pop":
                    self._apply_pending()
                self.transition = Transition(closing=False)
            elif not self.transition.closing and self.transition.done:
                self.transition = None

        scene = self.scene
        if scene is None:
            return
        scene.update(dt, self.controller)

        scene.draw(self.screen)
        self._draw_overlays(self.screen)
        if self.transition is not None:
            self.transition.draw(self.screen)

    def _handle_resize(self, event) -> None:
        width, height = max(640, event.w), max(400, event.h)
        try:
            self.screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
        except pygame.error:
            return
        self.size = self.screen.get_size()
        self.settings.set("window_size", list(self.size))
        for scene in self.scenes:
            scene.on_resize(self.size)

    def toggle_fullscreen(self) -> None:
        if self.headless:
            return
        fullscreen = not bool(self.settings.get("fullscreen"))
        try:
            flags = pygame.FULLSCREEN if fullscreen else pygame.RESIZABLE
            self.screen = pygame.display.set_mode(self.size if not fullscreen else (0, 0), flags)
        except pygame.error:
            return
        self.settings.set("fullscreen", fullscreen)
        self.size = self.screen.get_size()
        for scene in self.scenes:
            scene.on_resize(self.size)

    def _check_event_idle(self) -> None:
        """Event Mode: bounce an abandoned session back to the launcher."""
        if not self.event_mode or self.idle_timer < EVENT_IDLE_TIMEOUT:
            return
        if len(self.scenes) <= 1:
            self.idle_timer = 0.0
            return
        self.idle_timer = 0.0
        self.toast("READY FOR THE NEXT PLAYER", color=ui.AMBER)
        if self.launcher_factory is not None:
            self.set_scene(self.launcher_factory())
        else:
            while len(self.scenes) > 1:
                self.scenes.pop().on_exit()
            if self.scene:
                self.scene.on_enter()

    def _check_controller_link(self) -> None:
        connected = self.controller.connected
        if self._controller_was_connected and not connected:
            self._controller_was_connected = False
            if self.scene:
                self.scene.on_controller_lost()
            self.audio.play("warning")
        elif connected and not self._controller_was_connected:
            self._controller_was_connected = True
            self.toast("CONTROLLER RECONNECTED", color=ui.LIME)

    # ------------------------------------------------------------ overlays

    def _draw_overlays(self, surface: pygame.Surface) -> None:
        if not self.controller.connected:
            self._draw_disconnect_banner(surface)
        self._draw_messages(surface)
        if self.show_dev_overlay:
            self._draw_dev_overlay(surface)

    def _draw_disconnect_banner(self, surface: pygame.Surface) -> None:
        width, height = surface.get_size()
        rect = pygame.Rect(width // 2 - 300, height // 2 - 70, 600, 140)
        ui.draw_panel(surface, rect, border=ui.RED, alpha=235)
        ui.draw_text(surface, "CONTROLLER DISCONNECTED", rect.center, 30, ui.RED,
                     align="center", bold=True, glow=1.0)
        ui.draw_text(surface, "Reconnecting...  press K for keyboard mode",
                     (rect.centerx, rect.centery + 38), 20, ui.TEXT_DIM, align="center")

    def _draw_messages(self, surface: pygame.Surface) -> None:
        self.messages = [m for m in self.messages if m[1] > self.time]
        for i, (text, expiry, color) in enumerate(self.messages):
            alpha = int(255 * min(1.0, (expiry - self.time) / 0.6))
            ui.draw_text(surface, text, (surface.get_width() // 2, 24 + i * 26), 20, color,
                         align="center", alpha=alpha, bold=True)

    def _draw_dev_overlay(self, surface: pygame.Surface) -> None:
        controller = self.controller
        port = getattr(controller, "port", "-")
        scene = self.scene
        lines = [
            f"FPS         {self.fps:5.1f}",
            f"controller  {controller.kind}",
            f"port        {port}",
            f"connected   {controller.connected}",
            f"POT1 raw    {controller.pot1_raw:4d}   norm {controller.pot1:.3f}",
            f"POT2 raw    {controller.pot2_raw:4d}   norm {controller.pot2:.3f}",
            f"buttons     {''.join('1' if b else '0' for b in controller.buttons)}",
            f"scene       {scene.name if scene else '-'}",
            f"state       {scene.state_name if scene else '-'}",
            f"event mode  {self.event_mode}   idle {self.idle_timer:.0f}s",
        ]
        packets = getattr(controller, "packets_received", None)
        if packets is not None:
            lines.append(f"packets     {packets} ok / {getattr(controller, 'bad_packets', 0)} bad")
        rect = pygame.Rect(10, 10, 340, 24 * len(lines) + 20)
        ui.draw_panel(surface, rect, border=ui.LIME, alpha=205)
        for i, line in enumerate(lines):
            ui.draw_text(surface, line, (rect.x + 14, rect.y + 12 + i * 24), 17, ui.LIME)

    # ------------------------------------------------------------ shutdown

    def shutdown(self) -> None:
        while self.scenes:
            self.scenes.pop().on_exit()
        self.controller.close()
        self.audio.stop_all()


def now() -> float:
    return time.monotonic()
