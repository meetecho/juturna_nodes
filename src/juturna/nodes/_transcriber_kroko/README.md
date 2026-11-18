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

## License

- **Server:** [kroko-onnx](https://github.com/kroko-ai/kroko-onnx),
  Apache-2.0. The node only talks to it over a websocket.
- **Weights:** the server loads the model you give it. The kroko-onnx README
  describes its community models as CC-BY-SA and also offers commercial
  models; the [Banafo/Kroko-ASR](https://huggingface.co/Banafo/Kroko-ASR)
  card declares `license: other` with its own `LICENSE` file. Check the
  licence of the model you deploy.
