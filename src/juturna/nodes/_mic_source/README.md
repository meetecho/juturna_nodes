# MicSource

Capture mono audio from a microphone, through
[sounddevice](https://python-sounddevice.readthedocs.io) (PortAudio). With
push-to-talk on (the default), the node only sends audio between two presses
of Enter on the terminal that runs the pipeline.

- **Role:** source
- **Node type:** `MicSource`
- **Input:** none
- **Output:** `AudioPayload`
- **Extra:** `sound`

```console
pip install "juturna-nodes[sound]"
```

PortAudio comes with the wheel on macOS and Windows; on Linux install the
system package (`libportaudio2` on Debian and Ubuntu). List the devices with
`python -m sounddevice`.

## Push-to-talk

A terminal cannot tell when a key is released, so Enter works as a switch:
press it to start talking, press it again to stop. The node prints its state
(`[mic] listening, press Enter to stop`). When you stop, it sends
`trailing_silence` seconds of silence, so a downstream `TranscriberSherpa`
closes the sentence at once. While push-to-talk is off the microphone is
still read, but the audio is dropped: an assistant that answers through a
speaker does not hear itself.

Push-to-talk reads the standard input, so:

- run the pipeline in a terminal, with `python -m juturna launch --auto`
  (without `--auto` the launcher reads Enter itself to start and stop the
  pipeline);
- use one `MicSource` with push-to-talk per pipeline.

If the standard input is closed, push-to-talk stays off and a warning is
logged.

## Arguments

| Argument           | Type    | Default | Description |
| ------------------ | ------- | ------- | ----------- |
| `device`           | `str`   | `""`    | Input device, as a name (or part of it) or an index; empty for the system default |
| `sample_rate`      | `int`   | `16000` | Rate of the produced audio, in Hz |
| `block_size`       | `float` | `0.2`   | Length of each chunk, in seconds |
| `push_to_talk`     | `bool`  | `true`  | Send audio only between two presses of Enter |
| `trailing_silence` | `float` | `1.0`   | Seconds of silence sent when push-to-talk is turned off |

## Input message

The node is a source: it receives no messages.

## Output message

| Field | Content |
| --- | --- |
| `payload.audio` | Mono `float32` samples in `[-1, 1]`, `block_size` seconds long (`trailing_silence` seconds for the silence after push-to-talk) |
| `payload.sampling_rate` | `sample_rate` |
| `payload.channels` | `1` |
| `payload.start`, `payload.end` | Seconds of audio sent since the start, counting only the chunks that were sent |

`meta` is empty. `TranscriberSherpa` and `AudioWriter` read this format.

## Example

```json
{
  "name": "mic",
  "type": "MicSource",
  "configuration": { "push_to_talk": true }
}
```
