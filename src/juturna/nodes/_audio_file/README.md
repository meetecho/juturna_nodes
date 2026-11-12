# AudioFile

Read an audio file, split it into fixed-length chunks, and feed them to the
pipeline in real time: one chunk is produced every `block_size` seconds.

- **Role:** source
- **Node type:** `AudioFile`
- **Input:** none
- **Output:** `AudioPayload`
- **Extra:** `av` (`pip install "juturna-nodes[av]"`), plus the FFmpeg
  libraries on the system

## How it works

The whole file is decoded on warmup with PyAV, resampled to mono at
`audio_rate`, and converted to `float32` samples in the `[-1, 1]` range. The
last chunk is zero-padded to the full chunk length. When the file is over, the
node stops producing messages.

Every message carries the pipeline id in `meta['session_id']`.

## Arguments

| Argument      | Type  | Default | Description                                   |
| ------------- | ----- | ------- | --------------------------------------------- |
| `file_source` | `str` | `""`    | Path of the audio file to read                |
| `block_size`  | `int` | `3`     | Length of each produced chunk, in seconds     |
| `audio_rate`  | `int` | `16000` | Sampling rate the audio is resampled to, in Hz |

## Example

```json
{
  "name": "0_src",
  "type": "AudioFile",
  "configuration": { "file_source": "./speech.wav", "block_size": 2 }
}
```
