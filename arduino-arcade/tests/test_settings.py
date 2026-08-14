"""Settings persistence, corruption recovery and high scores."""

import json
import os

from arcade.calibration import Calibration, PotCalibration
from arcade.settings import DEFAULTS, Settings


def test_missing_file_uses_defaults(settings_path):
    settings = Settings(settings_path)
    assert settings.get("volume") == DEFAULTS["volume"]
    assert settings.load_error == ""


def test_values_persist_across_instances(settings_path):
    settings = Settings(settings_path)
    settings.set("volume", 0.3)
    settings.set("fullscreen", True)
    settings.set("preferred_port", "COM7")

    reloaded = Settings(settings_path)
    assert reloaded.get("volume") == 0.3
    assert reloaded.get("fullscreen") is True
    assert reloaded.get("preferred_port") == "COM7"


def test_corrupt_json_recovers_with_defaults(settings_path):
    with open(settings_path, "w", encoding="utf-8") as handle:
        handle.write("{ this is not json ")
    settings = Settings(settings_path)
    assert settings.load_error
    assert settings.get("volume") == DEFAULTS["volume"]
    assert os.path.exists(settings_path + ".corrupt")
    assert settings.save()


def test_non_object_json_recovers(settings_path):
    with open(settings_path, "w", encoding="utf-8") as handle:
        json.dump([1, 2, 3], handle)
    settings = Settings(settings_path)
    assert settings.load_error
    assert settings.get("volume") == DEFAULTS["volume"]


def test_wrong_types_are_coerced(settings_path):
    with open(settings_path, "w", encoding="utf-8") as handle:
        json.dump({"volume": "loud", "window_size": "big", "high_scores": "none",
                   "muted": "yes", "preferred_port": 5}, handle)
    settings = Settings(settings_path)
    assert settings.get("volume") == DEFAULTS["volume"]
    assert settings.get("window_size") == DEFAULTS["window_size"]
    assert settings.get("high_scores") == {}
    assert settings.get("preferred_port") == ""


def test_volume_is_clamped(settings_path):
    settings = Settings(settings_path)
    settings.set("volume", 4.5)
    assert settings.get("volume") == 1.0
    settings.set("volume", -2)
    assert settings.get("volume") == 0.0


def test_high_scores(settings_path):
    settings = Settings(settings_path)
    assert settings.high_score("neon_drift") == 0
    assert settings.submit_score("neon_drift", 1200)
    assert not settings.submit_score("neon_drift", 900)
    assert settings.submit_score("neon_drift", 1500)
    assert Settings(settings_path).high_score("neon_drift") == 1500


def test_calibration_round_trip(settings_path):
    settings = Settings(settings_path)
    settings.calibration = Calibration(pot1=PotCalibration(120, 880), calibrated=True)
    reloaded = Settings(settings_path)
    assert reloaded.calibration.calibrated
    assert reloaded.calibration.pot1.low == 120


def test_unknown_keys_are_ignored(settings_path):
    with open(settings_path, "w", encoding="utf-8") as handle:
        json.dump({"volume": 0.5, "hack": "the planet"}, handle)
    settings = Settings(settings_path)
    assert settings.get("volume") == 0.5
    assert "hack" not in settings.data
