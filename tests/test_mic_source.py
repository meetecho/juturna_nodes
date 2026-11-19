import os

import numpy as np
import pytest

from juturna.nodes import MicSource


class _FakeStream:
    def read(self, frames):
        return np.full((frames, 1), 0.5, dtype=np.float32), False


def _mic(push_to_talk):
    node = MicSource(
        device='',
        sample_rate=10,
        block_size=0.5,
        push_to_talk=push_to_talk,
        trailing_silence=1.0,
        node_name='mic',
        pipe_name='pipe',
    )
    node._stream = _FakeStream()

    return node


def test_device_is_an_index_a_name_or_the_default():
    assert _mic(False)._device is None
    assert MicSource('3', 16000, 0.2, False, 1.0, node_name='m')._device == 3
    assert MicSource('USB', 16000, 0.2, False, 1.0, node_name='m')._device == (
        'USB'
    )


def test_without_push_to_talk_every_chunk_is_sent():
    node = _mic(push_to_talk=False)
    first, second = node._read_chunk(), node._read_chunk()

    assert first.payload.audio.tolist() == [0.5] * 5
    assert (first.payload.start, first.payload.end) == (0.0, 0.5)
    assert (second.payload.start, second.payload.end) == (0.5, 1.0)


def test_push_to_talk_sends_audio_only_while_on(capsys):
    node = _mic(push_to_talk=True)

    assert node._read_chunk() is None

    node.toggle()
    talking = node._read_chunk()
    node.toggle()
    silence = node._read_chunk()

    assert talking.payload.audio.tolist() == [0.5] * 5
    # turning push-to-talk off sends the trailing silence once
    assert silence.payload.audio.tolist() == [0.0] * 10
    assert (silence.payload.start, silence.payload.end) == (0.5, 1.5)
    assert node._read_chunk() is None
    assert 'listening' in capsys.readouterr().out


@pytest.mark.parametrize('pressed', [0, 2])
def test_even_presses_leave_push_to_talk_off(pressed, capsys):
    node = _mic(push_to_talk=True)

    for _ in range(pressed):
        node.toggle()

    assert not node._talking.is_set()


def test_push_to_talk_without_a_terminal_fails_the_warmup(monkeypatch):
    read_end, write_end = os.pipe()
    os.close(write_end)

    with os.fdopen(read_end) as pipe:
        monkeypatch.setattr('sys.stdin', pipe)

        with pytest.raises(ValueError, match='terminal'):
            _mic(push_to_talk=True).warmup()


def test_push_to_talk_listens_to_the_keyboard_after_a_restart(
    monkeypatch, capsys
):
    read_end, write_end = os.pipe()
    monkeypatch.setattr('sys.stdin', os.fdopen(read_end))
    node = _mic(push_to_talk=True)
    node._stream.start = node._stream.stop = lambda: None

    node.start()
    node.stop()
    node.start()

    try:
        assert node._keys.is_alive()
    finally:
        node.stop()
        os.close(write_end)
