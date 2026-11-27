import fractions
import socket
import threading
import time

import pytest

av = pytest.importorskip('av')
np = pytest.importorskip('numpy')

from juturna.components import State  # noqa: E402
from juturna.nodes import VideoRtp  # noqa: E402
from juturna.utils.net_utils import get_available_port  # noqa: E402


_FPS = 10


def _start(tmp_path, codec):
    port = get_available_port()
    node = VideoRtp(
        rec_host='127.0.0.1',
        rec_port=port,
        payload_type=96,
        codec=codec,
        encoding_clock_chan=90000,
        node_name='rtp',
        pipe_name='pipe',
    )
    node.pipe_path = str(tmp_path)
    node.link_state(State())
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

    raise TimeoutError(f'VideoRtp did not bind port {port}')


def _send(port, frames):
    # one keyframe at the start, as a sender does when the stream begins
    with av.open(f'rtp://127.0.0.1:{port}', 'w', format='rtp') as out:
        stream = out.add_stream('libvpx', rate=_FPS)
        stream.width, stream.height, stream.pix_fmt = 64, 48, 'yuv420p'
        stream.time_base = fractions.Fraction(1, _FPS)
        stream.codec_context.gop_size = 1000

        for i in range(frames):
            image = np.full((48, 64, 3), 10 * i % 256, dtype=np.uint8)
            frame = av.VideoFrame.from_ndarray(image, format='rgb24')
            frame.pts = i
            out.mux(stream.encode(frame))
            time.sleep(1 / _FPS)

        out.mux(stream.encode())


def _frames(node, expected, timeout=5):
    deadline = time.monotonic() + timeout

    while len(node.sent) < expected and time.monotonic() < deadline:
        time.sleep(0.1)

    return len(node.sent)


def test_every_frame_of_a_vp8_stream_is_transmitted(tmp_path):
    if 'libvpx' not in av.codecs_available:
        pytest.skip('PyAV has no libvpx encoder')

    node, port = _start(tmp_path, 'VP8')

    try:
        threading.Thread(target=_send, args=(port, 20)).start()

        # 'nobuffer' dropped the packets read while probing, and with them the
        # only keyframe; frame threading held the last frames back
        assert _frames(node, expected=20) == 20
    finally:
        node.stop()


def test_stop_without_traffic_is_quick(tmp_path):
    node, _ = _start(tmp_path, 'VP8')
    time.sleep(1)

    started = time.monotonic()
    node.stop()

    assert time.monotonic() - started < 4
