.. _node-transcriber-whisper:

``TranscriberWhisper``
======================

:bdg-primary:`processing` :bdg-secondary-line:`extra: audio-ml`

Transcribe audio packets using whisper models.
For a full list of available models, see here:
https://github.com/SYSTRAN/faster-whisper

:Node type: ``TranscriberWhisper``
:Input: ``AudioPayload``
:Output: ``ObjectPayload``
:Extra: ``audio-ml``

.. code-block:: console

    $ pip install "juturna-nodes[audio-ml]"

Configuration
-------------

Default node arguments, as defined in the node ``config.toml`` file. Any of
them can be overridden in the node ``configuration`` of a pipeline.

.. literalinclude:: ../../../src/juturna/nodes/_transcriber_whisper/config.toml
    :language: toml

Pipeline usage
--------------

.. code-block:: json

    {
      "name": "transcriber_whisper",
      "type": "TranscriberWhisper",
      "configuration": {}
    }

Reference
---------

.. autoclass:: juturna.nodes._transcriber_whisper.transcriber_whisper.TranscriberWhisper
    :no-index:
