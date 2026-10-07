.. _node-audio-file:

``AudioFile``
=============

:bdg-primary:`source` :bdg-secondary-line:`extra: av`

Read an audio file and chunk it into smaller audio messages.

:Node type: ``AudioFile``
:Input: --
:Output: ``AudioPayload``
:Extra: ``av``

.. code-block:: console

    $ pip install "juturna-nodes[av]"

Configuration
-------------

Default node arguments, as defined in the node ``config.toml`` file. Any of
them can be overridden in the node ``configuration`` of a pipeline.

.. literalinclude:: ../../../src/juturna/nodes/_audio_file/config.toml
    :language: toml

Pipeline usage
--------------

.. code-block:: json

    {
      "name": "audio_file",
      "type": "AudioFile",
      "configuration": {}
    }

Reference
---------

.. autoclass:: juturna.nodes._audio_file.audio_file.AudioFile
    :no-index:
