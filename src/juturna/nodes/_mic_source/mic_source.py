"""
MicSource

@ Author: Paolo Saviano
@ Email: psaviano@meetecho.com

Capture audio from a microphone, optionally only while push-to-talk is on.
"""

import select
import sys

import numpy as np

from juturna.components import Message
from juturna.components import Node
from juturna.meta import JUTURNA_THREAD_JOIN_TIMEOUT

from juturna.payloads import AudioPayload


class MicSource(Node[AudioPayload, AudioPayload]):
    """Capture mono audio chunks from a microphone"""

    def __init__(
        self,
        device: str,
        sample_rate: int,
        block_size: float,
        push_to_talk: bool,
        trailing_silence: float,
        **kwargs,
    ):
        """
        Parameters
        ----------
        device : str
            Input device, as a name (or part of it) or an index listed by
            `python -m sounddevice`; empty for the system default.
        sample_rate : int
            Rate of the produced audio, in Hz.
        block_size : float
            Length of each produced chunk, in seconds.
        push_to_talk : bool
            Capture only between two presses of Enter on the terminal.
        trailing_silence : float
            Seconds of silence sent when push-to-talk is turned off, so that
            downstream speech recognition closes the sentence at once.
        kwargs : dict
            Superclass arguments.

        """
        super().__init__(**kwargs)

        self._device = int(device) if device.isdigit() else device or None
        self._rate = sample_rate
        self._frames = int(sample_rate * block_size)
        self._push_to_talk = push_to_talk
        self._trailing_silence = trailing_silence

        self._stream = None
        self._talking = self._transport.new_event()
        self._released = self._transport.new_event()
        self._stop_keys = self._transport.new_event()
        self._keys = None
        self._elapsed = 0

    def warmup(self):
        """Open the microphone"""
        import sounddevice

        self._stream = sounddevice.InputStream(
            device=self._device,
            samplerate=self._rate,
            channels=1,
            dtype='float32',
            blocksize=self._frames,
        )
        self.set_source(self._read_chunk, by=0)

        self.logger.info(f'microphone opened: {self._stream.device}')

    def start(self):
        """Start capturing, and listen to the keyboard for push-to-talk"""
        self._stream.start()
        self._stop_keys.clear()

        if self._push_to_talk:
            self._keys = self._transport.spawn(
                target=self._watch_keys, name=f'{self.name}_keys', daemon=True
            )
            self._keys.start()
            print(f'[{self.name}] press Enter to talk', flush=True)

        super().start()

    def stop(self):
        """Stop capturing"""
        self._stop_keys.set()

        if self._keys is not None:
            self._keys.join(JUTURNA_THREAD_JOIN_TIMEOUT)

        super().stop()

        if self._stream is not None:
            self._stream.stop()

    def destroy(self):
        """Close the microphone"""
        if self._stream is not None:
            self._stream.close()
            self._stream = None

    def update(self, message: Message[AudioPayload], **kwargs):
        """Transmit the captured chunk"""
        self.transmit(message)

    def toggle(self):
        """Turn push-to-talk on or off"""
        if self._talking.is_set():
            self._talking.clear()
            self._released.set()
            print(f'[{self.name}] stopped, press Enter to talk', flush=True)
        else:
            self._talking.set()
            print(f'[{self.name}] listening, press Enter to stop', flush=True)

    def _read_chunk(self) -> Message[AudioPayload] | None:
        # the stream is always read, so no stale audio piles up while muted
        audio, _ = self._stream.read(self._frames)
        audio = np.ascontiguousarray(audio[:, 0])

        if self._push_to_talk and not self._talking.is_set():
            if not self._released.is_set():
                return None

            self._released.clear()
            audio = np.zeros(
                int(self._rate * self._trailing_silence), np.float32
            )

        start = self._elapsed / self._rate
        self._elapsed += audio.size

        return Message[AudioPayload](
            creator=self.name,
            payload=AudioPayload(
                audio=audio,
                sampling_rate=self._rate,
                channels=1,
                start=start,
                end=self._elapsed / self._rate,
            ),
        )

    def _watch_keys(self):
        while not self._stop_keys.is_set():
            ready, _, _ = select.select([sys.stdin], [], [], 0.2)

            if not ready:
                continue

            if not sys.stdin.readline():
                self.logger.warning('standard input closed, push-to-talk off')

                return

            self.toggle()
