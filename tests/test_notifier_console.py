import numpy as np

from juturna.components import Message
from juturna.nodes import NotifierConsole
from juturna.payloads import AudioPayload, ObjectPayload


def _console():
    return NotifierConsole(node_name='console', pipe_name='pipe')


def _send(node, payload):
    node.update(Message(creator='whisper', payload=payload))


def test_transcript_is_printed_as_text(capsys):
    words = [{'word': ' Hello', 'start': 0.0}, {'word': ' world.', 'end': 1.0}]
    _send(_console(), ObjectPayload.from_dict({'transcript': words}))

    assert capsys.readouterr().out == '[whisper] Hello world.\n'


def test_empty_transcript_prints_nothing(capsys):
    _send(_console(), ObjectPayload.from_dict({'transcript': []}))

    assert capsys.readouterr().out == ''


def test_text_field_is_printed_as_is(capsys):
    payload = ObjectPayload.from_dict({'prompt': 'Hi?', 'text': ' Hello. '})
    _send(_console(), payload)

    assert capsys.readouterr().out == '[whisper] Hello.\n'


def test_other_objects_are_printed_as_compact_json(capsys):
    _send(_console(), ObjectPayload.from_dict({'label': 'cat', 'score': 0.9}))

    assert capsys.readouterr().out == '[whisper] {"label":"cat","score":0.9}\n'


def test_other_payloads_print_their_type(capsys):
    audio = AudioPayload(
        audio=np.zeros(4, dtype=np.float32), sampling_rate=16000
    )
    _send(_console(), audio)

    assert capsys.readouterr().out == '[whisper] <AudioPayload>\n'
