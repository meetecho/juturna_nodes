"""
DetectorYolo

@ Author: Antonio Bevilacqua
@ Email: abevilacqua@meetecho.com

Annotate frames using YOLO models.
For more info about the models, see here: https://github.com/ultralytics/ultralytics
"""

import numpy as np

from ultralytics import YOLO
from ultralytics.cfg import DEFAULT_CFG_DICT

from juturna.components import Message
from juturna.components import Node

from juturna.payloads import ImagePayload


class DetectorYolo(Node[ImagePayload, ImagePayload]):
    """Node implementation class"""

    def __init__(
        self,
        model: str,
        device: str,
        targets: list,
        confidence: float,
        half: bool,
        **kwargs,
    ):
        """
        Parameters
        ----------
        model : str
            Name of the model to use
        device : str
            Where to run inference (cpu or cuda).
        targets : list
            List of class to target during inference.
        confidence : float
            Minimum confidence to mark a positive.
        half : bool
            Enable half precision to speed up inference time.
        kwargs : dict
            Supernode arguments.

        """
        super().__init__(**kwargs)

        self.logger.info(f'received extras: {kwargs}')

        self._model_name = model
        self._device = device
        self._targets = targets
        self._confidence = confidence
        self._half = half

        self._model = None
        self._classes = None

        # ultralytics 8.4 replaced `half` with `quantize`, and warns on every
        # predict call that passes `half`, whatever its value
        if 'quantize' in DEFAULT_CFG_DICT:
            self._precision = {'quantize': 16 if half else None}
        else:
            self._precision = {'half': half}

    def warmup(self):
        """Warmup the node"""
        self._model = YOLO(self._model_name)
        self._model.to(self._device)
        self._classes = [
            {v: k for k, v in self._model.names.items()}[t]
            for t in self._targets
        ]

        # the first inference initialises CUDA kernels and takes seconds:
        # pay it here, before frames start queueing up
        self._model.predict(
            np.zeros((640, 640, 3), dtype=np.uint8),
            verbose=False,
            classes=self._classes,
            **self._precision,
        )

        self.logger.info('detector ready')

    def update(self, message: Message[ImagePayload], **kwargs):
        """Receive a message, transmit a message"""
        image = message.payload.image
        results = self._model.predict(
            image,
            verbose=False,
            classes=self._classes,
            conf=self._confidence,
            **self._precision,
        )

        annotated = results[0].plot()

        to_send = Message[ImagePayload](
            creator=self.name,
            version=message.version,
            payload=ImagePayload(
                image=annotated,
                width=annotated.shape[1],
                height=annotated.shape[0],
                depth=annotated.shape[2],
                pixel_format=message.payload.pixel_format,
                timestamp=message.payload.timestamp,
            ),
            timers_from=message,
        )

        to_send.meta['annotations'] = results[0]

        self.transmit(to_send)
