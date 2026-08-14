"""Scene base class.  The app owns a stack of these."""

from __future__ import annotations

import pygame


class Scene:
    #: Shown by the developer overlay.
    name = "scene"

    def __init__(self, app):
        self.app = app

    # Lifecycle -----------------------------------------------------------
    def on_enter(self) -> None:
        """Called when this scene becomes the active one."""

    def on_exit(self) -> None:
        """Called when the scene is popped or replaced."""

    def on_resize(self, size) -> None:
        """Called when the window changes size."""

    # Frame ---------------------------------------------------------------
    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle one pygame event (keyboard/mouse/window)."""

    def update(self, dt: float, controller) -> None:
        raise NotImplementedError

    def draw(self, surface: pygame.Surface) -> None:
        raise NotImplementedError

    # Hardware ------------------------------------------------------------
    def on_controller_lost(self) -> None:
        """Called once when the Arduino link drops; games should pause."""

    @property
    def state_name(self) -> str:
        """Sub-state shown in the developer overlay."""
        return "-"
