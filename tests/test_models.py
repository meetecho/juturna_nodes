import hashlib
import logging

import pytest

from juturna.nodes import _models


_DATA = b'model bytes'


class _Response:
    def __init__(self, data):
        self._data = data

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def raise_for_status(self):
        pass

    def iter_content(self, chunk_size):
        yield self._data[:4]
        yield self._data[4:]


@pytest.fixture
def fake_model(monkeypatch, tmp_path):
    monkeypatch.setenv('XDG_CACHE_HOME', str(tmp_path))
    sha256 = hashlib.sha256(_DATA).hexdigest()
    monkeypatch.setitem(
        _models.MODELS,
        'fake',
        {'model.onnx': ('https://example.org/model.onnx', len(_DATA), sha256)},
    )
    requests = list()

    def fake_get(url, **kwargs):
        requests.append(url)

        return _Response(fake_get.data)

    fake_get.data = _DATA
    monkeypatch.setattr(_models.requests, 'get', fake_get)

    return fake_get, requests, tmp_path / 'juturna' / 'models' / 'fake'


def test_missing_file_is_downloaded_and_checked(fake_model):
    _, requests, folder = fake_model

    assert _models.fetch('fake', logging.getLogger()) == folder
    assert (folder / 'model.onnx').read_bytes() == _DATA
    assert requests == ['https://example.org/model.onnx']
    assert [p.name for p in folder.iterdir()] == ['model.onnx']


def test_cached_file_is_not_downloaded_again(fake_model):
    _, requests, _ = fake_model

    _models.fetch('fake', logging.getLogger())
    _models.fetch('fake', logging.getLogger())

    assert len(requests) == 1


def test_cached_file_with_the_wrong_sha256_is_downloaded_again(fake_model):
    _, requests, folder = fake_model
    folder.mkdir(parents=True)
    (folder / 'model.onnx').write_bytes(b'model bytez')

    _models.fetch('fake', logging.getLogger())

    assert (folder / 'model.onnx').read_bytes() == _DATA
    assert len(requests) == 1


def test_corrupted_download_leaves_no_file(fake_model):
    fake_get, _, folder = fake_model
    fake_get.data = b'model bytez'

    with pytest.raises(ValueError, match='sha256'):
        _models.fetch('fake', logging.getLogger())

    assert list(folder.iterdir()) == []


def test_unknown_model_is_rejected():
    with pytest.raises(ValueError, match='unknown model'):
        _models.fetch('nope', logging.getLogger())
