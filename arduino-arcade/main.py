"""ARDUINO ARCADE - entry point.

    python main.py                 auto-detect the Arduino, fall back to keyboard
    python main.py --keyboard      play without any hardware
    python main.py --event         fullscreen event/kiosk mode
    python main.py --port COM5     force a serial port
    python main.py --game twin_pong    jump straight into one game
    python main.py --list-ports    print detected serial ports and exit
"""

from __future__ import annotations

import argparse
import os
import sys

# Make sure the repo root is importable when launched from elsewhere.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pygame  # noqa: E402

from arcade.app import App  # noqa: E402
from arcade.keyboard_controller import KeyboardController  # noqa: E402
from arcade.scenes.calibration_scene import CalibrationScene  # noqa: E402
from arcade.scenes.controller_test import ControllerTest  # noqa: E402
from arcade.scenes.device_select import DeviceSelect  # noqa: E402
from arcade.scenes.howto import HowToPlay  # noqa: E402
from arcade.scenes.launcher import Launcher  # noqa: E402
from arcade.scenes.settings_scene import SettingsScene  # noqa: E402
from arcade.serial_controller import SERIAL_AVAILABLE, autodetect, list_serial_ports  # noqa: E402
from arcade.settings import Settings  # noqa: E402
from games import GAMES  # noqa: E402


def parse_args(argv=None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="arduino-arcade", description="Arduino Arcade")
    parser.add_argument("--keyboard", action="store_true", help="play without an Arduino")
    parser.add_argument("--event", action="store_true", help="fullscreen event mode")
    parser.add_argument("--port", default="", help="force a serial port, e.g. COM5")
    parser.add_argument("--game", choices=sorted(GAMES), help="launch straight into a game")
    parser.add_argument("--size", default="", help="window size, e.g. 1600x900")
    parser.add_argument("--no-audio", action="store_true", help="disable sound")
    parser.add_argument("--list-ports", action="store_true", help="list serial ports and exit")
    return parser.parse_args(argv)


def print_ports() -> int:
    if not SERIAL_AVAILABLE:
        print("pyserial is not installed - run: pip install -r requirements.txt")
        return 1
    ports = list_serial_ports()
    if not ports:
        print("No serial ports found.  Is the Arduino plugged in?")
        return 0
    print(f"{'PORT':<12} {'LIKELY':<8} DESCRIPTION")
    for port in ports:
        print(f"{port.device:<12} {'yes' if port.likely else '-':<8} {port.description}")
    return 0


def build_controller(settings: Settings, args: argparse.Namespace):
    """Returns (controller, needs_device_screen)."""
    if args.keyboard:
        return KeyboardController(), False
    if args.port:
        from arcade.serial_controller import SerialController

        return SerialController(args.port, settings.calibration), False
    if not SERIAL_AVAILABLE:
        return KeyboardController(), False
    controller, candidates = autodetect(settings.calibration, settings.get("preferred_port", ""))
    if controller is not None:
        return controller, False
    # Zero candidates -> keyboard and get playing; several -> let the user pick.
    return KeyboardController(), len(candidates) > 1


class Arcade:
    """Wires the launcher up to the games and utility screens."""

    def __init__(self, app: App):
        self.app = app

    def launcher(self) -> Launcher:
        return Launcher(self.app, self.launch_game, self.open_screen)

    def launch_game(self, game_id: str) -> None:
        game_class = GAMES.get(game_id)
        if game_class is None:
            self.app.toast(f"UNKNOWN GAME {game_id}")
            return
        self.app.push_scene(game_class(self.app))

    def open_screen(self, label: str) -> None:
        app = self.app
        if label == "CONTROLLER TEST":
            app.push_scene(ControllerTest(app))
        elif label == "CALIBRATION":
            app.push_scene(CalibrationScene(app))
        elif label == "SETTINGS":
            app.push_scene(SettingsScene(app, self.open_calibration, self.open_devices))
        elif label == "HOW TO PLAY":
            app.push_scene(HowToPlay(app))
        elif label == "EXIT":
            app.quit()

    def open_calibration(self) -> None:
        self.app.push_scene(CalibrationScene(self.app))

    def open_devices(self) -> None:
        self.app.push_scene(DeviceSelect(self.app))


def main(argv=None) -> int:
    args = parse_args(argv)
    if args.list_ports:
        return print_ports()

    settings = Settings()
    size = None
    if args.size:
        try:
            width, height = (int(v) for v in args.size.lower().split("x"))
            size = (width, height)
        except ValueError:
            print(f"Ignoring bad --size {args.size!r}; expected WIDTHxHEIGHT")

    pygame.init()
    controller, needs_device_screen = build_controller(settings, args)

    audio = None
    if args.no_audio:
        from arcade.audio import NullAudio

        audio = NullAudio()

    app = App(settings=settings, controller=controller, event_mode=args.event, audio=audio, size=size)
    if settings.load_error:
        app.toast(settings.load_error, duration=6.0)

    arcade = Arcade(app)
    app.set_scene(arcade.launcher(), transition=False)
    app.launcher_factory = arcade.launcher

    if args.game:
        arcade.launch_game(args.game)
    elif needs_device_screen and not args.keyboard:
        app.push_scene(DeviceSelect(app), transition=False)
    elif not settings.calibration.calibrated and controller.kind == "arduino":
        # First run with real hardware: calibrate before anything else.
        app.push_scene(CalibrationScene(app), transition=False)

    try:
        app.run()
    finally:
        app.shutdown()
        pygame.quit()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
