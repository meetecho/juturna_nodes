import wave

import numpy as np

from juturna.components import Message
from juturna.nodes import AudioWriter
from juturna.payloads import AudioPayload


def _writer(folder):
    node = AudioWriter(file_name='out.wav', node_name='w', pipe_name='p')
    node.pipe_path = str(folder)

    return node


def _audio(samples, rate, channels=-1):
    return Message(
        payload=AudioPayload(
            audio=np.asarray(samples, dtype=np.float32),
            sampling_rate=rate,
            channels=channels,
        )
    )


def test_messages_are_appended_to_one_file(tmp_path):
    node = _writer(tmp_path)
    node.update(_audio([0.0, 0.5], 8000))
    node.update(_audio([-0.5, 2.0], 8000))
    node.destroy()

    with wave.open(str(tmp_path / 'out.wav')) as f:
        assert (f.getnchannels(), f.getsampwidth(), f.getframerate()) == (
            1,
            2,
            8000,
        )
        frames = np.frombuffer(f.readframes(f.getnframes()), dtype='<i2')

    # values outside [-1, 1] are clipped
    assert frames.tolist() == [0, 16383, -16383, 32767]


def test_message_with_another_rate_is_dropped(tmp_path):
    node = _writer(tmp_path)
    node.update(_audio([0.5], 8000))
    node.update(_audio([0.5, 0.5], 16000))
    node.destroy()

    with wave.open(str(tmp_path / 'out.wav')) as f:
        assert f.getnframes() == 1


def test_stereo_message_is_dropped(tmp_path):
    node = _writer(tmp_path)
    node.update(_audio([0.5], 8000, channels=1))
    node.update(_audio([0.5, 0.5], 8000, channels=2))
    node.destroy()

    with wave.open(str(tmp_path / 'out.wav')) as f:
        assert f.getnframes() == 1


def test_destroy_without_messages_creates_no_file(tmp_path):
    _writer(tmp_path).destroy()

    assert not (tmp_path / 'out.wav').exists()
