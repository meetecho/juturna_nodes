# VideoCapture

Read video from a file or from a V4L2 webcam with PyAV, and transmit one RGB
frame per message.

- **Role:** source
- **Node type:** `VideoCapture`
- **Input:** none
- **Output:** `ImagePayload`
- **Extra:** `av` (`pip install "juturna-nodes[av]"`)

## How it works

A `source` made of digits (`"0"`) or starting with `/dev/video` is a webcam,
opened with the `v4l2` format; anything else is a video file.

- **File.** The frames are transmitted in real time, following their
  timestamps. At the end of the file the node logs `end of file, stopping the
  source` and stops producing frames, or starts again from the beginning when
  `loop` is true. A missing file makes the warmup fail.
- **Webcam.** The device sets the pace. If the device cannot be opened or read
  (unplugged, busy, missing), the error is logged by the node, counted in
  `health['source_failures']`, and the node tries again after a backoff that
  starts at 0.1 s and doubles at every failure, up to
  `JUTURNA_SOURCE_MAX_BACKOFF` (5 s by default). The backoff resets at the
  first frame read.

Corrupt packets are skipped, with a warning in the log. Looping on a file
without video frames is reported as a source failure instead of spinning.

With `fps` greater than 0, frames closer than `1 / fps` seconds to the last
transmitted one are dropped. Use it when a slower node follows, such as a
detector on CPU, so that its queue does not grow.

## Arguments

| Argument | Type    | Default | Description |
| -------- | ------- | ------- | ----------- |
| `source` | `str`   | `""`    | Path of a video file, or a webcam as `/dev/videoN` or `N` |
| `loop`   | `bool`  | `false` | Files only: start again at the end of the file instead of stopping |
| `fps`    | `float` | `0.0`   | Maximum frames per second; `0` transmits every frame |

## Input message

The node has no input: it reads the file or the device.

## Output message

| Field | Content |
| --- | --- |
| `payload.image` | The frame, `uint8` array of shape `(height, width, 3)` |
| `payload.width`, `payload.height`, `payload.depth` | Frame size, depth `3` |
| `payload.pixel_format` | `rgb24` |
| `payload.timestamp` | Wall-clock time the frame was read, as `time.time()` |
| `meta['pts']` | Frame time in seconds: from the start of the file (growing across loops), or the device clock for a webcam |
| `version` | Number of frames transmitted by the node, from `0` |

## Limits

- The end of a file is not propagated downstream: the node only stops
  transmitting.
- Webcams work on Linux only (V4L2). The resolution and the pixel format are
  the device defaults.
- RTSP and other network streams are not supported today: for RTP video use
  `VideoRtp`.

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
  "type": "VideoCapture",
  "configuration": { "source": "/dev/video0", "fps": 5 }
}
```
