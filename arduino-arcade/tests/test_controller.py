"""Controller API: normalisation, smoothing and button edge detection."""

from arcade.calibration import Calibration, PotCalibration
from arcade.controller import Controller, RawState
from arcade.simulated_controller import SimulatedController


class FakeController(Controller):
    """Backend that replays a fixed list of raw states."""

    kind = "fake"

    def __init__(self, states, calibration=None):
        super().__init__(calibration, smoothing=0.0)
        self.states = list(states)

    def _poll(self, dt, events):
        return self.states.pop(0) if self.states else None


def test_button_edges():
    states = [
        RawState(0, 0, [False] * 4),
        RawState(0, 0, [True, False, False, False]),
        RawState(0, 0, [True, False, False, False]),
        RawState(0, 0, [False, False, False, False]),
    ]
    controller = FakeController(states)

    controller.update(0.016)
    assert not controller.button1 and not controller.button1_pressed

    controller.update(0.016)
    assert controller.button1 and controller.button1_pressed and not controller.button1_released

    controller.update(0.016)   # still held: no new press edge
    assert controller.button1 and not controller.button1_pressed

    controller.update(0.016)
    assert not controller.button1 and controller.button1_released


def test_named_button_properties_cover_all_four():
    controller = FakeController([RawState(0, 0, [False, True, False, True])])
    controller.update(0.016)
    assert (controller.button1, controller.button2, controller.button3, controller.button4) == (
        False, True, False, True)
    assert controller.button2_pressed and controller.button4_pressed


def test_reset_edges_swallows_pending_presses():
    controller = FakeController([RawState(0, 0, [True, False, False, False])])
    controller.update(0.016)
    assert controller.button1_pressed
    controller.reset_edges()
    assert not controller.button1_pressed


def test_normalisation_uses_calibration():
    cal = Calibration(pot1=PotCalibration(low=100, high=900, dead_zone=0.0),
                      pot2=PotCalibration(dead_zone=0.0))
    controller = FakeController([RawState(500, 0, [False] * 4)], cal)
    controller.update(0.016)
    assert abs(controller.pot1 - 0.5) < 0.01
    assert controller.pot1_raw == 500


def test_inverted_pot():
    cal = Calibration(pot1=PotCalibration(low=0, high=1023, invert=True, dead_zone=0.0))
    controller = FakeController([RawState(0, 0, [False] * 4)], cal)
    controller.update(0.016)
    assert controller.pot1 == 1.0


def test_values_are_clamped_outside_calibrated_range():
    cal = Calibration(pot1=PotCalibration(low=200, high=800, dead_zone=0.0))
    controller = FakeController([RawState(1023, 0, [False] * 4), RawState(0, 0, [False] * 4)], cal)
    controller.update(0.016)
    assert controller.pot1 == 1.0
    controller.update(0.016)
    assert controller.pot1 == 0.0


def test_smoothing_converges_without_overshoot():
    states = [RawState(1023, 1023, [False] * 4) for _ in range(120)]
    controller = FakeController(states)
    controller.smoothing = 0.5
    for _ in range(120):
        controller.update(1 / 60.0)
        assert 0.0 <= controller.pot1 <= 1.0
    assert controller.pot1 > 0.99


def test_stale_state_is_reused_when_backend_returns_none():
    controller = FakeController([RawState(700, 300, [True, False, False, False])])
    controller.update(0.016)
    controller.update(0.016)      # no new packet
    assert controller.pot1_raw == 700
    assert not controller.button1_pressed   # no repeated press edge


def test_simulated_controller_script():
    controller = SimulatedController()
    controller.sweep(1, 0.0, 1.0, 1.0).tap(2)
    pressed = released = False
    for _ in range(80):
        controller.update(1 / 60.0)
        pressed = pressed or controller.button2_pressed
        released = released or controller.button2_released
    assert controller.pot1 > 0.9
    assert pressed and released
    assert controller.script_finished


def test_simulated_controller_accepts_raw_packets():
    controller = SimulatedController()
    assert controller.feed_packet("512,1023,0,0,1,0")
    controller.update(0.016)
    assert controller.pot2 == 1.0
    assert controller.button3
    assert not controller.feed_packet("nonsense")
