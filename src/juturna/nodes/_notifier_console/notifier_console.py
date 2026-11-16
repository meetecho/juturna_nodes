"""
NotifierConsole

Print every received message on the standard output, one line each.
"""

import json

from juturna.components import Message
from juturna.components import Node

from juturna.payloads import BasePayload
from juturna.payloads import ObjectPayload


class NotifierConsole(Node[BasePayload, None]):
    """Print incoming messages on the standard output"""

    def update(self, message: Message[BasePayload], **kwargs):
        """Print the message text, or its payload as compact JSON"""
        line = _render(message.payload)

        if line:
            print(f'[{message.creator}] {line}', flush=True)


def _render(payload: BasePayload) -> str:
    if not isinstance(payload, ObjectPayload):
        return f'<{type(payload).__name__}>'

    # transcriber nodes send a list of words: print them as text
    if isinstance(payload.get('transcript'), list):
        return ''.join(w.get('word', '') for w in payload['transcript']).strip()

    if isinstance(payload.get('text'), str):
        return payload['text'].strip()

    return json.dumps(dict(payload), default=str, separators=(',', ':'))
