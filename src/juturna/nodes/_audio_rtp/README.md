# AudioRtp

Receive an RTP audio stream with PyAV, resample it, and transmit it in
fixed-length chunks of `block_size` seconds.

- **Role:** source
- **Node type:** `AudioRtp`
- **Input:** none
- **Output:** `AudioPayload`
- **Extra:** `av` (`pip install "juturna-nodes[av]"`), plus the FFmpeg
  libraries on the system

## How it works

On warmup the node writes an SDP file, `_session_in.sdp`, in its pipeline
folder, describing a stream on `host:port` with `payload_type` and
`encoding_clock_chan`. On start, a worker opens that SDP with PyAV and listens
for RTP packets on the port. Start the pipeline first, then the sender:
packets sent before the node listens are lost, without any error.

The decoded audio is resampled to `out_rate`, `out_channels` and
`resampler_format`, and cut into chunks of `block_size` seconds.

The input is opened and read with a timeout of `JUTURNA_THREAD_JOIN_TIMEOUT`
seconds, 2 s by default (the times below assume the default). When no
packet arrives for 2 s (the sender stopped, or never started), the node closes
the input and opens it again: without traffic this happens about every 4 s,
and only shows up in the log at `DEBUG` level (`demux terminate while
reading False`). When the input is closed, the samples still pending are
transmitted as a last chunk, padded with zeros to `block_size` when
`flush_partial_on_error` is true, and dropped otherwise. If the input cannot
be opened at all, for example because another process uses the port, the
node logs `source unavailable (...), retrying...` at `ERROR` level and tries
again every 2 s, until it succeeds or the node stops.

The UDP receive buffer is 64 KB, so short bursts of packets are not dropped.
`stop()` returns within a few seconds (up to 3 s in our tests).

## Arguments

| Argument                 | Type   | Default          | Description |
| ------------------------ | ------ | ---------------- | ----------- |
| `host`                   | `str`  | `"127.0.0.1"`    | Address the stream is received on |
| `port`                   | `int`  | `8888`           | UDP port of the stream; `0` picks a free port when the node is configured |
| `payload_type`           | `int`  | `97`             | RTP payload type of the stream |
| `encoding_clock_chan`    | `str`  | `"opus/48000/2"` | Encoding name, clock rate and channels, as in an SDP `rtpmap` line |
| `out_rate`               | `int`  | `16000`          | Sampling rate of the transmitted audio, in Hz |
| `out_channels`           | `int`  | `1`              | Channels of the transmitted audio |
| `resampler_format`       | `str`  | `"dblp"`         | Sample format of the transmitted audio, as named by PyAV: one of `flt`, `fltp` (`float32`), `dbl`, `dblp` (`float64`), `s16`, `s16p`, `s32`, `s32p`, `u8`, `u8p` |
| `block_size`             | `int`  | `3`              | Length of each chunk, in seconds |
| `flush_partial_on_error` | `bool` | `true`           | Transmit the pending samples, padded with zeros, when the input is closed |

For telephony audio, G.711 µ-law at 8 kHz mono (from a PBX such as
Asterisk, a Janus RTP forwarder, or
`ffmpeg ... -ac 1 -ar 8000 -c:a pcm_mulaw -f rtp rtp://127.0.0.1:5004`), use
`encoding_clock_chan: "PCMU/8000"` (`"PCMU/8000/1"` works the same) and set
`payload_type` to the type the sender uses: `0` is the static type of PCMU,
but a sender may be configured with a dynamic one. The string is written as
is in the SDP `rtpmap` line, and the audio is resampled from 8 kHz to
`out_rate`. The example at the end of this page receives such a stream.

## Input message

The node has no input: it reads the RTP stream.

## Output message

| Field | Content |
| --- | --- |
| `payload.audio` | `out_rate * block_size` samples, with the dtype of `resampler_format` (but see the limits for integer formats); with `out_channels: 2` the samples are interleaved |
| `payload.sampling_rate` | `out_rate` |
| `payload.channels` | `out_channels` |
| `payload.audio_format` | `resampler_format` |
| `payload.start`, `payload.end` | Seconds from the time the input was opened. They start again from `0.0` every time the input is opened again, so after every pause of more than 2 s |
| `version` | Number of chunks transmitted by the node, from `0` |

`meta` is empty, and the message has no timers.

## Limits

- The end of a stream is not propagated downstream: the node only stops
  transmitting. A downstream node waiting for silence, such as
  `TranscriberSherpa`, keeps its sentence open until more audio comes or the
  pipeline stops.
- With `out_channels: 2`, `block_size`, `start` and `end` count the
  interleaved samples as if they were mono: each chunk holds `block_size / 2`
  seconds of audio. Use `out_channels: 1`.
- With `out_channels: 1` and an integer `resampler_format` (`s16`, `s32`,
  `u8` and their planar forms), the audio is converted to `float64` while
  `payload.audio_format` still names the integer format. Use `flt` or `dblp`.

## Example

```json
{
  "name": "question",
  "type": "AudioRtp",
  "configuration": {
    "port": 5004,
    "payload_type": 0,
    "encoding_clock_chan": "PCMU/8000",
    "resampler_format": "flt",
    "block_size": 1
  }
}
```
