import json

import numpy as np

from juturna.components import Message
from juturna.components._state import State
from juturna.nodes import DetectionEvents
from juturna.payloads import ImagePayload


def _node(interval=1.0):
    node = DetectionEvents(interval=interval, node_name='e', pipe_name='p')
    sent = list()
    node.transmit = sent.append

    return node, sent


def _frame(version, timestamp, detections):
    message = Message[ImagePayload](
        creator='detector',
        version=version,
        payload=ImagePayload(
            image=np.zeros((48, 64, 3), dtype=np.uint8),
            width=64,
            height=48,
            depth=3,
            pixel_format='rgb24',
            timestamp=timestamp,
        ),
    )
    message.meta['detections'] = detections
    # frozen like a transmitted message: meta lists become tuples
    message._freeze()

    return message


_PERSON = {'label': 'person', 'confidence': 0.9, 'bbox': [1, 2, 30, 40]}
_DOG = {'label': 'dog', 'confidence': 0.6, 'bbox': [5, 5, 20, 20]}


def test_one_event_per_class_every_interval():
    node, sent = _node(interval=1.0)
    state = State()

    for i in range(30):
        node.update(_frame(i, 100 + i / 30, [_PERSON]), state=state)

    node.update(_frame(30, 101.0, [_PERSON]), state=state)

    assert [m.payload['frame'] for m in sent] == [0, 30]


def test_each_class_has_its_own_event():
    node, sent = _node()
    node.update(_frame(0, 100.0, [_PERSON, _PERSON, _DOG]), state=State())

    assert {m.payload['label']: m.payload['count'] for m in sent} == {
        'person': 2,
        'dog': 1,
    }


def test_frame_without_detections_emits_nothing():
    node, sent = _node()
    node.update(_frame(0, 100.0, []), state=State())

    assert sent == list()


def test_zero_interval_emits_for_every_frame():
    node, sent = _node(interval=0)
    state = State()

    for i in range(3):
        node.update(_frame(i, 100.0, [_PERSON]), state=state)

    assert len(sent) == 3


def test_event_is_plain_json():
    node, sent = _node()
    node.update(_frame(7, 123.5, [_PERSON]), state=State())

    assert json.loads(json.dumps(dict(sent[0].payload))) == {
        'event': 'detection',
        'label': 'person',
        'count': 1,
        'objects': [{'confidence': 0.9, 'bbox': [1, 2, 30, 40]}],
        'frame': 7,
        'timestamp': 123.5,
        'width': 64,
        'height': 48,
    }
    assert sent[0].version == 7
    # what NotifierUDP sends
    assert json.loads(sent[0].to_json())['payload']['label'] == 'person'
