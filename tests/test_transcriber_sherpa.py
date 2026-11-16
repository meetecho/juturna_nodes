import os
import pathlib
import wave

import numpy as np
import pytest

from juturna.components import Message
from juturna.nodes import TranscriberSherpa
from juturna.nodes._transcriber_sherpa.transcriber_sherpa import _words
from juturna.payloads import AudioPayload


def test_tokens_are_joined_into_words_with_absolute_times():
    words = _words([' HEL', 'LO', ' WORLD'], [0.5, 0.6, 1.0], offset=10.0)

    assert words == [
        {'word': ' hello', 'start': 10.5, 'end': 11.0},
        {'word': ' world', 'start': 11.0, 'end': 11.0},
    ]


def test_no_tokens_give_no_words():
    assert _words([], [], offset=0.0) == []


# end to end on a real model: set JT_TEST_SHERPA_STT to its folder
_MODEL = os.environ.get('JT_TEST_SHERPA_STT')


@pytest.mark.skipif(not _MODEL, reason='JT_TEST_SHERPA_STT is not set')
def test_sentence_is_transmitted_after_trailing_silence():
    pytest.importorskip('sherpa_onnx')

    with wave.open(str(pathlib.Path(_MODEL) / 'test_wavs' / '0.wav')) as f:
        rate = f.getframerate()
        audio = np.frombuffer(f.readframes(f.getnframes()), dtype=np.int16)

    audio = np.concatenate(
        [audio.astype(np.float32) / 32768, np.zeros(rate * 2, np.float32)]
    )

    node = TranscriberSherpa(
        model='',
        model_dir=_MODEL,
        num_threads=2,
        min_trailing_silence=0.8,
        node_name='stt',
        pipe_name='pipe',
    )
    sent = list()
    node.transmit = sent.append
    node.warmup()

    for i in range(0, len(audio), rate // 5):
        chunk = audio[i : i + rate // 5]
        node.update(
            Message(payload=AudioPayload(audio=chunk, sampling_rate=rate))
        )

    node.destroy()

    assert len(sent) == 1
    assert sent[0].payload['text'].startswith('after early nightfall')
    assert sent[0].payload['transcript'][0]['word'] == ' after'
