"""
PrompterOllama

@ Author: Paolo Saviano
@ Email: psaviano@meetecho.com

Send the text of each message to a model served by Ollama, and transmit the
answer.
"""

import time

import requests

from juturna.components import Message
from juturna.components import Node

from juturna.payloads import ObjectPayload


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
            Seconds to wait for each answer.
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

    def warmup(self):
        """Load the model, so the first question is not slowed down"""
        self._chat(list())

        self.logger.info(f'model {self._model_name} loaded')

    def update(self, message: Message[ObjectPayload], **kwargs):
        """Ask the model the text of the message, transmit its answer"""
        prompt = message.payload.get('text', '').strip()

        if not prompt:
            return

        start = time.perf_counter()

        try:
            answer = self._chat([{'role': 'user', 'content': prompt}])
        except requests.RequestException as error:
            self.logger.error(f'request to {self._url} failed: {error}')

            return

        to_send = Message[ObjectPayload](
            creator=self.name,
            version=message.version,
            payload=ObjectPayload.from_dict(
                {'prompt': prompt, 'text': answer['message']['content'].strip()}
            ),
            timers_from=message,
        )
        to_send.timer(self.name, time.perf_counter() - start)

        self.transmit(to_send)

    def _chat(self, messages: list[dict]) -> dict:
        response = requests.post(
            self._url,
            json={
                'model': self._model_name,
                'messages': self._system + messages if messages else list(),
                'stream': False,
                'keep_alive': self._keep_alive,
                'think': self._think,
            },
            timeout=self._timeout,
        )
        response.raise_for_status()

        return response.json()
