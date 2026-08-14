"""Serial packet parsing and the packet-level robustness guarantees."""

import pytest

from arcade.controller import parse_packet


def test_valid_packet():
    state = parse_packet("512,831,0,1,0,0")
    assert state is not None
    assert state.pot1 == 512
    assert state.pot2 == 831
    assert state.buttons == [False, True, False, False]


def test_packet_with_newline_and_carriage_return():
    assert parse_packet("0,1023,1,1,1,1\r\n").buttons == [True] * 4


def test_bytes_packet():
    assert parse_packet(b"100,200,0,0,0,0").pot1 == 100


@pytest.mark.parametrize(
    "line",
    [
        "",
        "   ",
        "512,831,0,1,0",              # too few fields
        "512,831,0,1,0,0,1",          # too many fields
        "512,831,0,1,0,x",            # non-numeric
        "1024,0,0,0,0,0",             # pot out of range
        "-5,0,0,0,0,0",               # negative pot
        "512,831,0,2,0,0",            # button not 0/1
        "31,0,0,0",                   # truncated mid-stream
        "\x00\xff garbage",           # boot garbage
        "512;831;0;1;0;0",            # wrong separator
        None,
        12345,
    ],
)
def test_malformed_packets_return_none(line):
    assert parse_packet(line) is None


def test_partial_line_then_valid_line():
    """A torn packet is dropped; the next whole packet still parses."""
    assert parse_packet("512,83") is None
    assert parse_packet("512,831,0,0,0,0") is not None


def test_whitespace_tolerated():
    assert parse_packet(" 12 , 34 , 0 , 0 , 1 , 0 ").buttons[2] is True
