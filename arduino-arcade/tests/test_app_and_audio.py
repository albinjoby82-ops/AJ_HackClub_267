"""App shell, scene stack, event mode, and audio degradation."""

import pygame

from arcade.audio import RECIPES, Audio, NullAudio, generate_assets
from arcade.keyboard_controller import KeyboardController
from arcade.scene import Scene
from arcade.simulated_controller import SimulatedController
from games import GAMES

DT = 1 / 60.0


class DummyScene(Scene):
    name = "dummy"

    def __init__(self, app):
        super().__init__(app)
        self.updates = 0
        self.entered = 0
        self.exited = 0
        self.lost_controller = 0

    def on_enter(self):
        self.entered += 1

    def on_exit(self):
        self.exited += 1

    def on_controller_lost(self):
        self.lost_controller += 1

    def update(self, dt, controller):
        self.updates += 1

    def draw(self, surface):
        surface.fill((0, 0, 0))


def test_scene_stack_push_pop(app):
    first, second = DummyScene(app), DummyScene(app)
    app.set_scene(first, transition=False)
    app.step(DT, [])
    assert app.scene is first and first.entered == 1

    app.push_scene(second, transition=False)
    app.step(DT, [])
    assert app.scene is second

    app.pop_scene(transition=False)
    app.step(DT, [])
    assert app.scene is first
    assert second.exited == 1


def test_headless_scene_swaps_are_immediate(app):
    """Transitions are cosmetic and skipped headless, so tests stay fast."""
    first, second = DummyScene(app), DummyScene(app)
    app.set_scene(first, transition=False)
    app.step(DT, [])
    app.push_scene(second, transition=True)
    app.step(DT, [])
    assert app.scene is second


def test_transition_wipe_completes():
    from arcade.effects import Transition

    wipe = Transition(duration=0.3, closing=True)
    assert not wipe.done and wipe.progress == 0.0
    for _ in range(20):
        wipe.update(DT)
    assert wipe.done and wipe.progress == 1.0
    surface = pygame.Surface((320, 200))
    wipe.draw(surface)


def test_dev_overlay_toggles_with_f3(app):
    app.set_scene(DummyScene(app), transition=False)
    assert not app.show_dev_overlay
    app.step(DT, [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_F3, mod=0)])
    assert app.show_dev_overlay
    app.step(DT, [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_F3, mod=0)])
    assert not app.show_dev_overlay


def test_dev_overlay_renders_for_every_backend(app):
    app.set_scene(DummyScene(app), transition=False)
    app.show_dev_overlay = True
    for controller in (SimulatedController(), KeyboardController()):
        app.replace_controller(controller)
        app.step(DT, [])


def test_quit_event_stops_the_loop(app):
    app.set_scene(DummyScene(app), transition=False)
    app.running = True
    app.step(DT, [pygame.event.Event(pygame.QUIT)])
    assert not app.running


def test_controller_loss_notifies_the_scene(app):
    scene = DummyScene(app)
    app.set_scene(scene, transition=False)

    class Flaky(SimulatedController):
        @property
        def connected(self):
            return False

    app.replace_controller(Flaky())
    app.step(DT, [])
    assert scene.lost_controller == 1
    app.step(DT, [])
    assert scene.lost_controller == 1     # fires once, not every frame


def test_keyboard_fallback_key_switches_backend(app):
    scene = DummyScene(app)
    app.set_scene(scene, transition=False)

    class Flaky(SimulatedController):
        @property
        def connected(self):
            return False

    app.replace_controller(Flaky())
    app.step(DT, [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_k, mod=0)])
    assert app.controller.kind == "keyboard"


def test_event_mode_returns_to_launcher_when_idle(app):
    from arcade.app import EVENT_IDLE_TIMEOUT

    launcher = DummyScene(app)
    app.event_mode = True
    app.launcher_factory = lambda: launcher
    app.set_scene(DummyScene(app), transition=False)
    app.push_scene(GAMES["neon_drift"](app), transition=False)
    app.step(DT, [])
    app.idle_timer = EVENT_IDLE_TIMEOUT + 1
    app.step(DT, [])
    for _ in range(60):
        app.step(DT, [])
    assert app.scene is launcher


def test_null_audio_is_silent_and_safe():
    audio = NullAudio()
    audio.play("explosion")
    audio.set_volume(0.5)
    audio.toggle_mute()
    audio.stop_all()
    assert not audio.available


def test_audio_survives_a_missing_device(monkeypatch):
    def boom(*args, **kwargs):
        raise pygame.error("no audio device")

    monkeypatch.setattr(pygame.mixer, "init", boom)
    audio = Audio()
    assert not audio.available
    assert audio.error
    audio.play("shoot")          # must not raise


def test_sound_assets_generate_once():
    generate_assets()
    created = generate_assets()
    assert created == []         # already on disk, nothing rewritten
    assert len(RECIPES) >= 15


def test_mute_round_trips_through_settings(app):
    app.audio = Audio(0.5, muted=False)
    muted = app.audio.toggle_mute()
    app.settings.set("muted", muted)
    assert app.settings.get("muted") is True
