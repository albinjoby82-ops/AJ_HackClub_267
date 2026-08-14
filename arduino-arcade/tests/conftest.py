import os
import sys

# Headless by default so the suite runs on CI and over remote sessions.
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest  # noqa: E402


@pytest.fixture()
def settings_path(tmp_path):
    return str(tmp_path / "settings.json")


@pytest.fixture()
def app(tmp_path):
    """A headless App with a simulated controller and silent audio."""
    import pygame

    from arcade.app import App
    from arcade.audio import NullAudio
    from arcade.settings import Settings
    from arcade.simulated_controller import SimulatedController

    pygame.init()
    instance = App(
        settings=Settings(str(tmp_path / "settings.json")),
        controller=SimulatedController(),
        audio=NullAudio(),
        headless=True,
    )
    yield instance
    instance.shutdown()
