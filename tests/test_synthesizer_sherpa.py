import os
import types

import pytest

from juturna.components import Message
from juturna.nodes import SynthesizerSherpa
from juturna.payloads import ObjectPayload


def _synthesizer(model_dir='', model_type='kitten', lexicon=''):
    node = SynthesizerSherpa(
        model_dir=model_dir,
        model_type=model_type,
        lexicon=lexicon,
        speaker_id=0,
        speed=1.0,
        num_threads=2,
        node_name='tts',
        pipe_name='pipe',
    )
    node.sent = list()
    node.transmit = node.sent.append

    return node


def _say(node, text):
    node.update(
        Message(creator='llm', payload=ObjectPayload.from_dict({'text': text}))
    )


class _FakeTts:
    def __init__(self, samples):
        self.samples = samples
        self.calls = list()

    def generate(self, text, sid, speed):
        self.calls.append(text)

        return types.SimpleNamespace(samples=self.samples, sample_rate=4)


def test_unknown_model_type_is_rejected():
    with pytest.raises(ValueError, match='model_type'):
        _synthesizer(model_type='piper')


def test_text_becomes_an_audio_message():
    node = _synthesizer()
    node._tts = _FakeTts([0.0, 0.5, -0.5, 0.0, 0.25, 0.0, 0.0, 0.0])

    _say(node, ' Rome is the capital. ')

    payload = node.sent[0].payload
    assert node._tts.calls == ['Rome is the capital.']
    assert payload.sampling_rate == 4
    assert payload.audio.dtype.name == 'float32'
    assert (payload.start, payload.end) == (0.0, 2.0)
    assert node.sent[0].meta['text'] == 'Rome is the capital.'


def test_empty_text_or_audio_transmits_nothing():
    node = _synthesizer()
    node._tts = _FakeTts([])

    _say(node, '')
    _say(node, 'Juturna')

    assert node._tts.calls == ['Juturna']
    assert node.sent == []


# end to end on a real model: set JT_TEST_SHERPA_TTS to the model folder and
# JT_TEST_SHERPA_LEXICON to the lexicon file
_MODEL = os.environ.get('JT_TEST_SHERPA_TTS')
_LEXICON = os.environ.get('JT_TEST_SHERPA_LEXICON', '')


@pytest.mark.skipif(not _MODEL, reason='JT_TEST_SHERPA_TTS is not set')
def test_real_model_speaks():
    pytest.importorskip('sherpa_onnx')

    node = _synthesizer(model_dir=_MODEL, lexicon=_LEXICON)
    node.warmup()
    _say(node, 'The capital of Italy is Rome.')
    node.destroy()

    payload = node.sent[0].payload
    assert payload.sampling_rate > 0
    assert 1.0 < payload.end < 5.0
    assert abs(payload.audio).max() > 0.01
