import wave

import numpy as np
import pytest

pytest.importorskip('av')

from juturna.nodes import AudioFile  # noqa: E402


def _write_wav(path, samples, rate):
    with wave.open(str(path), 'wb') as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(rate)
        f.writeframes(samples.astype('<i2').tobytes())


def test_warmup_decodes_the_file_into_chunks(tmp_path):
    rate = 16000
    samples = np.full(int(rate * 2.5), 8192, dtype=np.int16)
    _write_wav(tmp_path / 'sample.wav', samples, rate)

    node = AudioFile(
        file_source=str(tmp_path / 'sample.wav'),
        block_size=1,
        audio_rate=rate,
        node_name='audio',
        pipe_name='pipe',
    )
    node.warmup()

    chunks = [node._generate_chunks() for _ in range(3)]

    assert [len(c.payload.audio) for c in chunks] == [rate] * 3
    assert np.allclose(chunks[0].payload.audio, 0.25)
    # the last chunk is padded with silence up to the block size
    assert np.allclose(chunks[2].payload.audio[rate // 2 :], 0.0)
    assert node._generate_chunks() is None
