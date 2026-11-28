"""
SpeakerSink

@ Author: Paolo Saviano
@ Email: psaviano@meetecho.com

Play the audio of every received message on a speaker.
"""

import numpy as np

from juturna.components import Message
from juturna.components import Node

from juturna.payloads import AudioPayload


class SpeakerSink(Node[AudioPayload, None]):
    """Play incoming audio on an output device, one message after the other"""

    def __init__(self, device: str, **kwargs):
        """
        Parameters
        ----------
        device : str
            Output device, as a name (or part of it) or an index listed by
            `python -m sounddevice`; empty for the system default.
        kwargs : dict
            Superclass arguments.

        """
        super().__init__(**kwargs)

        self._device = int(device) if device.isdigit() else device or None
        self._sounddevice = None
        # set by stop(): the audio playing is cut, the queued one dropped
        self._stopping = self._transport.new_event()

    def warmup(self):
        """Check that the output device exists"""
        import sounddevice

        sounddevice.check_output_settings(device=self._device)
        self._sounddevice = sounddevice

    def update(self, message: Message[AudioPayload], **kwargs):
        """Play the audio and wait until it ends, or until the node stops"""
        if self._stopping.is_set():
            return

        payload = message.payload
        audio = np.clip(payload.audio, -1.0, 1.0).astype(np.float32)

        self._sounddevice.play(
            audio, samplerate=payload.sampling_rate, device=self._device
        )

        if self._stopping.wait(len(audio) / payload.sampling_rate):
            self._sounddevice.stop()
        else:
            self._sounddevice.wait()

    def start(self):
        """Start the node"""
        self._stopping.clear()

        super().start()

    def stop(self):
        """Stop the node, silencing the speaker at once"""
        # before super().stop(), which waits for the queued audio to drain
        self._stopping.set()

        super().stop()
