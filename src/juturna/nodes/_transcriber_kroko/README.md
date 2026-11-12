# TranscriberKroko

> **Experimental.** This node is a work in progress: its arguments and its
> output format may change in any release, without a major version bump.

Transcribe audio with a [kroko-onnx](https://github.com/kroko-ai/kroko-onnx)
server, reached over a websocket.

- **Role:** processing
- **Node type:** `TranscriberKroko`
- **Input:** `AudioPayload`
- **Output:** `ObjectPayload`
- **Extra:** none

## Arguments

| Argument | Type  | Default               | Description                       |
| -------- | ----- | --------------------- | --------------------------------- |
| `ws`     | `str` | `ws://localhost:6006` | Websocket URL of the Kroko server |
