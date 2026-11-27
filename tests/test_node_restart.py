import http.server
import json
import threading
import time

import pytest

from juturna.components import State
from juturna.utils.net_utils import get_available_port


def _wait_for(condition, timeout=5):
    deadline = time.monotonic() + timeout

    while time.monotonic() < deadline:
        if condition():
            return True

        time.sleep(0.05)

    return False


def _capture(node):
    node.link_state(State())
    node.sent = list()
    node.transmit = node.sent.append

    return node


def test_video_rtp_worker_runs_after_restart(tmp_path):
    pytest.importorskip('av')
    from juturna.nodes import VideoRtp

    node = VideoRtp(
        rec_host='127.0.0.1',
        rec_port=get_available_port(),
        payload_type=96,
        codec='VP8',
        encoding_clock_chan=90000,
        node_name='video',
        pipe_name='pipe',
    )
    node.pipe_path = str(tmp_path)
    # shortcut: an idle av.open blocks stop() for ~11 s, so the stream loop
    # is replaced by a wait on the node stop event
    node._generate_chunks = node._stop_event.wait
    node.stop()
    node.warmup()
    node.start()
    node.stop()
    node.start()

    try:
        # a stale stop event would end the worker at once
        assert not _wait_for(lambda: not node._t.is_alive(), timeout=0.5)
    finally:
        started = time.monotonic()
        node.stop()
        node.stop()

        assert time.monotonic() - started < 5


def test_notifier_http_sends_after_restart(tmp_path):
    pytest.importorskip('requests')
    from juturna.components import Message
    from juturna.nodes import NotifierHTTP
    from juturna.payloads import ObjectPayload

    received = list()

    class _Handler(http.server.BaseHTTPRequestHandler):
        def do_POST(self):  # noqa: N802
            length = int(self.headers['Content-Length'])
            received.append(json.loads(self.rfile.read(length)))
            self.send_response(200)
            self.end_headers()

        def log_message(self, *args):
            pass

    server = http.server.HTTPServer(('127.0.0.1', 0), _Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()

    node = NotifierHTTP(
        endpoint=f'http://127.0.0.1:{server.server_port}',
        timeout=2,
        content_type='application/json',
        node_name='http',
        pipe_name='pipe',
    )
    node.stop()

    def _message(n):
        return Message[ObjectPayload](
            creator='src',
            version=n,
            payload=ObjectPayload.from_dict({'n': n}),
        )

    try:
        node.warmup()
        node.start()
        node.put(_message(1))
        assert _wait_for(lambda: len(received) == 1)

        node.stop()
        node.start()
        node.put(_message(2))
        assert _wait_for(lambda: len(received) == 2)
    finally:
        node.stop()
        node.stop()
        server.shutdown()


def test_json_websocket_receives_after_restart():
    pytest.importorskip('websockets')
    from websockets.sync.client import connect

    from juturna.nodes import JsonWebsocket

    port = get_available_port()
    node = _capture(
        JsonWebsocket(
            rtx_host='127.0.0.1',
            rtx_port=port,
            node_name='ws',
            pipe_name='pipe',
        )
    )
    node.stop()

    def _send(n):
        with connect(f'ws://127.0.0.1:{port}', open_timeout=2) as ws:
            ws.send(json.dumps({'n': n}))

    try:
        node.warmup()
        node.start()
        _send(1)
        assert _wait_for(lambda: len(node.sent) == 1)

        node.stop()
        node.start()
        _send(2)
        assert _wait_for(lambda: len(node.sent) == 2)
    finally:
        node.stop()
        node.stop()


def test_file_watcher_fires_after_restart(tmp_path):
    pytest.importorskip('watchdog')
    from juturna.nodes import FileWatcher

    node = _capture(
        FileWatcher(
            location=str(tmp_path),
            pattern='*',
            recursive=False,
            ignore_directories=True,
            ignore_updates=True,
            ignore_deletions=True,
            node_name='watcher',
            pipe_name='pipe',
        )
    )
    node.stop()

    try:
        node.warmup()
        node.start()
        (tmp_path / 'one').touch()
        assert _wait_for(lambda: len(node.sent) == 1)

        node.stop()
        node.start()
        (tmp_path / 'two').touch()
        assert _wait_for(lambda: len(node.sent) == 2)
    finally:
        node.stop()
        node.stop()


def test_json_http_receives_after_double_stop_and_restart():
    requests = pytest.importorskip('requests')
    from juturna.nodes import JsonHTTP

    port = get_available_port()
    node = _capture(
        JsonHTTP(
            host='127.0.0.1',
            port=port,
            endpoint='in',
            node_name='http_in',
            pipe_name='pipe',
        )
    )
    node.stop()

    def _post(n):
        requests.post(
            f'http://127.0.0.1:{port}/in', json={'n': n}, timeout=2
        ).raise_for_status()

    try:
        node.warmup()
        node.start()
        _post(1)
        assert _wait_for(lambda: len(node.sent) == 1)

        node.stop()
        node.stop()
        node.start()
        _post(2)
        assert _wait_for(lambda: len(node.sent) == 2)
    finally:
        node.destroy()
