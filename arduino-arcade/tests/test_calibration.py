"""Calibration recording, sanitising and round-tripping."""

from arcade.calibration import Calibration, CalibrationRecorder, PotCalibration


def test_default_calibration_is_identity():
    pot = PotCalibration(dead_zone=0.0)
    assert pot.normalize(0) == 0.0
    assert pot.normalize(1023) == 1.0
    assert abs(pot.normalize(512) - 0.5) < 0.01


def test_dead_zone_lets_cheap_pots_reach_the_ends():
    pot = PotCalibration(dead_zone=0.05)
    assert pot.normalize(30) == 0.0
    assert pot.normalize(1000) == 1.0


def test_too_narrow_span_falls_back_to_full_range():
    pot = PotCalibration(low=500, high=505)
    pot.sanitize()
    assert (pot.low, pot.high) == (0, 1023)


def test_out_of_order_range_is_repaired():
    pot = PotCalibration(low=900, high=100)
    pot.sanitize()
    assert pot.low < pot.high


def test_recorder_tracks_extremes_and_completion():
    recorder = CalibrationRecorder(required_span=300)
    assert not recorder.complete
    for value in range(120, 900, 20):
        recorder.feed(value, 1023 - value)
    assert recorder.complete
    assert recorder.progress(1) == 1.0

    calibration = recorder.build()
    assert calibration.calibrated
    assert calibration.pot1.low >= 120
    assert calibration.pot1.high <= 900
    # The recorded extremes should map close to the ends of the range.
    assert calibration.normalize(1, 890) > 0.9
    assert calibration.normalize(1, 130) < 0.1


def test_recorder_build_can_invert():
    recorder = CalibrationRecorder()
    for value in range(0, 1024, 16):
        recorder.feed(value, value)
    calibration = recorder.build(invert1=True)
    assert calibration.pot1.invert
    assert calibration.normalize(1, 0) > 0.9


def test_round_trip_through_dict():
    original = Calibration(pot1=PotCalibration(50, 950, True, 0.04), calibrated=True)
    restored = Calibration.from_dict(original.to_dict())
    assert restored.pot1.low == 50
    assert restored.pot1.invert
    assert restored.calibrated


def test_from_dict_survives_garbage():
    for payload in (None, [], {"pot1": "nope"}, {"pot1": {"low": "x"}}):
        calibration = Calibration.from_dict(payload)
        assert 0.0 <= calibration.normalize(1, 512) <= 1.0
