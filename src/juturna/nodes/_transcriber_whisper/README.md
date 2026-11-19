# TranscriberWhisper

Transcribe audio with Whisper models, through
[faster-whisper](https://github.com/SYSTRAN/faster-whisper).

- **Role:** processing
- **Node type:** `TranscriberWhisper`
- **Input:** `AudioPayload`
- **Output:** `ObjectPayload`
- **Extra:** `audio-ml` (`pip install "juturna-nodes[audio-ml]"`)

## How it works

The node keeps the last `buffer_size` audio messages of each upstream node,
and transcribes the whole buffer every time a new message arrives. It is meant
to follow a `VadSilero` node:

- a message with `meta['silence']` set empties the buffer, and produces an
  empty transcript;
- the `meta['speech_timestamps']` of the buffered messages are used to map
  word timestamps back to the original audio timeline.

Each message triggers one transcription of the whole buffer: the audio of the
last `buffer_size` messages from that upstream node, concatenated. Every chunk
is therefore transcribed up to `buffer_size` times, and once the buffer is
full each call processes `buffer_size` chunks of audio (with the default, five
times the chunk length) to produce one message. `buffer_size` is the bound:
the buffer never holds more messages, and a message with `meta['silence']`
empties it, so the cost drops back after each pause. faster-whisper encodes
audio in 30 s windows (its default `chunk_length`): a buffer shorter than 30 s
costs one encoder window per call, and a longer one costs more. If the node
falls behind its input, lower `buffer_size` or send shorter chunks.

The output payload has a `transcript` key, with a list of words:

```json
{
  "transcript": [
    {
      "word": " hello",
      "start": 0.0,
      "end": 0.42,
      "start_abs": 12.0,
      "end_abs": 12.42,
      "probability": 0.98
    }
  ]
}
```

The name of the node the audio came from is stored in `meta['origin']`.

The model is loaded when the node is created. With `only_local` enabled (the
default), the model must already be in the local cache, and is never
downloaded.

## Arguments

| Argument             | Type   | Default      | Description                                            |
| -------------------- | ------ | ------------ | ------------------------------------------------------ |
| `model_name`         | `str`  | `tiny`       | Whisper model name, or path of a local model           |
| `only_local`         | `bool` | `true`       | Only use local model files, and never download them    |
| `language`           | `str`  | `en`         | Language of the source audio                           |
| `task`               | `str`  | `transcribe` | Task to perform (`transcribe` or `translate`)          |
| `buffer_size`        | `int`  | `5`          | Number of audio messages kept and transcribed together |
| `device`             | `str`  | `cuda`       | Where to run the model (`cpu` or `cuda`)               |
| `word_timestamps`    | `bool` | `true`       | Compute word-level timestamps                          |
| `without_timestamps` | `bool` | `false`      | Skip timestamp generation                              |

## License

- **Code:** [faster-whisper](https://github.com/SYSTRAN/faster-whisper), MIT.
- **Weights:** a model name such as `tiny` is resolved by faster-whisper to a
  CTranslate2 conversion on Hugging Face (`tiny` →
  [Systran/faster-whisper-tiny](https://huggingface.co/Systran/faster-whisper-tiny),
  MIT on its model card). OpenAI releases the original Whisper code and
  weights under MIT ([openai/whisper README](https://github.com/openai/whisper#license)).
- **Runtime:** [CTranslate2](https://github.com/OpenNMT/CTranslate2), MIT.
- **The `audio-ml` extra** installs faster-whisper and silero-vad together.
  faster-whisper imports `av` (PyAV, BSD-3-Clause), whose PyPI wheels bundle
  an FFmpeg that is effectively GPL (see the License section of `AudioRtp`),
  and depends on onnxruntime (MIT); silero-vad imports PyTorch
  (BSD-3-Clause).

## Example

```json
{
  "name": "2_transcriber",
  "type": "TranscriberWhisper",
  "configuration": { "model_name": "small", "language": "en", "device": "cpu" }
}
```
