"""
AudioWriter

Append the audio of every received message to a WAV file.
"""

import pathlib
import wave

import numpy as np

from juturna.components import Message
from juturna.components import Node

from juturna.payloads import AudioPayload


class AudioWriter(Node[AudioPayload, None]):
    """Write incoming audio to a 16-bit mono WAV file"""

    def __init__(self, file_name: str, **kwargs):
        """
        Parameters
        ----------
        file_name : str
            Name of the WAV file, created in the node folder of the pipeline.
        kwargs : dict
            Superclass arguments.

        """
        super().__init__(**kwargs)

        self._file_name = file_name
        self._wav = None

    def update(self, message: Message[AudioPayload], **kwargs):
        """Append the audio of the message to the file"""
        payload = message.payload

        # the sampling rate is only known with the first message
        if self._wav is None:
            path = pathlib.Path(self.pipe_path, self._file_name)
            # kept open across messages, closed in destroy()
            self._wav = wave.open(str(path), 'wb')  # noqa: SIM115
            self._wav.setnchannels(1)
            self._wav.setsampwidth(2)
            self._wav.setframerate(payload.sampling_rate)

            self.logger.info(f'writing to {path}')

        if payload.sampling_rate != self._wav.getframerate():
            self.logger.error(
                f'sampling rate {payload.sampling_rate} differs from the file '
                f'rate {self._wav.getframerate()}, message dropped'
            )

            return

        samples = np.clip(payload.audio, -1.0, 1.0) * 32767
        self._wav.writeframes(samples.astype('<i2').tobytes())

    def destroy(self):
        """Close the file"""
        if self._wav is not None:
            self._wav.close()
            self._wav = None
