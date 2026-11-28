# AudioFile

Read an audio file, split it into fixed-length chunks, and feed them to the
pipeline in real time: one chunk is produced every `block_size` seconds.

- **Role:** source
- **Node type:** `AudioFile`
- **Input:** none
- **Output:** `AudioPayload`
- **Extra:** `audio-file` (`pip install "juturna-nodes[audio-file]"`)

## How it works

The whole file is decoded on warmup with PyAV, resampled to mono at
`audio_rate`, and converted to `float32` samples in the `[-1, 1]` range. The
last chunk is zero-padded to the full chunk length. When the file is over, the
node stops producing messages.

The payload `start` and `end` are in seconds from the beginning of the file:
with `block_size: 2`, the chunks cover `0.0`–`2.0`, `2.0`–`4.0`, and so on.

Every message carries the pipeline id in `meta['session_id']`.

## Arguments

| Argument      | Type  | Default | Description                                   |
| ------------- | ----- | ------- | --------------------------------------------- |
| `file_source` | `str` | `""`    | Path of the audio file to read                |
| `block_size`  | `int` | `3`     | Length of each produced chunk, in seconds     |
| `audio_rate`  | `int` | `16000` | Sampling rate the audio is resampled to, in Hz |

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
- **NumPy:** BSD-3-Clause AND 0BSD AND MIT AND Zlib AND CC0-1.0 (the
  `License-Expression` of numpy on PyPI).

## Example

```json
{
  "name": "0_src",
  "type": "AudioFile",
  "configuration": { "file_source": "./speech.wav", "block_size": 2 }
}
```
