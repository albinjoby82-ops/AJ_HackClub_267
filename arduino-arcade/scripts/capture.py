"""Render screens to PNG files so visuals can be reviewed without a display.

    python scripts/capture.py --out build/shots
"""

from __future__ import annotations

import argparse
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame  # noqa: E402

from arcade.game import PLAYING  # noqa: E402
from arcade.scenes.calibration_scene import CalibrationScene  # noqa: E402
from arcade.scenes.controller_test import ControllerTest  # noqa: E402
from arcade.scenes.howto import HowToPlay  # noqa: E402
from arcade.scenes.settings_scene import SettingsScene  # noqa: E402
from arcade.simulated_controller import SimulatedController  # noqa: E402
from games import GAMES  # noqa: E402
from main import Arcade  # noqa: E402
from scripts.smoke_test import DT, build_app, script_controller  # noqa: E402


def save(app, path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    pygame.image.save(app.screen, path)
    print("wrote", path)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="build/shots")
    parser.add_argument("--size", default="1280x720")
    parser.add_argument("--seconds", type=float, default=6.0)
    args = parser.parse_args(argv)
    width, height = (int(v) for v in args.size.lower().split("x"))

    app = build_app((width, height))
    arcade = Arcade(app)
    app.launcher_factory = arcade.launcher
    controller = SimulatedController()
    app.replace_controller(controller)

    app.set_scene(arcade.launcher(), transition=False)
    for _ in range(20):
        app.step(DT, [])
    save(app, os.path.join(args.out, "launcher.png"))

    for scene, name in ((ControllerTest(app), "controller_test"),
                        (HowToPlay(app), "how_to_play"),
                        (SettingsScene(app, lambda: None, lambda: None), "settings"),
                        (CalibrationScene(app), "calibration")):
        app.push_scene(scene, transition=False)
        controller.sweep(1, 0.2, 0.8, 0.5).sweep(2, 0.8, 0.3, 0.5)
        for _ in range(40):
            app.step(DT, [])
        save(app, os.path.join(args.out, f"{name}.png"))
        app.pop_scene(transition=False)
        app.step(DT, [])

    for game_id, game_class in sorted(GAMES.items()):
        controller = SimulatedController()
        app.replace_controller(controller)
        game = game_class(app)
        app.set_scene(game, transition=False)
        for _ in range(20):
            app.step(DT, [])
        save(app, os.path.join(args.out, f"{game_id}_intro.png"))
        game.start_countdown()
        game.set_state(PLAYING)
        script_controller(controller)
        for _ in range(int(args.seconds / DT)):
            app.step(DT, [])
            if controller.script_finished:
                script_controller(controller)
        save(app, os.path.join(args.out, f"{game_id}_play.png"))
        game.game_over("SMOKE TEST")
        for _ in range(40):
            app.step(DT, [])
        save(app, os.path.join(args.out, f"{game_id}_over.png"))

    app.shutdown()
    pygame.quit()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
