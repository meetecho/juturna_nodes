import json

import numpy as np
import pytest

pytest.importorskip('onnxruntime')

from juturna.components import Message  # noqa: E402
from juturna.nodes import DetectorYolox  # noqa: E402
from juturna.nodes._detector_yolox import detector_yolox  # noqa: E402
from juturna.payloads import ImagePayload  # noqa: E402


# the classic test image of YOLOX, at a fixed commit of its Apache-2.0 repo
_DOG_JPG = (
    'https://raw.githubusercontent.com/Megvii-BaseDetection/YOLOX/'
    '6ddff4824372906469a7fae2dc3206c7aa4bbaee/assets/dog.jpg'
)


def _detector(targets=(), size=416):
    node = DetectorYolox(
        model='unused.onnx',
        targets=list(targets),
        confidence=0.3,
        nms=0.45,
        device='cpu',
        node_name='d',
        pipe_name='p',
    )
    node._size = size
    node._grids, node._strides = detector_yolox._grids(size)

    return node


def _raw_output(size, cells):
    """
    Model output with every score at zero but the given cells, as
    ``{row: (cx, cy, w, h, class index, score)}`` in pixels
    """
    grids, strides = detector_yolox._grids(size)
    out = np.zeros((len(grids), 85), dtype=np.float32)
    out[:, 2:4] = -20  # exp() of it is ~0 width

    for row, (cx, cy, w, h, cls, score) in cells.items():
        out[row, :2] = np.array([cx, cy]) / strides[row] - grids[row]
        out[row, 2:4] = np.log(np.array([w, h]) / strides[row])
        out[row, 4] = 1.0
        out[row, 5 + cls] = score

    return out


def test_unknown_target_is_rejected():
    with pytest.raises(ValueError, match='unicorn'):
        _detector(targets=['person', 'unicorn'])


def test_letterbox_keeps_the_ratio_and_swaps_to_bgr():
    image = np.zeros((100, 200, 3), dtype=np.uint8)
    image[..., 0] = 255  # red

    blob, ratio = detector_yolox._letterbox(image, 416)

    assert blob.shape == (1, 3, 416, 416)
    assert blob.dtype == np.float32
    assert ratio == pytest.approx(2.08)
    # red ends up in the last channel, the padding below is grey
    assert blob[0, :, 0, 0].tolist() == [0, 0, 255]
    assert blob[0, :, 300, 0].tolist() == [114, 114, 114]


def test_decode_scales_boxes_back_and_merges_overlaps():
    node = _detector()
    out = _raw_output(
        416,
        {
            100: (100, 100, 40, 80, 0, 0.9),  # person
            101: (102, 100, 40, 80, 0, 0.8),  # the same person, merged
            3000: (300, 300, 50, 50, 16, 0.6),  # dog
            3001: (200, 300, 50, 50, 16, 0.1),  # below confidence
        },
    )

    detections = node._decode(out, ratio=0.5, width=1000, height=1000)

    assert detections == [
        {'label': 'person', 'confidence': 0.9, 'bbox': [160, 120, 240, 280]},
        {'label': 'dog', 'confidence': 0.6, 'bbox': [550, 550, 650, 650]},
    ]


def test_decode_keeps_only_targets():
    node = _detector(targets=['dog'])
    out = _raw_output(
        416,
        {100: (100, 100, 40, 80, 0, 0.9), 3000: (300, 300, 50, 50, 16, 0.6)},
    )

    labels = [d['label'] for d in node._decode(out, 1.0, 416, 416)]

    assert labels == ['dog']


def test_update_attaches_plain_detections(monkeypatch):
    node = _detector()
    sent = list()
    monkeypatch.setattr(node, 'transmit', sent.append)
    monkeypatch.setattr(
        node,
        'detect',
        lambda image: [
            {'label': 'cat', 'confidence': 0.5, 'bbox': [1, 2, 3, 4]}
        ],
    )
    payload = ImagePayload(image=np.zeros((4, 4, 3), np.uint8), timestamp=1.0)

    message = Message[ImagePayload](creator='src', version=3, payload=payload)
    message.meta['pts'] = 42
    message._freeze()  # as transmit() delivers it
    node.update(message)

    assert sent[0].meta['pts'] == 42
    assert sent[0].version == 3
    assert sent[0].payload is payload
    assert json.loads(json.dumps(sent[0].meta['detections']))[0]['label'] == (
        'cat'
    )


def test_yolox_nano_finds_the_dog(tmp_path, monkeypatch):
    av = pytest.importorskip('av')
    requests = pytest.importorskip('requests')

    try:
        response = requests.get(_DOG_JPG, timeout=30)
        response.raise_for_status()
    except requests.RequestException as e:
        pytest.skip(f'test image not reachable: {e}')

    (tmp_path / 'dog.jpg').write_bytes(response.content)
    monkeypatch.setenv('XDG_CACHE_HOME', str(tmp_path / 'cache'))

    node = DetectorYolox(
        model='yolox_nano',
        targets=[],
        confidence=0.3,
        nms=0.45,
        device='cpu',
        node_name='d',
        pipe_name='p',
    )
    node.warmup()

    with av.open(str(tmp_path / 'dog.jpg')) as container:
        image = next(container.decode(video=0)).to_ndarray(format='rgb24')

    found = {d['label']: d for d in node.detect(image)}

    assert {'dog', 'bicycle'} <= set(found)
    assert found['dog']['confidence'] > 0.8
    x1, y1, x2, y2 = found['dog']['bbox']
    # the dog sits in the lower left of the 768x576 picture
    assert x1 < 200 < x2 < 400 and 150 < y1 < 300 < y2
