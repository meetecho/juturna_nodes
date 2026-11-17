import numpy as np
import pytest

pytest.importorskip('av')

from juturna.nodes import AudioRtp  # noqa: E402


@pytest.mark.parametrize('channels', [1, 2])
def test_a_chunk_holds_block_size_seconds(channels):
    node = AudioRtp(
        host='127.0.0.1',
        port=5004,
        payload_type=0,
        encoding_clock_chan='PCMU/8000',
        out_rate=16000,
        out_channels=channels,
        resampler_format='flt',
        block_size=1,
        flush_partial_on_error=True,
        node_name='rtp',
        pipe_name='pipe',
    )
    sent = list()
    node.transmit = sent.append

    # two seconds of interleaved samples
    node._pending = np.zeros(2 * 16000 * channels, dtype=np.float32)
    node._flush_pending()

    assert [(m.payload.start, m.payload.end) for m in sent] == [
        (0.0, 1.0),
        (1.0, 2.0),
    ]
    assert all(len(m.payload.audio) == 16000 * channels for m in sent)
