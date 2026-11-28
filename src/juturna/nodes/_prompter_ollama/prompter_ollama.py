"""
PrompterOllama

@ Author: Paolo Saviano
@ Email: psaviano@meetecho.com

Send the text of each message to a model served by Ollama, and transmit the
answer sentence by sentence while the model writes it.
"""

import contextlib
import json
import re
import time

import requests

from juturna.components import Message
from juturna.components import Node
from juturna.payloads import ObjectPayload
from juturna.transport import Empty


# a sentence ends at . ! ? or an ellipsis followed by a space, or at a newline
_SENTENCE_END = re.compile(r'(?<=[.!?…])\s+|\n+')
# shortcut: fixed threshold, make it an argument if it needs tuning
_MIN_SENTENCE_CHARS = 20
# how long the idle source waits for a question, and stop() for the source
_POLL = 0.1


class PrompterOllama(Node[ObjectPayload, ObjectPayload]):
    """Ask a model served by Ollama, one request per message"""

    def __init__(
        self,
        endpoint: str,
        model_name: str,
        system_prompt: str,
        keep_alive: str,
        think: bool,
        timeout: float,
        stream: bool,
        **kwargs,
    ):
        """
        Parameters
        ----------
        endpoint : str
            Base address of the Ollama server.
        model_name : str
            Model to chat with, as listed by `ollama list`.
        system_prompt : str
            System message sent before every question; empty for none.
        keep_alive : str
            How long Ollama keeps the model loaded after a request, in its
            duration format ("5m", "-1" for ever, "0" to unload at once).
        think : bool
            Let models that support it reason before answering.
        timeout : float
            Seconds to wait for the connection and between two pieces of the
            answer, the first one included.
        stream : bool
            Transmit the answer one sentence at a time; if false, transmit
            it whole once the model is done.
        kwargs : dict
            Superclass arguments.

        """
        super().__init__(**kwargs)

        self._url = endpoint.rstrip('/') + '/api/chat'
        self._model_name = model_name
        self._system = (
            [{'role': 'system', 'content': system_prompt}]
            if system_prompt
            else list()
        )
        self._keep_alive = keep_alive
        self._think = think
        self._timeout = timeout
        self._stream = stream

        # questions wait here for the source, which streams the answers
        self._turns = self._transport.new_queue(local=True)
        self._turn = None
        self._answer = None
        # set by stop(): the answer in progress ends at its next piece
        self._stopping = self._transport.new_event()

        self.set_source(self._next_sentence)

    def warmup(self):
        """Load the model, so the first question is not slowed down"""
        # loading a large model can take minutes: bound only the connection
        response = requests.post(
            self._url,
            json=self._body(list(), stream=False),
            timeout=(self._timeout, None),
        )
        response.raise_for_status()

        self.logger.info(f'model {self._model_name} loaded')

    def start(self):
        """Start the node"""
        self._stopping.clear()

        super().start()

    def stop(self):
        """Stop the node, and drop the answer in progress"""
        # before super().stop(), which waits for the source call to return
        self._stopping.set()

        super().stop()

        # the questions and sentences still queued become stale
        self._turn = None

        if self._answer is not None:
            # raised if a killed source is still reading: it exits on its own
            with contextlib.suppress(ValueError):
                self._answer.close()

            self._answer = None

    def update(self, message: Message[ObjectPayload], **kwargs):
        """Queue a question, or transmit a sentence of the current answer"""
        if message.creator == self.name:
            # a sentence from the source: drop it if a newer question came
            if message.meta['turn'] == self._turn:
                self.transmit(message)

            return

        prompt = message.payload.get('text', '').strip()

        if not prompt:
            return

        self._turn = message.id
        self._turns.put((message, prompt, time.perf_counter()))

    def _next_sentence(self) -> Message[ObjectPayload] | None:
        """Source: the next sentence of the current answer, if any"""
        if self._answer is None:
            try:
                message, prompt, start = self._turns.get(timeout=_POLL)
            except Empty:
                return None

            if message.id != self._turn:
                return None

            self._answer = self._sentences(message, prompt, start)

        try:
            return next(self._answer)
        except StopIteration:
            self._answer = None

            return None
        except Exception:
            self._answer = None

            raise

    def _sentences(self, message: Message, prompt: str, start: float):
        sequence = 0
        buffer = ''
        body = self._body([{'role': 'user', 'content': prompt}], stream=True)

        with requests.post(
            self._url, json=body, stream=True, timeout=self._timeout
        ) as response:
            response.raise_for_status()

            for line in response.iter_lines():
                if message.id != self._turn or self._stopping.is_set():
                    # leaving the block closes the connection: Ollama stops
                    return

                if not line:
                    continue

                chunk = json.loads(line)

                if 'error' in chunk:
                    raise RuntimeError(f'Ollama error: {chunk["error"]}')

                buffer += chunk.get('message', dict()).get('content', '')

                if chunk.get('done'):
                    break

                while self._stream and (cut := _sentence_cut(buffer)):
                    text, buffer = buffer[: cut[0]].strip(), buffer[cut[1] :]

                    yield self._sentence(message, prompt, text, sequence, start)

                    sequence += 1
            else:
                raise requests.ConnectionError('answer ended before done')

        final = self._sentence(message, prompt, buffer.strip(), sequence, start)
        final.meta['final'] = True

        yield final

    def _sentence(
        self,
        message: Message,
        prompt: str,
        text: str,
        sequence: int,
        start: float,
    ) -> Message[ObjectPayload]:
        to_send = Message[ObjectPayload](
            creator=self.name,
            version=message.version,
            payload=ObjectPayload.from_dict({'prompt': prompt, 'text': text}),
            timers_from=message,
        )
        to_send.meta.update(
            turn=message.id,
            sequence=sequence,
            final=False,
            source=message.creator,
        )
        to_send.timer(self.name, time.perf_counter() - start)

        return to_send

    def _body(self, messages: list[dict], stream: bool) -> dict:
        return {
            'model': self._model_name,
            'messages': self._system + messages if messages else list(),
            'stream': stream,
            'keep_alive': self._keep_alive,
            'think': self._think,
        }


def _sentence_cut(buffer: str) -> tuple[int, int] | None:
    """Where the first sentence long enough ends, and the next one starts"""
    for match in _SENTENCE_END.finditer(buffer):
        if len(buffer[: match.start()].strip()) >= _MIN_SENTENCE_CHARS:
            return match.start(), match.end()

    return None
