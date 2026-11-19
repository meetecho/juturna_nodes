# PassthroughIdentity

Forward every received message unchanged, after a fixed delay. This is a test
node, useful to try out a pipeline or to simulate a slow processing step.

- **Role:** processing
- **Node type:** `PassthroughIdentity`
- **Input:** any payload
- **Output:** the same payload as the input
- **Extra:** none

The forwarded message keeps the version, the payload, the `meta` and the
timers of the input message, and records the wait in a `<node name>_delay`
timer.

## Arguments

| Argument | Type  | Default | Description                                        |
| -------- | ----- | ------- | -------------------------------------------------- |
| `delay`  | `int` | `1`     | Seconds to wait before forwarding each message     |

## License

- **Code:** this node is part of juturna-nodes, MIT (its `LICENSE` file).
- **Third-party runtime:** none beyond the juturna core (MIT); the node
  uses the Python standard library.

## Example

```json
{
  "name": "delay",
  "type": "PassthroughIdentity",
  "configuration": { "delay": 2 }
}
```
