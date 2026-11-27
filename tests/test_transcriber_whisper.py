import numpy as np
import pytest

pytest.importorskip('faster_whisper')

from juturna.components import Message  # noqa: E402
from juturna.components._state import State  # noqa: E402
from juturna.payloads import AudioPayload  # noqa: E402
from juturna.remotizer.utils import to_typed_value  # noqa: E402

from juturna.nodes._transcriber_whisper import transcriber_whisper  # noqa: E402


class _StubModel:
    def __init__(self, *args, **kwargs):
        self.lengths = list()

    def transcribe(self, speech, **kwargs):
        self.lengths.append(len(speech))

        return [], None


class _Sink:
    def __init__(self, sent):
        self.put = sent.append


def test_buffers_messages_of_any_creator_without_origins(monkeypatch):
    monkeypatch.setattr(transcriber_whisper, 'WhisperModel', _StubModel)

    node = transcriber_whisper.TranscriberWhisper(
        model_name='tiny',
        only_local=True,
        language='en',
        task='transcribe',
        buffer_size=2,
        device='cpu',
        node_name='trx',
        pipe_name='pipe',
    )
    sent = list()
    node.add_destination('sink', _Sink(sent))

    # built alone, as the remote service does: no origins
    node.warmup()
    state = State()

    for version in range(3):
        node.update(
            Message[AudioPayload](
                creator='not_an_origin',
                version=version,
                payload=AudioPayload(
                    audio=np.zeros(100, dtype=np.float32),
                    sampling_rate=16000,
                    start=float(version),
                ),
            ),
            state=state,
        )

    assert [m.payload['transcript'] for m in sent] == [[], [], []]
    assert [m.meta['origin'] for m in sent] == ['not_an_origin'] * 3
    # the buffer keeps the last buffer_size messages
    assert node._model.lengths == [100, 200, 200]
    # a remote service sends the state: it must hold no unsendable type
    assert to_typed_value(dict(state)) is not None

    silence = Message[AudioPayload](
        creator='not_an_origin',
        payload=AudioPayload(audio=np.zeros(0, dtype=np.float32)),
    )
    silence.meta['silence'] = True
    node.update(silence, state=state)

    assert 'not_an_origin' not in state
    assert sent[-1].payload['transcript'] == []
