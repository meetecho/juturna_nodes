"""
DetectionEvents

@ Author: Paolo Saviano
@ Email: psaviano@meetecho.com

Turn the detections attached to frames into small JSON events.
"""

from juturna.components import Message
from juturna.components import Node
from juturna.payloads import ImagePayload
from juturna.payloads import ObjectPayload


class DetectionEvents(Node[ImagePayload, ObjectPayload]):
    """Emit at most one event per detected class every interval"""

    def __init__(self, interval: float, **kwargs):
        """
        Parameters
        ----------
        interval : float
            Minimum time, in seconds of frame timestamp, between two events of
            the same class. With ``0`` every frame with the class produces an
            event.
        kwargs : dict
            Superclass arguments.

        """
        super().__init__(**kwargs)

        self._interval = interval

    def update(self, message: Message[ImagePayload], **kwargs):
        """Transmit one event per class not reported in the last interval"""
        state = kwargs.get('state')
        last = state.setdefault('last', dict())
        frame = message.payload
        groups = dict()

        for detection in message.meta.get('detections', ()):
            groups.setdefault(detection['label'], list()).append(
                {
                    'confidence': float(detection['confidence']),
                    'bbox': [int(v) for v in detection['bbox']],
                }
            )

        for label, objects in groups.items():
            if label in last and frame.timestamp - last[label] < self._interval:
                continue

            last[label] = frame.timestamp

            self.transmit(
                Message[ObjectPayload](
                    creator=self.name,
                    version=message.version,
                    timers_from=message,
                    payload=ObjectPayload.from_dict(
                        {
                            'event': 'detection',
                            'label': label,
                            'count': len(objects),
                            'objects': objects,
                            'frame': message.version,
                            'timestamp': frame.timestamp,
                            'width': frame.width,
                            'height': frame.height,
                        }
                    ),
                )
            )
