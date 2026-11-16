from types import SimpleNamespace

import numpy as np
import pytest

av = pytest.importorskip('av')

from juturna.nodes import AudioRtp  # noqa: E402
from juturna.nodes._audio_rtp import audio_rtp  # noqa: E402


def _blocks(monkeypatch, out_channels, resampler_format, audio):
    """Run the node reader on one decoded frame, without a network"""
    frame = av.AudioFrame.from_ndarray(audio, format='s16p', layout='stereo')
    frame.sample_rate = 16000
    container = SimpleNamespace(
        streams=SimpleNamespace(audio=[None]),
        demux=lambda stream: [SimpleNamespace(decode=lambda: [frame])],
        close=lambda: None,
    )
    monkeypatch.setattr(audio_rtp.av, 'open', lambda *a, **k: container)

    node = AudioRtp(
        host='127.0.0.1',
        port=5004,
        payload_type=0,
        encoding_clock_chan='PCMU/8000',
        out_rate=16000,
        out_channels=out_channels,
        resampler_format=resampler_format,
        block_size=1,
        flush_partial_on_error=True,
        node_name='rtp',
        pipe_name='pipe',
    )
    node._sdp_file_path = 'unused.sdp'

    return np.concatenate(list(node._stream_audio_blocks()))


@pytest.mark.parametrize('fmt', ['s16', 's16p', 's32', 'u8'])
def test_mono_keeps_the_integer_format(monkeypatch, fmt):
    audio = np.full((2, 160), 1000, dtype=np.int16)

    samples = _blocks(monkeypatch, 1, fmt, audio)

    assert samples.dtype == audio_rtp.FORMAT_DTYPES[fmt]
    assert samples.ndim == 1


def test_stereo_samples_are_interleaved(monkeypatch):
    audio = np.stack(
        [np.full(160, 1000, np.int16), np.full(160, -1000, np.int16)]
    )

    samples = _blocks(monkeypatch, 2, 's16', audio)

    assert samples.dtype == np.int16
    assert (samples[0::2] == 1000).all()
    assert (samples[1::2] == -1000).all()
