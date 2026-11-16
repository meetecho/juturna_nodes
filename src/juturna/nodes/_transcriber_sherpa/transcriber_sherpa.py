"""
TranscriberSherpa

@ Author: Paolo Saviano
@ Email: psaviano@meetecho.com

Streaming speech recognition with sherpa-onnx: transmit one message for each
sentence, when the speaker stops talking.
"""

import pathlib

from juturna.components import Message
from juturna.components import Node

from juturna.payloads import AudioPayload
from juturna.payloads import ObjectPayload

from .._sherpa_models import fetch


class TranscriberSherpa(Node[AudioPayload, ObjectPayload]):
    """Transcribe audio with a streaming sherpa-onnx transducer model"""

    def __init__(
        self,
        model: str,
        model_dir: str,
        num_threads: int,
        min_trailing_silence: float,
        **kwargs,
    ):
        """
        Parameters
        ----------
        model : str
            Name of a known model, downloaded on first use into the cache.
            Ignored when model_dir is set.
        model_dir : str
            Folder of a sherpa-onnx streaming transducer model, holding
            tokens.txt and the encoder, decoder and joiner ONNX files; empty
            to use model.
        num_threads : int
            CPU threads used by the recognizer.
        min_trailing_silence : float
            Seconds of silence after speech that close a sentence.
        kwargs : dict
            Superclass arguments.

        """
        super().__init__(**kwargs)

        self._model = model
        self._model_dir = model_dir
        self._num_threads = num_threads
        self._min_trailing_silence = min_trailing_silence

        self._recognizer = None
        self._stream = None

    def warmup(self):
        """Load the model and open the recognition stream"""
        import sherpa_onnx

        model_dir = (
            pathlib.Path(self._model_dir)
            if self._model_dir
            else fetch(self._model, self.logger)
        )

        self._recognizer = sherpa_onnx.OnlineRecognizer.from_transducer(
            tokens=str(model_dir / 'tokens.txt'),
            encoder=_model_file(model_dir, 'encoder'),
            decoder=_model_file(model_dir, 'decoder'),
            joiner=_model_file(model_dir, 'joiner'),
            num_threads=self._num_threads,
            enable_endpoint_detection=True,
            rule2_min_trailing_silence=self._min_trailing_silence,
        )
        self._stream = self._recognizer.create_stream()

        self.logger.info(f'model loaded from {model_dir}')

    def update(self, message: Message[AudioPayload], **kwargs):
        """Feed the audio, transmit a sentence when it ends"""
        payload = message.payload
        self._stream.accept_waveform(payload.sampling_rate, payload.audio)

        while self._recognizer.is_ready(self._stream):
            self._recognizer.decode_stream(self._stream)

        if not self._recognizer.is_endpoint(self._stream):
            return

        result = self._recognizer.get_result_all(self._stream)
        self._recognizer.reset(self._stream)

        words = _words(result.tokens, result.timestamps, result.start_time)

        if not words:
            return

        to_send = Message[ObjectPayload](
            creator=self.name,
            version=message.version,
            payload=ObjectPayload.from_dict(
                {
                    'text': ''.join(w['word'] for w in words).strip(),
                    'transcript': words,
                }
            ),
            timers_from=message,
        )

        self.transmit(to_send)

    def destroy(self):
        """Release the model"""
        self._stream = None
        self._recognizer = None


def _model_file(model_dir: pathlib.Path, part: str) -> str:
    files = sorted(model_dir.glob(f'{part}*.onnx'))

    if not files:
        raise FileNotFoundError(f'no {part}*.onnx file in {model_dir}')

    # prefer the quantized model, which is smaller and faster on CPU
    int8 = [f for f in files if '.int8.' in f.name]

    return str((int8 or files)[0])


def _words(tokens: list, timestamps: list, offset: float) -> list[dict]:
    """Join the BPE tokens into words, with times in seconds from the start"""
    words = list()

    for token, time in zip(tokens, timestamps, strict=True):
        if token.startswith(' ') or not words:
            if words:
                words[-1]['end'] = offset + time

            words.append({'word': token, 'start': offset + time})
        else:
            words[-1]['word'] += token

    if words:
        words[-1]['end'] = offset + timestamps[-1]

    for w in words:
        w['word'] = ' ' + w['word'].strip().lower()

    return words
