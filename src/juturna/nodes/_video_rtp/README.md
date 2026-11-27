# VideoRtp

Receive an RTP video stream with PyAV, and transmit one RGB frame per message.

- **Role:** source
- **Node type:** `VideoRtp`
- **Input:** none
- **Output:** `ImagePayload`
- **Extra:** `video-rtp` (`pip install "juturna-nodes[video-rtp]"`)

## How it works

On warmup the node writes an SDP file, `_session_in.sdp`, in its pipeline
folder, describing a stream on `rec_host:rec_port` with `payload_type` and
`codec` at a 90000 Hz clock. On start, a worker opens that SDP with PyAV,
decodes every packet and converts each frame to RGB. The frames go through
the node queue, so `update()` numbers them and transmits them in order.

Packets that cannot be decoded are skipped, with a warning in the log
(`error decoding packet: ...`). This is common until the first keyframe
arrives.

When no packet arrives for `JUTURNA_THREAD_JOIN_TIMEOUT` seconds (2 s by
default), the read times out, the input is closed and opened again: the node
waits for the stream to come back, and only logs `demux terminate while
reading False` at `DEBUG` level. Opening the input has no timeout. Any other
error is logged as `source unavailable (...), retrying...` and the node tries
again after 2 s.

In our tests (ffmpeg sending H.264 at 10 fps on localhost), the first frame
came out about 2.3 s after the sender started, every time the stream started
or resumed after a pause: shorter bursts produced no frame at all. After
that, every frame was transmitted.

## Arguments

| Argument              | Type         | Default       | Description |
| --------------------- | ------------ | ------------- | ----------- |
| `rec_host`            | `str`        | `"127.0.0.1"` | Address the stream is received on |
| `rec_port`            | `int`, `str` | `"auto"`      | UDP port of the stream; `"auto"` picks a free port when the node is configured |
| `payload_type`        | `int`        | `96`          | RTP payload type of the stream |
| `codec`               | `str`        | `"vp8"`       | Encoding name written in the SDP `rtpmap` line, such as `H264` or `VP8` |
| `encoding_clock_chan` | `int`        | `90000`       | Not used: the SDP always declares a 90000 Hz clock |

The node `configuration` reports `host` and `port`, so the port picked with
`"auto"` can be read and given to the sender.

## Input message

The node has no input: it reads the RTP stream.

## Output message

| Field | Content |
| --- | --- |
| `payload.image` | The frame, `uint8` array of shape `(height, width, 3)` |
| `payload.width`, `payload.height` | Frame size |
| `payload.depth` | Not set (`-1`) |
| `payload.pixel_format` | `rgb24` |
| `payload.timestamp` | Wall-clock time the frame was decoded, as `time.time()` |
| `version` | Number of frames transmitted by the node, from `0` |

`meta` is empty, and the message has no timers.

## Limits

- The end of a stream is not propagated downstream: the node only stops
  transmitting.
- The SDP always carries `a=fmtp:<payload_type> packetization-mode=1`, an
  H.264 parameter, whatever the codec.
- With ffmpeg sending VP8 (`-c:v libvpx -f rtp`), our test decoded no frame:
  every packet failed with `Invalid data found when processing input`. The
  default `codec` is `vp8`, so check your sender before relying on it; H.264
  worked.
- `stop()` took about 1 s while a stream had been received, but 7 s when no
  sender had ever connected, because opening the input has no timeout.

## License

- **Code:** this node is part of juturna-nodes, MIT (its `LICENSE` file).
- **PyAV:** BSD-3-Clause (the `License-Expression` of av on PyPI).
- **FFmpeg:** effectively GPL. The PyAV wheels on PyPI bundle their own
  FFmpeg: av 19.0.2 ships FFmpeg 9.0.2 from the
  [pyav-ffmpeg 9.0.2-4 build](https://github.com/PyAV-Org/pyav-ffmpeg/releases/tag/9.0.2-4),
  which links x264 and x265 (GPL-2.0-or-later). The FFmpeg
  [legal page](https://ffmpeg.org/legal.html) says that when its GPL parts
  are used, "the GPL applies to all of FFmpeg". The libraries still report
  "LGPL version 3 or later" only because a pyav-ffmpeg patch to FFmpeg's
  `configure` moves x264 and x265 out of the libraries that need
  `--enable-gpl`. A PyAV built from source against an LGPL build of FFmpeg
  (without x264, x265 or other GPL parts) avoids the GPL. (Checked on
  2026-11-18 on av 19.0.2.)

## Example

```json
{
  "name": "camera",
  "type": "VideoRtp",
  "configuration": { "rec_port": 5004, "payload_type": 96, "codec": "H264" }
}
```
