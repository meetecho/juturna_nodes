import types

import numpy as np

from juturna.components import Message
from juturna.nodes import SpeakerSink
from juturna.payloads import AudioPayload


def test_audio_is_played_clipped_and_blocking():
    played = list()
    node = SpeakerSink(device='', node_name='speaker', pipe_name='pipe')
    node._sounddevice = types.SimpleNamespace(
        play=lambda audio, **kwargs: played.append((audio.tolist(), kwargs))
    )

    audio = np.asarray([0.5, 2.0, -3.0], dtype=np.float32)
    node.update(Message(payload=AudioPayload(audio=audio, sampling_rate=24000)))

    assert played == [
        (
            [0.5, 1.0, -1.0],
            {'samplerate': 24000, 'device': None, 'blocking': True},
        )
    ]
