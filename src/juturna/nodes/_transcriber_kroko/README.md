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
- **websockets:** BSD-3-Clause (the `License-Expression` of websockets on
  PyPI), to reach the server.
- **Weights:** the server loads the model you give it. The
  [Banafo/Kroko-ASR](https://huggingface.co/Banafo/Kroko-ASR) model card
  describes its Community models as "Licensed under CC-BY-SA", without a
  version, and also offers commercial models. Its metadata declares
  `license: other` with `license_link: LICENSE`, but that `LICENSE` file is
  empty (0 bytes, checked on 2026-11-18), so no license text is published
  with the weights. Check the license of the model you deploy with Kroko.
