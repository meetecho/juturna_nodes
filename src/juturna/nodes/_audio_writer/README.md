# AudioWriter

Append the audio of every received message to one WAV file, 16-bit mono, in
the node folder of the pipeline run (`<pipeline folder>/<node name>/`).

- **Role:** sink
- **Node type:** `AudioWriter`
- **Input:** `AudioPayload`
- **Output:** none
- **Extra:** none

The file is created when the first message arrives, with the sampling rate of
that message, and closed when the pipeline is destroyed. The WAV header is
updated after every message, so the file can be played while the pipeline
runs.

## Arguments

| Argument    | Type  | Default        | Description |
| ----------- | ----- | -------------- | ----------- |
| `file_name` | `str` | `"output.wav"` | Name of the WAV file in the node folder |

## Input message

| Field | Use |
| --- | --- |
| `payload.audio` | Mono `float32` samples, required. Values outside `[-1, 1]` are clipped |
| `payload.sampling_rate` | Required. A message with a rate different from the first one is dropped, with an error in the log |

`meta` is not read. `SynthesizerSherpa` and `AudioFile` produce this format.

## Output message

The node does not transmit messages.

## Example

```json
{
  "name": "speaker",
  "type": "AudioWriter",
  "configuration": { "file_name": "answer.wav" }
}
```
