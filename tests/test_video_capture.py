import threading
import time

import pytest

av = pytest.importorskip('av')
np = pytest.importorskip('numpy')

from juturna.nodes import VideoCapture  # noqa: E402


def _write(path, fps=10, frames=10, **options):
    """A video whose frame i is filled with the value 20 * i"""
    with av.open(str(path), 'w', options=options) as container:
        stream = container.add_stream('mpeg4', rate=fps)
        stream.width, stream.height, stream.pix_fmt = 32, 32, 'yuv420p'

        for i in range(frames):
            image = np.full((32, 32, 3), 20 * i % 256, dtype=np.uint8)
            frame = av.VideoFrame.from_ndarray(image, format='rgb24')
            container.mux(stream.encode(frame))

        container.mux(stream.encode())

    return path


@pytest.fixture(scope='module')
def video(tmp_path_factory):
    """A 1 s video at 10 fps"""
    return _write(tmp_path_factory.mktemp('video') / 'clip.mp4')


def _capture(source, loop=False, fps=0):
    node = VideoCapture(
        source=source, loop=loop, fps=fps, node_name='v', pipe_name='p'
    )
    node.warmup()

    return node


def _drain(node, limit=100):
    messages = list()

    for _ in range(limit):
        message = node._next_frame()

        if message is None:
            break

        messages.append(message)

    return messages


def test_file_frames_are_paced_in_real_time(video):
    node = _capture(video)
    start = time.monotonic()
    messages = _drain(node)
    elapsed = time.monotonic() - start

    assert [m.version for m in messages] == list(range(10))
    assert 0.8 <= elapsed < 2.0
    assert messages[0].payload.image.shape == (32, 32, 3)
    assert messages[0].payload.pixel_format == 'rgb24'
    assert [round(m.meta['pts'], 1) for m in messages[:3]] == [0.0, 0.1, 0.2]
    # the frames come in order: their grey level grows
    levels = [int(m.payload.image.mean()) for m in messages]
    assert levels == sorted(levels)


def test_end_of_file_stops_the_source(video):
    node = _capture(video)
    _drain(node)

    assert node._stop_source_event.is_set()
    assert node._container is None


def test_fps_drops_frames(video):
    messages = _drain(_capture(video, fps=2))

    assert [round(m.meta['pts'], 1) for m in messages] == [0.0, 0.5]


def test_loop_reads_the_file_again(video):
    node = _capture(video, loop=True)
    messages = _drain(node, limit=15)

    assert [m.version for m in messages] == list(range(15))
    assert round(messages[10].meta['pts'], 1) == 1.0
    assert not node._stop_source_event.is_set()


def test_missing_file_fails_at_warmup(tmp_path):
    with pytest.raises(FileNotFoundError):
        _capture(tmp_path / 'nope.mp4')


def test_missing_camera_raises_for_the_source_backoff():
    node = _capture('99')

    with pytest.raises((OSError, av.error.FFmpegError)):
        node._next_frame()

    assert node._container is None


def test_file_starting_late_is_counted_from_its_first_frame(tmp_path):
    # an MPEG-TS file whose timestamps start 30 s in
    path = _write(tmp_path / 'late.ts', output_ts_offset='30')
    node = _capture(path)
    start = time.monotonic()
    messages = _drain(node)

    assert time.monotonic() - start < 2.0
    assert len(messages) == 10
    assert round(messages[0].meta['pts'], 1) == 0.0


def test_fps_keeps_frames_on_the_boundary(tmp_path):
    # at 30 fps a 10 fps cap keeps every third frame, despite float rounding
    path = _write(tmp_path / 'fast.mp4', fps=30, frames=30)

    assert len(_drain(_capture(path, fps=10))) == 10


def test_corrupt_and_empty_camera_packets_are_skipped():
    class Packet:
        def __init__(self, frames, size=1):
            self.frames = frames
            self.size = size

        def decode(self):
            if self.size == 0:
                raise av.error.ArgumentError(22, 'avcodec_send_packet()')

            if self.frames is None:
                raise av.error.InvalidDataError(1094995529, 'corrupt')

            return self.frames

    class Container:
        def demux(self, stream):
            # a reopened V4L2 device starts with an empty packet
            packets = [Packet([], size=0), Packet(['a']), Packet(None)]

            return iter([*packets, Packet(['b'])])

    node = _capture('0')
    node._container = Container()

    assert list(node._decoded(None)) == ['a', 'b']


def test_loop_on_a_file_without_frames_fails(video, monkeypatch):
    class Container:
        def close(self):
            pass

    def empty_open():
        node._container = Container()
        node._frames = iter(())
        node._opened_at = node._sent

    node = _capture(video, loop=True)
    monkeypatch.setattr(node, '_open', empty_open)

    with pytest.raises(OSError, match='no frames'):
        node._next_frame()


def test_destroy_leaves_a_running_read_to_close_the_source(video):
    # kill() left the source thread behind, blocked in a read
    release = threading.Event()
    closed = list()

    class Container:
        def close(self):
            closed.append(threading.current_thread().name)

    def blocked_frames():
        release.wait(5)
        yield 'frame'

    node = _capture(video)
    node._container, node._frames = Container(), blocked_frames()
    reader = threading.Thread(target=node._next_frame, name='reader')
    reader.start()
    node._reader = reader
    node._stop_source_event.set()

    node.destroy()

    assert closed == list()

    release.set()
    reader.join(5)

    assert closed == ['reader']
    assert node._container is None


def test_destroy_closes_the_source_once_the_reader_is_gone(video):
    node = _capture(video)
    node._next_frame()
    node._reader = threading.Thread(target=lambda: None)

    node.destroy()

    assert node._container is None


def test_start_keeps_the_source_thread_for_destroy(video):
    node = _capture(video)
    node.start()

    assert node._reader is not None
    assert node._reader.is_alive()

    node.kill()
    node._reader.join(5)
    node.destroy()

    assert node._container is None


def test_restart_after_a_pause_resumes_in_real_time(video):
    received = list()

    class Sink:
        name = 's'

        def put(self, message):
            received.append((time.monotonic(), message.meta['pts']))

    def wait_for(count):
        deadline = time.monotonic() + 5

        while len(received) < count and time.monotonic() < deadline:
            time.sleep(0.01)

    node = _capture(video)
    node.add_destination('s', Sink())
    node.start()
    wait_for(3)
    node.stop()  # the source is waiting for the pace of the next frame
    time.sleep(0.5)  # the pause, 5 frames long

    restarted = time.monotonic()
    node.start()
    wait_for(10)
    node.stop()

    pts = [round(p, 1) for _, p in received]
    assert pts == [round(0.1 * i, 1) for i in range(10)]
    # the frames of the pause are not sent in a burst at the restart
    burst = [t for t, _ in received if restarted <= t < restarted + 0.25]
    assert len(burst) <= 3
