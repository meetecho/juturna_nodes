import http.server
import json
import threading
import time

import pytest

from juturna.components import Message
from juturna.nodes import PrompterOllama
from juturna.payloads import ObjectPayload


class _FakeOllama(http.server.BaseHTTPRequestHandler):
    """Ollama /api/chat: one JSON answer, or NDJSON chunks when streaming"""

    requests = list()
    completed = list()
    # per request: pieces of the answer, seconds between them, how it ends
    pieces = ['Hello there.']
    gap = 0.0
    delay = 0.0
    status = 200
    ending = 'done'  # 'done', 'error' or 'drop'

    def do_POST(self):  # noqa: N802
        body = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
        time.sleep(_FakeOllama.delay)
        _FakeOllama.requests.append((self.path, body))

        self.send_response(_FakeOllama.status)
        self.send_header('Content-Type', 'application/x-ndjson')
        self.end_headers()

        if not body['stream']:
            self._line({'message': {'content': ''.join(self.pieces)}})

            return

        try:
            for piece in _FakeOllama.pieces:
                self._line({'message': {'content': piece}, 'done': False})
                time.sleep(_FakeOllama.gap)

            if _FakeOllama.ending == 'error':
                self._line({'error': 'model crashed'})
            elif _FakeOllama.ending == 'done':
                self._line({'message': {'content': ''}, 'done': True})
        except OSError:
            return

        _FakeOllama.completed.append(body['messages'][-1]['content'])

    def _line(self, chunk):
        self.wfile.write(json.dumps(chunk).encode() + b'\n')
        self.wfile.flush()

    def log_message(self, *args):
        pass


@pytest.fixture
def server():
    _FakeOllama.requests = list()
    _FakeOllama.completed = list()
    _FakeOllama.pieces = ['Hello there.']
    _FakeOllama.gap = 0.0
    _FakeOllama.delay = 0.0
    _FakeOllama.status = 200
    _FakeOllama.ending = 'done'
    httpd = http.server.ThreadingHTTPServer(('127.0.0.1', 0), _FakeOllama)
    httpd.daemon_threads = True
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()

    yield f'http://127.0.0.1:{httpd.server_port}'

    httpd.shutdown()
    httpd.server_close()


@pytest.fixture
def started():
    nodes = list()

    def _start(node):
        node.start()
        nodes.append(node)

        return node

    yield _start

    for node in nodes:
        node.kill()


def _prompter(endpoint, system_prompt='Be brief.', timeout=5.0, stream=True):
    node = PrompterOllama(
        endpoint=endpoint,
        model_name='tiny',
        system_prompt=system_prompt,
        keep_alive='5m',
        think=False,
        timeout=timeout,
        stream=stream,
        node_name='llm',
        pipe_name='pipe',
    )
    node.sent = list()
    node.transmit = node.sent.append

    return node


def _ask(node, text):
    question = Message(
        creator='stt', payload=ObjectPayload.from_dict({'text': text})
    )
    node.put(question)

    return question


def _wait(condition, seconds=3.0):
    deadline = time.monotonic() + seconds

    while not condition():
        assert time.monotonic() < deadline, 'condition not met in time'
        time.sleep(0.01)


def _final(node):
    return any(m.meta['final'] for m in node.sent)


def _texts(node):
    return [m.payload['text'] for m in node.sent]


def test_warmup_loads_the_model_with_an_empty_chat(server):
    _prompter(server).warmup()

    path, body = _FakeOllama.requests[0]
    assert path == '/api/chat'
    assert body['model'] == 'tiny'
    assert body['messages'] == []
    assert body['stream'] is False


def test_warmup_waits_for_a_slow_model_load(server, started):
    _FakeOllama.delay = 0.5
    node = _prompter(server, timeout=0.2)

    node.warmup()
    # the answers keep their timeout
    started(node)
    _ask(node, 'Hi')
    _wait(lambda: node.health['source_failures'] == 1)

    assert node.sent == []


def test_answer_is_transmitted_sentence_by_sentence(server, started):
    _FakeOllama.pieces = [
        'Rome is the capital',
        ' of Italy. It is',
        ' a big city with ',
        'a long history. Ok',
    ]
    node = started(_prompter(server))
    question = _ask(node, ' What is the capital of Italy? ')
    _wait(lambda: _final(node))

    _, body = _FakeOllama.requests[0]
    assert body['stream'] is True
    assert body['messages'] == [
        {'role': 'system', 'content': 'Be brief.'},
        {'role': 'user', 'content': 'What is the capital of Italy?'},
    ]

    assert _texts(node) == [
        'Rome is the capital of Italy.',
        'It is a big city with a long history.',
        'Ok',
    ]
    assert [dict(m.meta) for m in node.sent] == [
        {'turn': question.id, 'sequence': i, 'final': i == 2, 'source': 'stt'}
        for i in range(3)
    ]
    assert {m.payload['prompt'] for m in node.sent} == {
        'What is the capital of Italy?'
    }
    assert all(m.timers['llm'] > 0 for m in node.sent)


