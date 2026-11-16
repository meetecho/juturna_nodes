# SynthesizerSherpa

Text to speech with [sherpa-onnx](https://github.com/k2-fsa/sherpa-onnx), on
CPU and without torch: the text of each message becomes one audio message.

- **Role:** processing
- **Node type:** `SynthesizerSherpa`
- **Input:** `ObjectPayload`
- **Output:** `AudioPayload`
- **Extra:** `sherpa`

```console
pip install "juturna-nodes[sherpa]"
```

## Model and lexicon

The node does not download models. It supports the Kitten and Kokoro model
families of the sherpa-onnx releases. Since sherpa-onnx 2.0 these models
need a pronunciation lexicon, a separate download:

```console
curl -LO https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/kitten-nano-en-v0_8-int8.tar.bz2
tar xjf kitten-nano-en-v0_8-int8.tar.bz2
curl -LO https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/lexicon-en-us.txt
```

Words missing from the lexicon are skipped, which includes most names.
Measured on CPU with 2 threads, Kitten nano int8 (Apache-2.0, 29 MB) speaks
5.6 s of audio in about 1.8 s; Kokoro int8 (Apache-2.0, 98 MB) has a more
natural voice but is slower than real time.

## Arguments

| Argument      | Type    | Default    | Description |
| ------------- | ------- | ---------- | ----------- |
| `model_dir`   | `str`   | `""`       | Model folder, holding one ONNX file, `voices.bin` and `tokens.txt` |
| `model_type`  | `str`   | `"kitten"` | Model family: `kitten` or `kokoro` |
| `lexicon`     | `str`   | `""`       | Pronunciation lexicon file, such as `lexicon-en-us.txt` |
| `speaker_id`  | `int`   | `0`        | Voice to use, among the voices of the model |
| `speed`       | `float` | `1.0`      | Speech speed, 1.0 being the natural speed of the voice |
| `num_threads` | `int`   | `2`        | CPU threads used by the model |

## Input message

| Field | Use |
| --- | --- |
| `payload['text']` | The text to speak, required. An empty or missing text is ignored |

`meta` is not read. `PrompterOllama` produces this format.

## Output message

| Field | Content |
| --- | --- |
| `payload.audio` | Mono `float32` samples in `[-1, 1]` |
| `payload.sampling_rate` | Rate of the model (24000 Hz for Kitten and Kokoro) |
| `payload.channels` | `1` |
| `payload.start`, `payload.end` | `0.0` and the duration of the audio, in seconds |
| `meta['text']` | The text that was spoken |

The message keeps the version and the timers of the input message, and adds
a `<node name>` timer with the synthesis time. If the model produces no audio
(for example, every word is missing from the lexicon), a warning is logged
and nothing is transmitted.

## Example

```json
{
  "name": "tts",
  "type": "SynthesizerSherpa",
  "configuration": {
    "model_dir": "./models/kitten-nano-en-v0_8-int8",
    "lexicon": "./models/lexicon-en-us.txt"
  }
}
```
