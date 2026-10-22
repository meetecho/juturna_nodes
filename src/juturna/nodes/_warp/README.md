# warp

Client of a node that runs remotely, behind `python -m juturna remotize`.

## Node type: proc

## Node class name: Warp

## Node name: warp

## How it works

A pipeline never lists `Warp` itself: a node with `"warped": true` is
replaced by a `Warp` whose arguments come from `warp_configuration`, and
whose `remote_config` is the configuration of the replaced node.

For every message, `update()` sends one gRPC request to the remote service
and waits for its response, so messages are processed one at a time, in
order. The remote service answers when the remote node's `update()` returns:
with the first message it transmitted, or with none.

The `sticky` flag of the warped node (default `true`) tells where the remote
node state lives:

- **sticky**: the service keeps the state. The warp node sends no state,
  unless the service answers `FAILED_PRECONDITION` because it does not know
  this node (it restarted, or dropped an idle state): then the request is
  sent again with the copy kept by the warp node, and the service starts
  again from it. Each response carries the updated copy.
- **not sticky**: the service keeps nothing, so `grpc_host` can be a load
  balancer, or a name that resolves to several replicas. The state travels
  with every request and is replaced by the one in the response. Requests
  are spread over all the addresses of `grpc_host` (`round_robin`), and a
  request that fails with `UNAVAILABLE` is sent again, up to 3 attempts.

A response from a service that does not support the `sticky` option raises
`RuntimeError`.

Values of types the remote protocol cannot carry are left out of what is
sent, and reported with a single warning that lists their paths, once by this
node and once for each client by the remote service. A service started with `--strict` fails the request
with `DATA_LOSS` instead: the update fails, is counted in the node health, and
the next message goes on.

## Arguments

- `grpc_host` (`"localhost"`): host of the remote service.
- `grpc_port` (`50080`): port of the remote service.
- `timeout` (`30`): seconds to wait for each response.
- `sticky` (`true`): see above. Set by the `sticky` key of the warped node,
  not inside `warp_configuration`.
- `remote_config` (`{}`): configuration of the remote node, sent with every
  request. The service is configured once, when it starts, and only logs a
  warning about it.

## Input message

Any message, sent unchanged to the remote node: every payload type is
supported. `meta` and `ObjectPayload` values of types the remote protocol
cannot carry are left out (it carries `None`, booleans, numbers, strings,
bytes, lists, tuples, frozensets, dicts, numpy arrays and scalars, messages).

## Output message

The message transmitted by the remote node, forwarded unchanged: its payload,
`creator`, `version` and `meta` are the remote node's. Nothing is transmitted
when the remote node kept the input without producing a message.

## State

The warp node state is the copy of the remote node state, as described
above, without the values the remote protocol cannot carry.

## Extra

`warp` (`pip install "juturna-nodes[warp]"`). The remote service must run a
juturna version with the same remote protocol.

## Example

```json
{
  "name": "transcriber",
  "type": "TranscriberWhisper",
  "configuration": { "model_name": "large-v3" },
  "warped": true,
  "sticky": false,
  "warp_configuration": {
    "grpc_host": "transcribers.internal",
    "grpc_port": 45000,
    "timeout": 10
  }
}
```
