import time
import types

import numpy as np

from juturna.components import Message
from juturna.nodes import SpeakerSink
from juturna.payloads import AudioPayload


def _fake_sounddevice(calls):
    return types.SimpleNamespace(
        play=lambda audio, **kwargs: calls.append(('play', audio.tolist())),
        stop=lambda: calls.append(('stop',)),
        wait=lambda: calls.append(('wait',)),
    )


def _audio(samples, rate=1000):
    audio = np.zeros(samples, dtype=np.float32)

    return Message(payload=AudioPayload(audio=audio, sampling_rate=rate))


def _wait_for(condition):
    deadline = time.monotonic() + 5

    while not condition() and time.monotonic() < deadline:
        time.sleep(0.01)


def test_audio_is_played_clipped_until_it_ends():
    calls = list()
    node = SpeakerSink(device='', node_name='speaker', pipe_name='pipe')
    node._sounddevice = _fake_sounddevice(calls)

    audio = np.asarray([0.5, 2.0, -3.0], dtype=np.float32)
    node.update(Message(payload=AudioPayload(audio=audio, sampling_rate=24000)))

    assert calls == [('play', [0.5, 1.0, -1.0]), ('wait',)]


def test_stop_cuts_the_audio_and_drops_the_queue_then_restart_plays():
    calls = list()
    node = SpeakerSink(device='', node_name='speaker', pipe_name='pipe')
    node._sounddevice = _fake_sounddevice(calls)

    node.start()
    node.put(_audio(10_000))  # 10 s
    node.put(_audio(10_000))  # queued behind it
    _wait_for(lambda: calls)

    started = time.monotonic()
    node.stop()

    assert time.monotonic() - started < 1
    assert [c[0] for c in calls] == ['play', 'stop']

    node.start()
    node.put(_audio(10))
    _wait_for(lambda: len(calls) == 4)
    node.stop()

    assert [c[0] for c in calls] == ['play', 'stop', 'play', 'wait']
