import http.server
import json
import threading

import pytest

from juturna.components import Message
from juturna.nodes import PrompterOllama
from juturna.payloads import ObjectPayload


class _FakeOllama(http.server.BaseHTTPRequestHandler):
    requests = list()

    def do_POST(self):  # noqa: N802
        body = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
        _FakeOllama.requests.append((self.path, body))
        last = body['messages'][-1]['content'] if body['messages'] else ''
        reply = json.dumps({'message': {'content': f' answer to {last} '}})

        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(reply.encode())

    def log_message(self, *args):
        pass


@pytest.fixture
def server():
    _FakeOllama.requests = list()
    httpd = http.server.HTTPServer(('127.0.0.1', 0), _FakeOllama)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()

    yield f'http://127.0.0.1:{httpd.server_port}'

    httpd.shutdown()
    httpd.server_close()


def _prompter(endpoint, system_prompt='Be brief.'):
    node = PrompterOllama(
        endpoint=endpoint,
        model_name='tiny',
        system_prompt=system_prompt,
        keep_alive='5m',
        think=False,
        timeout=5.0,
        node_name='llm',
        pipe_name='pipe',
    )
    node.sent = list()
    node.transmit = node.sent.append

    return node


def _ask(node, text):
    node.update(
        Message(creator='stt', payload=ObjectPayload.from_dict({'text': text}))
    )


def test_warmup_loads_the_model_with_an_empty_chat(server):
    _prompter(server).warmup()

    path, body = _FakeOllama.requests[0]
    assert path == '/api/chat'
    assert body['model'] == 'tiny'
    assert body['messages'] == []


def test_answer_is_transmitted_with_its_prompt(server):
    node = _prompter(server)
    _ask(node, ' What is the capital of Italy? ')

    _, body = _FakeOllama.requests[0]
    assert body['messages'] == [
        {'role': 'system', 'content': 'Be brief.'},
        {'role': 'user', 'content': 'What is the capital of Italy?'},
    ]
    assert body['stream'] is False

    payload = node.sent[0].payload
    assert payload['prompt'] == 'What is the capital of Italy?'
    assert payload['text'] == 'answer to What is the capital of Italy?'


def test_empty_system_prompt_sends_only_the_question(server):
    node = _prompter(server, system_prompt='')
    _ask(node, 'Hi')

    assert _FakeOllama.requests[0][1]['messages'] == [
        {'role': 'user', 'content': 'Hi'}
    ]


def test_empty_text_sends_no_request(server):
    node = _prompter(server)
    _ask(node, '   ')

    assert _FakeOllama.requests == []
    assert node.sent == []


def test_unreachable_server_drops_the_message():
    node = _prompter('http://127.0.0.1:9')
    _ask(node, 'Hi')

    assert node.sent == []
