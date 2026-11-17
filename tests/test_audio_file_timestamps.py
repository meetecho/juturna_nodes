import numpy as np
import pytest

pytest.importorskip('av')

from juturna.nodes import AudioFile  # noqa: E402


def test_chunk_start_and_end_are_in_seconds():
    rate = 16000
    node = AudioFile(
        file_source='',
        block_size=2,
        audio_rate=rate,
        node_name='audio',
        pipe_name='pipe',
    )
    # skip warmup: the timestamps only depend on the decoded samples
    node._audio = np.zeros(int(rate * 5), dtype=np.float32)
    node._audio_chunks = node._iter_audio_chunks()

    chunks = [node._generate_chunks().payload for _ in range(3)]

    assert [(c.start, c.end) for c in chunks] == [
        (0.0, 2.0),
        (2.0, 4.0),
        (4.0, 6.0),
    ]
