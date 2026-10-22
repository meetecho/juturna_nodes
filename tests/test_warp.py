from concurrent import futures

import pytest

from juturna.components import Message, Node, State
from juturna.payloads import ObjectPayload

grpc = pytest.importorskip('grpc')

from juturna.cli.commands._juturna_remote_service import (  # noqa: E402
    MessagingServiceImpl,
)
from juturna.nodes import Warp  # noqa: E402
from juturna.remotizer.c_protos import messaging_service_pb2_grpc  # noqa: E402
from juturna.remotizer.utils import create_envelope  # noqa: E402


class Accumulator(Node):
    """Keep values in state['pending'], transmit their sum every 3."""

    def update(self, message, state=None):
        n = message.payload['n']

        if n == 0:
            state['ids'] = {1, 2}  # a set cannot be sent back
        if n == -1:
            state.pop('scratch', None)
        else:
            state['scratch'] = n

        pending = state.setdefault('pending', list())
        pending.append(n)

        if len(pending) < 3:
            return

        self.transmit(
            Message(creator=self.name, payload=ObjectPayload(sum=sum(pending)))
        )
        pending.clear()


class Service:
    """A remote service with its own node, on a local port."""

    def __init__(self):
        self.node = Accumulator(node_name='acc', pipe_name='remote')
        self.node.start()
        self.impl = MessagingServiceImpl(self.node, remote_name='remote')
        self.server = grpc.server(futures.ThreadPoolExecutor(max_workers=4))
        messaging_service_pb2_grpc.add_MessagingServiceServicer_to_server(
            self.impl, self.server
        )
        self.port = self.server.add_insecure_port('127.0.0.1:0')
        self.server.start()

    def close(self):
        self.server.stop(None)
        self.impl.shutdown()
        self.node.kill()


@pytest.fixture
def services():
    started = [Service(), Service()]

    yield started

    for service in started:
        service.close()


def _warp(port, sticky):
    warp = Warp(
        grpc_host='127.0.0.1',
        grpc_port=port,
        timeout=5,
        remote_config={},
        sticky=sticky,
        node_name='warp',
        pipe_name='pipe',
    )
    warp.pipe_id = 'pipe-1'
    warp.sent = list()
    warp.transmit = warp.sent.append
    warp.warmup()

    return warp


def _send(warp, state, n, port=None):
    if port is not None:  # the next request reaches another service
        warp.destroy()
        warp._grpc_port = port
        warp.warmup()

    warp.update(
        Message(creator='src', payload=ObjectPayload(n=n)), state=state
    )


def test_sticky_warp_sends_its_state_only_when_asked(services):
    service = services[0]
    warp = _warp(service.port, sticky=True)
    state = State()

    for n in (1, 2, 3):
        _send(warp, state, n)

    # asked once, for the first request only
    assert service.impl.get_stats()['unknown_client_requests'] == 1
    assert [m.payload['sum'] for m in warp.sent] == [6]
    assert dict(state) == {'pending': [], 'scratch': 3}

    warp.destroy()


def test_sticky_warp_recovers_after_a_service_restart(services):
    first, restarted = services
    warp = _warp(first.port, sticky=True)
    state = State()

    _send(warp, state, 1)
    _send(warp, state, 2)
    _send(warp, state, 3, port=restarted.port)

    assert [m.payload['sum'] for m in warp.sent] == [6]
    assert restarted.impl.get_stats()['unknown_client_requests'] == 1

    warp.destroy()


def test_sticky_state_that_cannot_be_sent_is_copied_without_it(services):
    warp = _warp(services[0].port, sticky=True)
    state = State()

    _send(warp, state, 1)
    _send(warp, state, 0)

    assert dict(state) == {'pending': [1, 0], 'scratch': 0}

    _send(warp, state, 2)

    assert [m.payload['sum'] for m in warp.sent] == [3]

    warp.destroy()


def test_input_values_that_cannot_be_sent_are_left_out(services, caplog):
    warp = _warp(services[0].port, sticky=False)
    state = State()

    for n in (1, 2):
        message = Message(creator='src', payload=ObjectPayload(n=n))
        message.meta[f'ids_{n}'] = {n}  # a new path for every message
        warp.update(message, state=state)

    assert state['pending'] == [1, 2]
    warnings = [r for r in caplog.records if 'cannot be sent' in r.message]
    assert len(warnings) == 1, [r.message for r in warnings]
    assert "message.meta['ids_1'] (set)" in warnings[0].message

    warp.destroy()


def test_stateless_warp_can_reach_any_replica(services):
    warp = _warp(services[0].port, sticky=False)
    state = State()

    for n in range(1, 7):
        _send(warp, state, n, port=services[n % 2].port)

    assert [m.payload['sum'] for m in warp.sent] == [6, 15]
    assert all(service.impl._state_store == {} for service in services)

    warp.destroy()


def test_stateless_warp_drops_the_keys_the_remote_node_deleted(services):
    warp = _warp(services[0].port, sticky=False)
    state = State()

    _send(warp, state, 1)
    assert state['scratch'] == 1

    _send(warp, state, -1)
    assert 'scratch' not in state

    warp.destroy()


def test_stateless_warp_refuses_a_service_without_the_option():
    warp = Warp(
        grpc_host='old',
        grpc_port=1,
        timeout=5,
        remote_config={},
        sticky=False,
        node_name='warp',
        pipe_name='pipe',
    )
    warp.pipe_id = 'pipe-1'

    class OldService:
        def SendAndReceive(self, envelope, timeout):
            return create_envelope(
                message=None,
                configuration={},
                metadata={},
                creator='remote',
                pipe_id='pipe-1',
                state=None,
            )

    warp.stub = OldService()

    with pytest.raises(RuntimeError, match='does not support the sticky'):
        _send(warp, State(), 1)


def test_stateless_warp_retries_an_unavailable_service(services):
    calls = list()
    service = services[0]

    class Flaky(messaging_service_pb2_grpc.MessagingServiceServicer):
        def SendAndReceive(self, request, context):
            calls.append(request.id)

            if len(calls) == 1:
                context.abort(grpc.StatusCode.UNAVAILABLE, 'going down')

            return service.impl.SendAndReceive(request, context)

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=2))
    messaging_service_pb2_grpc.add_MessagingServiceServicer_to_server(
        Flaky(), server
    )
    port = server.add_insecure_port('127.0.0.1:0')
    server.start()

    warp = _warp(port, sticky=False)
    state = State()

    try:
        _send(warp, state, 1)
    finally:
        warp.destroy()
        server.stop(None)

    assert len(calls) == 2 and calls[0] == calls[1], 'request not retried'
    assert dict(state) == {'pending': [1], 'scratch': 1}
