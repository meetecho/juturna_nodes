# TranscriberSherpa

Streaming speech recognition with [sherpa-onnx](https://github.com/k2-fsa/sherpa-onnx),
on CPU and without torch. The node feeds every audio chunk to a streaming
transducer model and transmits one message for each sentence, when it detects
the end of speech (`min_trailing_silence` seconds of silence). Partial
results are not transmitted.

- **Role:** processing
- **Node type:** `TranscriberSherpa`
- **Input:** `AudioPayload`
- **Output:** `ObjectPayload`
- **Extra:** `sherpa`

```console
pip install "juturna-nodes[sherpa]"
```

## Model

By default the node downloads the English streaming zipformer (Apache-2.0)
on first use: the int8 encoder, decoder and joiner and `tokens.txt`, 73 MB,
from the [Hugging Face repository](https://huggingface.co/csukuangfj/sherpa-onnx-streaming-zipformer-en-2023-06-26)
at a pinned revision. Each file is checked against its size and SHA-256 on
download. The files are kept in `~/.cache/juturna/models/<model>/` (or
under `$XDG_CACHE_HOME`), and later runs reuse them after checking their size.

To use a model you already have, set `model_dir` to its folder; `model` is
then ignored. The folder must hold `tokens.txt` and one `encoder*.onnx`,
`decoder*.onnx` and `joiner*.onnx` file each; when both are present, the
`.int8.` files are used.

## Arguments

| Argument               | Type    | Default | Description                                         |
| ---------------------- | ------- | ------- | --------------------------------------------------- |
| `model`                | `str`   | `"sherpa-onnx-streaming-zipformer-en-2023-06-26"` | Model downloaded into the cache; the only known one is the default |
| `model_dir`            | `str`   | `""`    | Folder of a streaming transducer model, used instead of `model` |
| `num_threads`          | `int`   | `2`     | CPU threads used by the recognizer                  |
| `min_trailing_silence` | `float` | `0.8`   | Seconds of silence after speech that close a sentence |

## Input message

| Field | Use |
| --- | --- |
| `payload.audio` | Mono `float32` samples in `[-1, 1]`, required |
| `payload.sampling_rate` | Rate of `audio`, required; resampled to the model rate internally |

`meta` is not read. The node keeps one recognition stream for all the
messages it receives, so it expects a single audio source. A sentence is
transmitted after enough silence, or when the node stops: when the pipeline
is stopped, the sentence still open is transmitted to the next nodes, which
are stopped after it. An audio source that stops sending while the pipeline
keeps running (a caller hanging up, for example) leaves the sentence open
until more audio comes.

## Output message

| Field | Content |
| --- | --- |
| `payload['text']` | The sentence, in lower case, without punctuation |
| `payload['transcript']` | List of words, each `{'word', 'start', 'end'}`: `word` starts with a space (as in `TranscriberWhisper`), `start` and `end` are seconds from the start of the stream |

The message keeps the version and the timers of the audio message that closed
the sentence. `meta` is empty.

## Example

```json
{
  "name": "stt",
  "type": "TranscriberSherpa",
  "configuration": {}
}
```
