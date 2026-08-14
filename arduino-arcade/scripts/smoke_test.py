"""Headless smoke test: drives every screen and game with a scripted controller.

    python scripts/smoke_test.py            all games, ~8 simulated seconds each
    python scripts/smoke_test.py --seconds 20 --size 1920x1080

Runs with the dummy SDL video/audio drivers, so it works over SSH and on CI.
"""

from __future__ import annotations

import argparse
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame  # noqa: E402

from arcade.app import App  # noqa: E402
from arcade.audio import NullAudio  # noqa: E402
from arcade.game import GAME_OVER, PLAYING  # noqa: E402
from arcade.simulated_controller import SimulatedController  # noqa: E402
from arcade.settings import Settings  # noqa: E402
from arcade.scenes.calibration_scene import CalibrationScene  # noqa: E402
from arcade.scenes.controller_test import ControllerTest  # noqa: E402
from arcade.scenes.howto import HowToPlay  # noqa: E402
from arcade.scenes.settings_scene import SettingsScene  # noqa: E402
from games import GAMES  # noqa: E402
from main import Arcade  # noqa: E402

DT = 1.0 / 60.0


def build_app(size=(1280, 720), settings_path=None) -> App:
    pygame.init()
    settings = Settings(settings_path or os.path.join(os.path.dirname(__file__), "..", ".smoke-settings.json"))
    controller = SimulatedController()
    app = App(settings=settings, controller=controller, audio=NullAudio(), size=size, headless=True)
    return app


def script_controller(controller: SimulatedController) -> None:
    """A generic 'someone is playing' input script that suits all four games."""
    (controller
     .sweep(1, 0.5, 0.9, 1.2).sweep(2, 0.5, 1.0, 1.0)
     .tap(1).tap(2)
     .wiggle(1, 2.0, 1.5).wiggle(2, 2.0, 2.0)
     .tap(3).tap(4)
     .sweep(1, 0.9, 0.1, 1.6).sweep(2, 1.0, 0.3, 1.2)
     .hold(1, 0.5).tap(2).tap(3).tap(4)
     .wiggle(1, 3.0, 3.0).wiggle(2, 3.0, 2.5))


def run_game(app: App, game_id: str, seconds: float, verbose: bool = True) -> dict:
    controller = SimulatedController()
    app.replace_controller(controller)
    game = GAMES[game_id](app)
    app.set_scene(game, transition=False)

    # Intro -> countdown -> play.
    controller.press(1)
    app.step(DT, [])
    controller.release(1)
    for _ in range(int(3.4 / DT)):
        app.step(DT, [])

    script_controller(controller)
    states = set()
    frames = int(seconds / DT)
    for _ in range(frames):
        app.step(DT, [])
        states.add(game.state)
        if controller.script_finished:
            script_controller(controller)

    result = {
        "game": game_id,
        "state": game.state,
        "score": int(game.score),
        "states": sorted(states),
        "particles": len(game.particles),
    }

    # Exercise pause, restart and game over paths.
    game.set_state(PLAYING)
    game.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE))
    app.step(DT, [])
    assert game.state == "paused", f"{game_id}: escape did not pause"
    game.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN))
    app.step(DT, [])

    game.game_over("SMOKE TEST")
    for _ in range(60):
        app.step(DT, [])
    assert game.state == GAME_OVER, f"{game_id}: did not reach game over"
    game.start_countdown()
    for _ in range(30):
        app.step(DT, [])

    # Back to the launcher.
    game.quit_to_launcher()
    for _ in range(20):
        app.step(DT, [])
    if verbose:
        print(f"  {game_id:<18} state={result['state']:<10} score={result['score']:<8} "
              f"states={','.join(result['states'])}")
    return result


def run_screens(app: App, arcade: Arcade) -> None:
    controller = SimulatedController()
    app.replace_controller(controller)
    app.set_scene(arcade.launcher(), transition=False)
    for _ in range(30):
        app.step(DT, [])

    for scene in (ControllerTest(app), HowToPlay(app),
                  SettingsScene(app, lambda: None, lambda: None), CalibrationScene(app)):
        app.push_scene(scene, transition=False)
        controller.sweep(1, 0.0, 1.0, 0.6).sweep(2, 1.0, 0.0, 0.6).tap(3).tap(4)
        for _ in range(90):
            app.step(DT, [])
        app.pop_scene(transition=False)
        for _ in range(10):
            app.step(DT, [])
        print(f"  screen ok: {scene.name}")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Arduino Arcade smoke test")
    parser.add_argument("--seconds", type=float, default=8.0)
    parser.add_argument("--size", default="1280x720")
    parser.add_argument("--game", choices=sorted(GAMES))
    args = parser.parse_args(argv)
    width, height = (int(v) for v in args.size.lower().split("x"))

    app = build_app((width, height))
    arcade = Arcade(app)
    app.launcher_factory = arcade.launcher

    print(f"SMOKE TEST  {width}x{height}")
    print("screens:")
    run_screens(app, arcade)
    print("games:")
    games = [args.game] if args.game else sorted(GAMES)
    for game_id in games:
        run_game(app, game_id, args.seconds)
    app.shutdown()
    pygame.quit()
    print("ALL SMOKE TESTS PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
