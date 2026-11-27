"""
DetectorYolox

@ Author: Paolo Saviano
@ Email: psaviano@meetecho.com

Detect objects in frames with YOLOX models exported to ONNX.

The pre and post-processing are ported from the ONNXRuntime demo of YOLOX
(https://github.com/Megvii-BaseDetection/YOLOX, Apache-2.0, Copyright (c)
Megvii Inc.).
"""

import pathlib

import numpy as np
import onnxruntime

from juturna.components import Message
from juturna.components import Node
from juturna.payloads import ImagePayload

from .._models import MODELS
from .._models import fetch


COCO_CLASSES = (
    'person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train',
    'truck', 'boat', 'traffic light', 'fire hydrant', 'stop sign',
    'parking meter', 'bench', 'bird', 'cat', 'dog', 'horse', 'sheep', 'cow',
    'elephant', 'bear', 'zebra', 'giraffe', 'backpack', 'umbrella', 'handbag',
    'tie', 'suitcase', 'frisbee', 'skis', 'snowboard', 'sports ball', 'kite',
    'baseball bat', 'baseball glove', 'skateboard', 'surfboard',
    'tennis racket', 'bottle', 'wine glass', 'cup', 'fork', 'knife', 'spoon',
    'bowl', 'banana', 'apple', 'sandwich', 'orange', 'broccoli', 'carrot',
    'hot dog', 'pizza', 'donut', 'cake', 'chair', 'couch', 'potted plant',
    'bed', 'dining table', 'toilet', 'tv', 'laptop', 'mouse', 'remote',
    'keyboard', 'cell phone', 'microwave', 'oven', 'toaster', 'sink',
    'refrigerator', 'book', 'clock', 'vase', 'scissors', 'teddy bear',
    'hair drier', 'toothbrush',
)  # fmt: skip


class DetectorYolox(Node[ImagePayload, ImagePayload]):
    """Attach the objects found by a YOLOX model to each frame"""

    def __init__(
        self,
        model: str,
        targets: list,
        confidence: float,
        nms: float,
        device: str,
        **kwargs,
    ):
        """
        Parameters
        ----------
        model : str
            ``yolox_nano``, ``yolox_tiny`` or ``yolox_s``, downloaded on first
            use, or the path of a YOLOX ``.onnx`` file.
        targets : list
            COCO class names to keep; empty keeps all of them.
        confidence : float
            Minimum score of a detection.
        nms : float
            IoU above which overlapping boxes are merged.
        device : str
            ``cpu``, or ``cuda`` with the ``onnxruntime-gpu`` package.
        kwargs : dict
            Superclass arguments.

        """
        super().__init__(**kwargs)

        unknown = set(targets) - set(COCO_CLASSES)

        if unknown:
            raise ValueError(f'unknown target classes: {sorted(unknown)}')

        self._model = model
        self._classes = [COCO_CLASSES.index(t) for t in targets] or list(
            range(len(COCO_CLASSES))
        )
        self._confidence = confidence
        self._nms = nms
        self._device = device

        self._session = None
        self._input = None
        self._size = 0
        self._grids = None
        self._strides = None

    def warmup(self):
        """Load the model and run it once"""
        path = (
            fetch(self._model, self.logger) / f'{self._model}.onnx'
            if self._model in MODELS
            else pathlib.Path(self._model)
        )
        providers = ['CPUExecutionProvider']

        if self._device == 'cuda':
            providers.insert(0, 'CUDAExecutionProvider')

        self._session = onnxruntime.InferenceSession(
            str(path), providers=providers
        )
        model_input = self._session.get_inputs()[0]
        _, _, height, width = model_input.shape

        if not isinstance(height, int) or height != width:
            raise ValueError(
                f'{path.name}: a fixed square input is needed, the model has '
                f'{height}x{width} (exported with --dynamic?)'
            )

        self._input = model_input.name
        self._size = height
        self._grids, self._strides = _grids(self._size)

        self._session.run(
            None,
            {self._input: np.zeros((1, 3, self._size, self._size), np.float32)},
        )
        self.logger.info(f'{path.name} ready, input {self._size}px')

    def update(self, message: Message[ImagePayload], **kwargs):
        """Transmit the frame with its detections in meta"""
        to_send = message.copy(creator=self.name)
        to_send.meta['detections'] = self.detect(message.payload.image)

        self.transmit(to_send)

    def detect(self, image: np.ndarray) -> list[dict]:
        """
        Find the objects in an RGB image.

        Parameters
        ----------
        image : np.ndarray
            ``uint8`` RGB image of shape ``(height, width, 3)``.

        Returns
        -------
        list[dict]
            One ``{"label", "confidence", "bbox"}`` per object, with the box
            as ``[x1, y1, x2, y2]`` pixels of the image.

        """
        blob, ratio = _letterbox(image, self._size)
        out = self._session.run(None, {self._input: blob})[0][0]

        return self._decode(out, ratio, image.shape[1], image.shape[0])

    def _decode(self, out, ratio, width, height) -> list[dict]:
        centres = (out[:, :2] + self._grids) * self._strides
        sizes = np.exp(out[:, 2:4]) * self._strides
        boxes = np.concatenate([centres - sizes / 2, centres + sizes / 2], 1)
        boxes /= ratio

        # the best class is picked over all of them, then kept if a target
        scores = out[:, 4:5] * out[:, 5:]
        best = scores.argmax(1)
        best_scores = scores[np.arange(len(best)), best]
        mask = (best_scores > self._confidence) & np.isin(best, self._classes)
        boxes, best, best_scores = boxes[mask], best[mask], best_scores[mask]

        boxes[:, [0, 2]] = boxes[:, [0, 2]].clip(0, width - 1)
        boxes[:, [1, 3]] = boxes[:, [1, 3]].clip(0, height - 1)

        return [
            {
                'label': COCO_CLASSES[best[i]],
                'confidence': round(float(best_scores[i]), 3),
                'bbox': [int(v) for v in boxes[i].round()],
            }
            for i in _nms(boxes, best_scores, self._nms)
        ]