def test_short_pieces_join_the_next_and_decimals_are_not_split(server, started):
    _FakeOllama.pieces = ['Yes. It costs 3.', '5 euros in total. ', 'Bye.']
    node = started(_prompter(server))
    _ask(node, 'How much?')
    _wait(lambda: _final(node))

    assert _texts(node) == ['Yes. It costs 3.5 euros in total.', 'Bye.']


def test_without_stream_the_whole_answer_is_one_message(server, started):
    _FakeOllama.pieces = ['Rome is the capital of Italy. ', 'It is big.']
    node = started(_prompter(server, stream=False))
    _ask(node, 'Capital?')
    _wait(lambda: _final(node))

    assert _texts(node) == ['Rome is the capital of Italy. It is big.']
    assert node.sent[0].meta['sequence'] == 0


def test_empty_system_prompt_sends_only_the_question(server, started):
    node = started(_prompter(server, system_prompt=''))
    _ask(node, 'Hi')
    _wait(lambda: _final(node))

    assert _FakeOllama.requests[0][1]['messages'] == [
        {'role': 'user', 'content': 'Hi'}
    ]


def test_empty_text_sends_no_request(server, started):
    node = started(_prompter(server))
    _ask(node, '   ')
    time.sleep(0.3)

    assert _FakeOllama.requests == []
    assert node.sent == []


def test_a_new_question_interrupts_the_current_answer(server, started):
    _FakeOllama.pieces = [f'This is sentence number {i}. ' for i in range(30)]
    _FakeOllama.gap = 0.05
    node = started(_prompter(server))
    first = _ask(node, 'first')
    _wait(lambda: node.sent)

    _FakeOllama.pieces = ['The second answer is short.']
    _FakeOllama.gap = 0.0
    second = _ask(node, 'second')
    _wait(lambda: _final(node))

    turns = [m.meta['turn'] for m in node.sent]
    switch = turns.index(second.id)
    assert set(turns[:switch]) == {first.id}
    assert set(turns[switch:]) == {second.id}
    assert switch < 30
    # the old connection was closed: the server fails to write the rest
    time.sleep(30 * 0.05)
    assert _FakeOllama.completed == ['second']


def test_stop_drops_the_answer_in_progress(server, started):
    _FakeOllama.pieces = [f'This is sentence number {i}. ' for i in range(30)]
    _FakeOllama.gap = 0.05
    node = started(_prompter(server))
    _ask(node, 'long')
    _wait(lambda: node.sent)

    begin = time.monotonic()
    node.stop()

    assert time.monotonic() - begin < 1.0

    sent = len(node.sent)
    node.start()
    time.sleep(30 * 0.05)

    assert len(node.sent) == sent
    assert not _final(node)
    assert _FakeOllama.completed == []


def test_stop_does_not_wait_for_a_sentence(server, started):
    # chunks without text, like a model that is thinking
    _FakeOllama.pieces = [''] * 100
    _FakeOllama.gap = 0.05
    node = started(_prompter(server))
    _ask(node, 'think')
    _wait(lambda: _FakeOllama.requests)
    time.sleep(0.2)

    begin = time.monotonic()
    node.stop()

    assert time.monotonic() - begin < 1.0


@pytest.mark.parametrize(
    ('status', 'ending', 'sent'),
    [
        (500, 'done', []),
        (200, 'error', ['The first sentence is here.']),
        (200, 'drop', ['The first sentence is here.']),
    ],
)
def test_failed_answers_are_counted_and_the_next_one_works(
    server, started, status, ending, sent
):
    _FakeOllama.status = status
    _FakeOllama.ending = ending
    _FakeOllama.pieces = ['The first sentence is here. ', 'And a partial']
    node = started(_prompter(server))
    _ask(node, 'broken')
    # the worker transmits the sentences after the source has failed
    _wait(
        lambda: (
            node.health['source_failures'] == 1 and len(node.sent) == len(sent)
        )
    )

    assert _texts(node) == sent

    _FakeOllama.status = 200
    _FakeOllama.ending = 'done'
    _FakeOllama.pieces = ['Fine now.']
    _ask(node, 'again')
    _wait(lambda: _final(node))

    assert _texts(node)[-1] == 'Fine now.'


def test_unreachable_server_drops_the_question(started):
    node = started(_prompter('http://127.0.0.1:9'))
    _ask(node, 'Hi')
    _wait(lambda: node.health['source_failures'] == 1)

    assert node.sent == []
