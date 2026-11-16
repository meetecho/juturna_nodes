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

The node does not download models. Download a streaming transducer model
from the sherpa-onnx releases and point `model_dir` at its folder, for
example the English zipformer (Apache-2.0, 68 MB for the int8 files):

```console
curl -LO https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-streaming-zipformer-en-2023-06-26.tar.bz2
tar xjf sherpa-onnx-streaming-zipformer-en-2023-06-26.tar.bz2
```

The folder must hold `tokens.txt` and one `encoder*.onnx`, `decoder*.onnx`
and `joiner*.onnx` file each; when both are present, the `.int8.` files are
used.

## Arguments

| Argument               | Type    | Default | Description                                         |
| ---------------------- | ------- | ------- | --------------------------------------------------- |
| `model_dir`            | `str`   | `""`    | Folder of the streaming transducer model            |
| `num_threads`          | `int`   | `2`     | CPU threads used by the recognizer                  |
| `min_trailing_silence` | `float` | `0.8`   | Seconds of silence after speech that close a sentence |

## Input message

| Field | Use |
| --- | --- |
| `payload.audio` | Mono `float32` samples in `[-1, 1]`, required |
| `payload.sampling_rate` | Rate of `audio`, required; resampled to the model rate internally |

`meta` is not read. The node keeps one recognition stream for all the
messages it receives, so it expects a single audio source. The last sentence
is only transmitted after enough silence: a file that ends while someone is
talking loses its last sentence.

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
  "configuration": {
    "model_dir": "./models/sherpa-onnx-streaming-zipformer-en-2023-06-26"
  }
}
```
