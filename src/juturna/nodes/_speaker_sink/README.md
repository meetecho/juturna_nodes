# SpeakerSink

Play the audio of every received message on a speaker, through
[sounddevice](https://python-sounddevice.readthedocs.io) (PortAudio). Messages
are played one after the other: the node waits for each one to end before
taking the next.

- **Role:** sink
- **Node type:** `SpeakerSink`
- **Input:** `AudioPayload`
- **Output:** none
- **Extra:** `speaker-sink`

```console
pip install "juturna-nodes[speaker-sink]"
```

On Linux PortAudio is a system package (`libportaudio2` on Debian and
Ubuntu). Warmup fails if the output device does not exist. When a microphone
in the same pipeline can hear the speaker, use `MicSource` with push-to-talk
or headphones.

## Arguments

| Argument | Type  | Default | Description |
| -------- | ----- | ------- | ----------- |
| `device` | `str` | `""`    | Output device, as a name (or part of it) or an index listed by `python -m sounddevice`; empty for the system default |

## Input message

| Field | Use |
| --- | --- |
| `payload.audio` | Mono `float32` samples, required. Values outside `[-1, 1]` are clipped |
| `payload.sampling_rate` | Required. If the device does not support this rate, the audio backend decides: it may resample or refuse to play |

`meta` is not read. `SynthesizerSherpa` produces this format.

## Output message

The node does not transmit messages.

## License

- **Code:** this node is part of juturna-nodes, MIT (its `LICENSE` file).
- **sounddevice:** MIT (the `License-Expression` of sounddevice on PyPI).
- **NumPy:** BSD-3-Clause AND 0BSD AND MIT AND Zlib AND CC0-1.0 (the
  `License-Expression` of numpy on PyPI).

## Example

```json
{
  "name": "speaker",
  "type": "SpeakerSink",
  "configuration": {}
}
```
