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

The node supports the Kitten and Kokoro model families of the sherpa-onnx
releases. Since sherpa-onnx 2.0 these models need a pronunciation lexicon.

By default the node downloads on first use:

- Kitten nano int8 (Apache-2.0): `model.int8.onnx`, `voices.bin` and
  `tokens.txt`, 28 MB, from the
  [Hugging Face repository](https://huggingface.co/csukuangfj2/kitten-nano-en-v0_8-int8)
  at a pinned revision;
- when `lexicon` is empty, `lexicon-en-us.txt` (6.3 MB) from the
  [`tts-models` release](https://github.com/k2-fsa/sherpa-onnx/releases/tag/tts-models)
  of sherpa-onnx.

Each file is checked against its size and SHA-256 on download. The files are
kept in `~/.cache/juturna/models/<model>/` (or under `$XDG_CACHE_HOME`), and
later runs reuse them after checking their size.

The lexicon is not distributed with this package: the node downloads it from
the sherpa-onnx release. Its header says it was generated from CMUdict and
an `en_list` word list; the sherpa-onnx release states no license for it.

To use a model you already have, for example Kokoro, set `model_dir` to its
folder and `model_type` to its family; `model` is then ignored.

Words missing from the lexicon are skipped, which includes most names.
Measured on CPU with 2 threads, Kitten nano int8 (Apache-2.0, 28 MB) speaks
5.6 s of audio in about 1.8 s; Kokoro int8 (Apache-2.0, 140 MB) has a more
natural voice but is slower than real time.

## Arguments

| Argument      | Type    | Default    | Description |
| ------------- | ------- | ---------- | ----------- |
| `model`       | `str`   | `"kitten-nano-en-v0_8-int8"` | Model downloaded into the cache; the only known one is the default |
| `model_dir`   | `str`   | `""`       | Model folder, holding one ONNX file, `voices.bin` and `tokens.txt`, used instead of `model` |
| `model_type`  | `str`   | `"kitten"` | Model family: `kitten` or `kokoro` |
| `lexicon`     | `str`   | `""`       | Pronunciation lexicon file; empty to download `lexicon-en-us.txt` |
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

## License

- **Weights:** the default model is downloaded from
  [csukuangfj2/kitten-nano-en-v0_8-int8](https://huggingface.co/csukuangfj2/kitten-nano-en-v0_8-int8),
  whose card states no licence; it is converted from
  [KittenML/kitten-tts-nano-0.8-int8](https://huggingface.co/KittenML/kitten-tts-nano-0.8-int8),
  Apache-2.0 on its model card. With `model_dir`, the licence is the one of
  the model you use.
- **Lexicon:** `lexicon-en-us.txt` comes from the sherpa-onnx
  [`tts-models` release](https://github.com/k2-fsa/sherpa-onnx/releases/tag/tts-models);
  no source we found states its licence.
- **Runtime:** [sherpa-onnx](https://github.com/k2-fsa/sherpa-onnx), Apache-2.0.

## Example

```json
{
  "name": "tts",
  "type": "SynthesizerSherpa",
  "configuration": {}
}
```
