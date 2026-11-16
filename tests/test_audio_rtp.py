import socket
import struct
import time

import numpy as np
import pytest

pytest.importorskip('av')

from juturna.nodes import AudioRtp  # noqa: E402
from juturna.utils.net_utils import get_available_port  # noqa: E402


_PACKET_SAMPLES = 160  # 20 ms of PCMU at 8 kHz
# a 1 kHz square wave in mu-law: 0x00 and 0x80 are the loudest values
_TONE = (b'\x00' * 4 + b'\x80' * 4) * (_PACKET_SAMPLES // 8)


def _start(tmp_path):
    port = get_available_port()
    node = AudioRtp(
        host='127.0.0.1',
        port=port,
        payload_type=0,
        encoding_clock_chan='PCMU/8000',
        out_rate=16000,
        out_channels=1,
        resampler_format='flt',
        block_size=1,
        flush_partial_on_error=True,
        node_name='rtp',
        pipe_name='pipe',
    )
    node.pipe_path = str(tmp_path)
    node.sent = list()
    node.transmit = node.sent.append
    node.warmup()
    node.start()

    _wait_until_bound(port)

    return node, port


def _wait_until_bound(port):
    deadline = time.monotonic() + 5

    while time.monotonic() < deadline:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as probe:
            try:
                probe.bind(('127.0.0.1', port))
            except OSError:
                return

        time.sleep(0.05)

    raise TimeoutError(f'AudioRtp did not bind port {port}')


def _send(port, seconds, burst):
    # the first `burst` seconds are sent at once, the rest in real time
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        for seq in range(int(seconds * 50)):
            header = struct.pack(
                '!BBHII', 0x80, 0, seq, seq * _PACKET_SAMPLES, 0x1234
            )
            sock.sendto(header + _TONE, ('127.0.0.1', port))

            if seq >= burst * 50:
                time.sleep(0.02)


def _tone_seconds(node, expected, timeout=10):
    # the last partial block is flushed when no packet arrives for a while
    deadline = time.monotonic() + timeout

    while time.monotonic() < deadline:
        audio = np.concatenate(
            [m.payload.audio for m in node.sent] or [np.zeros(0)]
        )
        windows = audio[: audio.size // 160 * 160].reshape(-1, 160)
        # 10 ms windows that carry the tone
        seconds = np.count_nonzero(np.sqrt((windows**2).mean(axis=1)) > 0.1)
        seconds /= 100

        if seconds >= expected:
            break

        time.sleep(0.1)

    return seconds


def test_first_packet_is_kept(tmp_path):
    node, port = _start(tmp_path)

    try:
        _send(port, seconds=1, burst=0)

        assert _tone_seconds(node, expected=1) >= 0.99
    finally:
        node.stop()


def test_burst_of_packets_is_received_whole(tmp_path):
    node, port = _start(tmp_path)

    try:
        _send(port, seconds=2, burst=2)

        assert _tone_seconds(node, expected=2) >= 1.98
    finally:
        node.stop()
