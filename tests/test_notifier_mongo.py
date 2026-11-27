import logging

import pytest

pytest.importorskip('pymongo')

from juturna.nodes import NotifierMongo  # noqa: E402


def test_warmup_does_not_log_the_credentials(caplog, monkeypatch):
    # the jt logger does not propagate: caplog listens on the root logger
    monkeypatch.setattr(logging.getLogger('jt'), 'propagate', True)

    node = NotifierMongo(
        endpoint='mongodb://user:secret@127.0.0.1:27017',
        database='db',
        collection='col',
        timeout=1,
        node_name='mongo',
        pipe_name='pipe',
    )

    # the client connects lazily: warmup needs no server
    with caplog.at_level(logging.DEBUG):
        node.warmup()

    node.destroy()

    assert 'secret' not in caplog.text
    assert 'db.col' in caplog.text
