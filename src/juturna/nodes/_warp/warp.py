"""
Warp Node

@ Author: Paolo Saviano
@ Email: psaviano@meetecho.com

Generic gRPC remote node using Juturna's protobuf messaging.
"""

import json

import grpc

from juturna.remotizer.c_protos import messaging_service_pb2_grpc

from juturna.remotizer.utils import (
    message_to_proto,
    create_envelope,
    deserialize_envelope,
)

from juturna.components import Message
from juturna.components import Node
from juturna.components import State


MAX_MESSAGE_LENGTH = 100 * 1024 * 1024

# a stateless request can be sent again safely: the state it carries is only
# replaced once a response arrives, so a retry starts from the same one
STATELESS_SERVICE_CONFIG = json.dumps(
    {
        'loadBalancingConfig': [{'round_robin': {}}],
        'methodConfig': [
            {
                'name': [
                    {'service': 'juturna.proto.messaging.MessagingService'}
                ],
                'retryPolicy': {
                    'maxAttempts': 3,
                    'initialBackoff': '0.1s',
                    'maxBackoff': '1s',
                    'backoffMultiplier': 2,
                    'retryableStatusCodes': ['UNAVAILABLE'],
                },
            }
        ],
    }
)


class Warp[T_Input, T_Output](Node[T_Input, T_Output]):
    """
    Type Parameters
    ---------------
    T_Input : TypeVar
        Input payload type (e.g., AudioPayload, ImagePayload)
    T_Output : TypeVar
        Output payload type (e.g., AudioPayload, ImagePayload)
    """

    def __init__(
        self,
        grpc_host: str,
        grpc_port: int,
        timeout: int,
        remote_config: dict,
        sticky: bool,
        **kwargs,
    ):
        """
        Parameters
        ----------
        grpc_host : str
            gRPC server hostname.
        grpc_port : int
            gRPC server port.
        timeout : int
            Timeout for gRPC calls in seconds.
        remote_config : dict
            Configuration of the remote node, sent with every request.
        sticky : bool
            True when the remote service is always the same one, and keeps
            the node state. False when the service can be any replica behind
            a load balancer, so the state travels with every request.
        kwargs : dict
            Supernode arguments.

        """
        super().__init__(**kwargs)

        self._grpc_host = grpc_host
        self._grpc_port = grpc_port
        self._timeout = timeout
        self._remote_config = remote_config
        self._sticky = sticky
        self.channel = None
        self._dropped_reported = False

        self.logger.info('warp node initialized')

    def warmup(self):
        """Warmup the node"""
        options = [
            ('grpc.max_send_message_length', MAX_MESSAGE_LENGTH),
            ('grpc.max_receive_message_length', MAX_MESSAGE_LENGTH),
        ]
        target = f'{self._grpc_host}:{self._grpc_port}'

        if not self._sticky:
            # every address of the host is a replica: spread the requests
            target = f'dns:///{target}'
            options += [
                ('grpc.service_config', STATELESS_SERVICE_CONFIG),
                ('grpc.enable_retries', 1),
            ]

        self.channel = grpc.insecure_channel(target, options=options)

        # Create stub: it stubs the remote service for the client-proxy;
        # it will be defined as MessagingServiceImpl on the server side
        self.stub = messaging_service_pb2_grpc.MessagingServiceStub(
            self.channel
        )

        self.logger.info(f'warmup node: {self.name}')

    def destroy(self):
        """Close the gRPC channel"""
        if self.channel is not None:
            self.channel.close()

    def update(self, message: Message[T_Input], **kwargs):
        """
        Send message via gRPC and wait for response

        The message can contain any payload type (T_Input). The response
        contains a message of type T_Output, which is transmitted, or none
        when the remote node kept the input without producing anything.

        Parameters
        ----------
        message : Message[T_Input]
            The message to send with input payload type.
        kwargs : dict
            State and more.

        """
        state: State = kwargs['state']

        try:
            if self._sticky:
                response = self._send_sticky(message, state)
            else:
                response = self._send(message, dict(state))
        except grpc.RpcError as e:
            self.logger.error(f'gRPC error: {e.code()} - {e.details()}')
            raise

        # replaced, not merged, or keys the remote node deleted would come back
        state.clear()
        state.update(response['state'] or dict())

        if response['message'] is not None:
            self.transmit(response['message'])

    def _send_sticky(self, message: Message, state: State) -> dict:
        try:
            return self._send(message, None)
        except grpc.RpcError as e:
            if e.code() != grpc.StatusCode.FAILED_PRECONDITION:
                raise

        # the service does not know this node (it restarted, or dropped an
        # idle state): it starts again from the copy kept here
        self.logger.info('remote service asked for the state, sending it')

        return self._send(message, dict(state))

    def _send(self, message: Message, state: dict | None) -> dict:
        dropped = list()
        envelope = create_envelope(
            message=message_to_proto(message, dropped),
            creator=self.name,
            pipe_id=self.pipe_id,
            state=state,
            priority=0,
            timeout=self._timeout,
            configuration=self._remote_config,
            metadata={},
            stateless=not self._sticky,
            dropped=dropped,
        )

        self._warn_dropped(dropped)

        self.logger.debug(f'sending message {message.id} ({envelope.id})')

        response = deserialize_envelope(
            self.stub.SendAndReceive(envelope, timeout=self._timeout)
        )

        if response['stateless'] == self._sticky:
            raise RuntimeError(
                f'remote service {self._grpc_host}:{self._grpc_port} does '
                'not support the sticky option: upgrade it'
            )

        return response

    def _warn_dropped(self, dropped: list[str]):
        # reported once: paths holding keys or indices are always new
        if dropped and not self._dropped_reported:
            self._dropped_reported = True
            self.logger.warning(
                f'{", ".join(dropped)} cannot be sent, left out'
            )
