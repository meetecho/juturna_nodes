import numpy as np
import pytest

pytest.importorskip('ultralytics')

from PIL import Image  # noqa: E402
from ultralytics.utils import ASSETS  # noqa: E402

from juturna.components import Message  # noqa: E402
from juturna.components import State  # noqa: E402
from juturna.nodes import DetectorYolo  # noqa: E402
from juturna.payloads import ImagePayload  # noqa: E402


@pytest.fixture(scope='module')
def detector(tmp_path_factory, monkeypatch_module):
    # ultralytics downloads the weights into the working directory
    monkeypatch_module.chdir(tmp_path_factory.mktemp('weights'))
    node = DetectorYolo(
        model='yolo11n.pt',
        device='cpu',
        targets=['person', 'bus'],
        confidence=0.25,
        half=False,
        node_name='detector',
        pipe_name='pipe',
    )
    node.warmup()

    return node


@pytest.fixture(scope='module')
def monkeypatch_module():
    with pytest.MonkeyPatch.context() as patch:
        yield patch


@pytest.fixture(scope='module')
def bus():
    return np.asarray(Image.open(ASSETS / 'bus.jpg').convert('RGB'))


def _detect(node, image):
    sent = list()
    node.transmit = sent.append
    message = Message[ImagePayload](
        creator='camera',
        version=7,
        payload=ImagePayload(
            image=image,
            width=image.shape[1],
            height=image.shape[0],
            depth=3,
            pixel_format='rgb24',
            timestamp=1.5,
        ),
    )
    node.update(message, state=State())

    return sent[0]


def test_detections_are_plain_data_in_meta(detector, bus):
    detections = _detect(detector, bus).meta['detections']

    assert {d['label'] for d in detections} == {'bus', 'person'}

    for d in detections:
        assert set(d) == {'label', 'confidence', 'bbox'}
        assert 0.25 <= d['confidence'] <= 1
        x1, y1, x2, y2 = d['bbox']
        assert 0 <= x1 < x2 <= bus.shape[1]
        assert 0 <= y1 < y2 <= bus.shape[0]
        assert all(isinstance(v, int) for v in d['bbox'])


def test_model_receives_bgr_and_output_stays_rgb(detector, bus, monkeypatch):
    seen = list()
    predict = detector._model.predict

    def spy(image, **kwargs):
        seen.append(image)

        return predict(image, **kwargs)

    monkeypatch.setattr(detector._model, 'predict', spy)
    out = _detect(detector, bus)

    # ultralytics reads NumPy arrays as BGR
    assert np.array_equal(seen[0], bus[..., ::-1])
    # a corner far from every box keeps the colour of the input frame
    assert np.array_equal(out.payload.image[0, 0], bus[0, 0])
    assert out.payload.pixel_format == 'rgb24'
    assert out.version == 7
