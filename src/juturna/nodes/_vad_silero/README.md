# VadSilero

Voice activity detection with the
[Silero VAD](https://github.com/snakers4/silero-vad) model: silence is removed
from the incoming audio, and only speech is forwarded.

- **Role:** processing
- **Node type:** `VadSilero`
- **Input:** `AudioPayload`
- **Output:** `AudioPayload`
- **Extra:** `audio-ml` (`pip install "juturna-nodes[audio-ml]"`)

## How it works

The node keeps the last `keep` audio messages, and runs the model on their
concatenation every time a new message arrives. The output payload carries
the speech found in that audio, and the output `meta` describes it:

| Meta key             | Description                                           |
| -------------------- | ----------------------------------------------------- |
| `silence`            | `true` when no speech was detected                    |
| `speech_timestamps`  | The detected speech segments                          |
| `duration_after_vad` | Duration of the speech audio left after the detection |
| `original_audio`     | The audio the detection ran on, before the cut        |
| `sequence_number`    | Version of the last buffered message                  |

`TranscriberWhisper` relies on `silence` and `speech_timestamps`, so the two
nodes are usually linked together.

## Arguments

The detection arguments are passed to the Silero `get_speech_timestamps`
function.

| Argument                  | Type             | Default | Description                                               |
| ------------------------- | ---------------- | ------- | --------------------------------------------------------- |
| `device`                  | `str`            | `cpu`   | Where to run the model (`cpu` or `cuda`)                  |
| `rate`                    | `int`            | `16000` | Sampling rate of the source audio, in Hz                  |
| `threshold`               | `float`          | `0.75`  | Speech probability threshold                              |
| `min_speech_duration_ms`  | `int`            | `0`     | Discard speech chunks shorter than this                   |
| `max_speech_duration_s`   | `float` or `str` | `"inf"` | Split speech chunks longer than this                      |
| `min_silence_duration_ms` | `int`            | `2000`  | Silence to wait after speech ends before cutting          |
| `speech_pad_ms`           | `int`            | `400`   | Padding added to each side of a speech chunk              |
| `keep`                    | `int`            | `1`     | Number of audio messages the detection runs on            |

## Example

```json
{
  "name": "1_vad",
  "type": "VadSilero",
  "configuration": { "threshold": 0.6, "min_silence_duration_ms": 1000 }
}
```
