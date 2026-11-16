"""
SynthesizerSherpa

Text to speech with sherpa-onnx: turn the text of each message into audio.
"""

import pathlib
import time

import numpy as np

from juturna.components import Message
from juturna.components import Node

from juturna.payloads import AudioPayload
from juturna.payloads import ObjectPayload


_MODEL_TYPES = ('kitten', 'kokoro')


class SynthesizerSherpa(Node[ObjectPayload, AudioPayload]):
    """Synthesize speech from text with a sherpa-onnx model"""

    def __init__(
        self,
        model_dir: str,
        model_type: str,
        lexicon: str,
        speaker_id: int,
        speed: float,
        num_threads: int,
        **kwargs,
    ):
        """
        Parameters
        ----------
        model_dir : str
            Folder of a sherpa-onnx TTS model, holding one ONNX file,
            voices.bin and tokens.txt.
        model_type : str
            Model family: kitten or kokoro.
        lexicon : str
            Pronunciation lexicon file, such as lexicon-en-us.txt. Words that
            are not in it are skipped.
        speaker_id : int
            Voice to use, among the voices of the model.
        speed : float
            Speech speed, 1.0 being the natural speed of the voice.
        num_threads : int
            CPU threads used by the model.
        kwargs : dict
            Superclass arguments.

        """
        super().__init__(**kwargs)

        if model_type not in _MODEL_TYPES:
            raise ValueError(f'model_type must be one of {_MODEL_TYPES}')

        self._model_dir = pathlib.Path(model_dir)
        self._model_type = model_type
        self._lexicon = lexicon
        self._speaker_id = speaker_id
        self._speed = speed
        self._num_threads = num_threads

        self._tts = None

    def warmup(self):
        """Load the model"""
        import sherpa_onnx

        model_files = sorted(self._model_dir.glob('*.onnx'))

        if len(model_files) != 1:
            raise FileNotFoundError(
                f'expected one ONNX file in {self._model_dir}, '
                f'found {len(model_files)}'
            )

        model_config = getattr(
            sherpa_onnx, f'OfflineTts{self._model_type.title()}ModelConfig'
        )(
            model=str(model_files[0]),
            voices=str(self._model_dir / 'voices.bin'),
            tokens=str(self._model_dir / 'tokens.txt'),
            lexicon=self._lexicon,
        )

        self._tts = sherpa_onnx.OfflineTts(
            sherpa_onnx.OfflineTtsConfig(
                model=sherpa_onnx.OfflineTtsModelConfig(
                    num_threads=self._num_threads,
                    **{self._model_type: model_config},
                )
            )
        )

        self.logger.info(f'model loaded from {self._model_dir}')

    def update(self, message: Message[ObjectPayload], **kwargs):
        """Synthesize the text of the message, transmit the audio"""
        text = message.payload.get('text', '').strip()

        if not text:
            return

        start = time.perf_counter()
        speech = self._tts.generate(
            text, sid=self._speaker_id, speed=self._speed
        )
        audio = np.asarray(speech.samples, dtype=np.float32)

        if audio.size == 0:
            self.logger.warning(f'no audio generated for: {text}')

            return

        to_send = Message[AudioPayload](
            creator=self.name,
            version=message.version,
            payload=AudioPayload(
                audio=audio,
                sampling_rate=speech.sample_rate,
                channels=1,
                start=0.0,
                end=audio.size / speech.sample_rate,
            ),
            timers_from=message,
        )
        to_send.meta['text'] = text
        to_send.timer(self.name, time.perf_counter() - start)

        self.transmit(to_send)

    def destroy(self):
        """Release the model"""
        self._tts = None
