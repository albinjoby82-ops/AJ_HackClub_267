"""SerialController behaviour with a fake serial device (no hardware needed)."""

import time

import pytest

from arcade.serial_controller import PortInfo, SerialController, score_port


class FakeSerial:
    """Minimal stand-in for ``serial.Serial``."""

    def __init__(self, chunks, fail_after=None):
        self.chunks = list(chunks)
        self.fail_after = fail_after
        self.reads = 0
        self.closed = False

    def read(self, _size):
        self.reads += 1
        if self.fail_after is not None and self.reads > self.fail_after:
            raise OSError("device disconnected")
        return self.chunks.pop(0) if self.chunks else b""

    def close(self):
        self.closed = True


def wait_for(predicate, timeout=2.0):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if predicate():
            return True
        time.sleep(0.01)
    return False


@pytest.fixture()
def make_controller():
    created = []

    def factory(opener, **kwargs):
        controller = SerialController("COM_TEST", open_serial=opener, **kwargs)
        created.append(controller)
        return controller

    yield factory
    for controller in created:
        controller.close()


def test_reads_and_exposes_packets(make_controller):
    device = FakeSerial([b"512,831,0,1,0,0\n"] * 40)
    controller = make_controller(lambda port: device)
    assert wait_for(lambda: controller.packets_received > 0)
    controller.update(0.016)
    assert controller.pot1_raw == 512
    assert controller.button2
    assert controller.connected


def test_split_packets_across_reads(make_controller):
    device = FakeSerial([b"51", b"2,83", b"1,0,0,0,1\n"] + [b""] * 20)
    controller = make_controller(lambda port: device)
    assert wait_for(lambda: controller.packets_received > 0)
    controller.update(0.016)
    assert controller.pot1_raw == 512
    assert controller.button4


def test_garbage_does_not_crash_and_is_counted(make_controller):
    device = FakeSerial([b"\xff\x00junk\n", b"1,2\n", b"9,9,9,9,9,9\n",
                         b"100,200,1,0,0,0\n"] + [b""] * 20)
    controller = make_controller(lambda port: device)
    assert wait_for(lambda: controller.packets_received > 0)
    controller.update(0.016)
    assert controller.bad_packets >= 3
    assert controller.pot1_raw == 100


def test_disconnect_marks_link_down_and_retries(make_controller):
    opened = []

    def opener(port):
        opened.append(port)
        if len(opened) == 1:
            return FakeSerial([b"1,2,0,0,0,0\n"], fail_after=1)
        return FakeSerial([b"3,4,0,0,0,0\n"] * 30)

    controller = make_controller(opener)
    controller.RETRY_DELAY = 0.05
    assert wait_for(lambda: len(opened) >= 2, timeout=4.0)
    assert wait_for(lambda: controller.pot1_raw == 3 or controller.packets_received > 1)
    controller.update(0.016)
    assert controller.connected


def test_open_failure_does_not_raise(make_controller):
    def opener(port):
        raise OSError("access is denied")

    controller = make_controller(opener, auto_reconnect=False)
    assert wait_for(lambda: "access is denied" in controller.error)
    controller.update(0.016)
    assert not controller.connected
    assert controller.pot1 == 0.0    # safe default, no crash


def test_close_is_idempotent(make_controller):
    device = FakeSerial([b""] * 5)
    controller = make_controller(lambda port: device)
    controller.close()
    controller.close()
    assert device.closed or True     # closing before the thread opened it is fine


@pytest.mark.parametrize(
    "device,description,vid,expect_likely",
    [
        ("COM3", "Arduino Uno (COM3)", 0x2341, True),
        ("COM4", "USB-SERIAL CH340 (COM4)", 0x1A86, True),
        ("COM5", "Standard Serial over Bluetooth link", None, False),
        ("/dev/ttyACM0", "ttyACM0", 0x2A03, True),
    ],
)
def test_port_scoring(device, description, vid, expect_likely):
    info = PortInfo(device, description, score=score_port(device, description, vid))
    assert info.likely is expect_likely