def _grids(size: int) -> tuple[np.ndarray, np.ndarray]:
    """Cell coordinates and strides of the model outputs"""
    grids, strides = list(), list()

    for stride in (8, 16, 32):
        cells = size // stride
        xs, ys = np.meshgrid(np.arange(cells), np.arange(cells))
        grids.append(np.stack((xs, ys), 2).reshape(-1, 2))
        strides.append(np.full((cells * cells, 1), stride))

    return np.concatenate(grids), np.concatenate(strides)


def _letterbox(image: np.ndarray, size: int) -> tuple[np.ndarray, float]:
    """Scale into a size x size BGR blob, padded with grey"""
    height, width = image.shape[:2]
    ratio = min(size / height, size / width)
    new_h, new_w = int(height * ratio), int(width * ratio)

    # shortcut: nearest-neighbour resize, to avoid an image library; use a
    # linear one (as YOLOX does with OpenCV) if small objects are missed
    rows = np.minimum((np.arange(new_h) / ratio).astype(int), height - 1)
    cols = np.minimum((np.arange(new_w) / ratio).astype(int), width - 1)

    padded = np.full((size, size, 3), 114, dtype=np.uint8)
    # YOLOX models are trained on BGR images
    padded[:new_h, :new_w] = image[rows][:, cols, ::-1]
    blob = padded.transpose(2, 0, 1)[None].astype(np.float32)

    return blob, ratio


def _nms(boxes: np.ndarray, scores: np.ndarray, threshold: float) -> list:
    """Indexes of the boxes kept by a class-agnostic non-maximum suppression"""
    areas = (boxes[:, 2] - boxes[:, 0] + 1) * (boxes[:, 3] - boxes[:, 1] + 1)
    order = scores.argsort()[::-1]
    keep = list()

    while order.size > 0:
        i, rest = order[0], order[1:]
        keep.append(int(i))

        x1 = np.maximum(boxes[i, 0], boxes[rest, 0])
        y1 = np.maximum(boxes[i, 1], boxes[rest, 1])
        x2 = np.minimum(boxes[i, 2], boxes[rest, 2])
        y2 = np.minimum(boxes[i, 3], boxes[rest, 3])
        inter = np.maximum(0.0, x2 - x1 + 1) * np.maximum(0.0, y2 - y1 + 1)
        overlap = inter / (areas[i] + areas[rest] - inter)

        order = rest[overlap <= threshold]

    return keep
