.. _node-vad-silero:

``VadSilero``
=============

:bdg-primary:`processing` :bdg-secondary-line:`extra: audio-ml`

Use the Silero VAD model to perform voice activity detection on audio content.
Find the model here: https://github.com/snakers4/silero-vad

:Node type: ``VadSilero``
:Input: ``AudioPayload``
:Output: ``AudioPayload``
:Extra: ``audio-ml``

.. code-block:: console

    $ pip install "juturna-nodes[audio-ml]"

Configuration
-------------

Default node arguments, as defined in the node ``config.toml`` file. Any of
them can be overridden in the node ``configuration`` of a pipeline.

.. literalinclude:: ../../../src/juturna/nodes/_vad_silero/config.toml
    :language: toml

Pipeline usage
--------------

.. code-block:: json

    {
      "name": "vad_silero",
      "type": "VadSilero",
      "configuration": {}
    }

Reference
---------

.. autoclass:: juturna.nodes._vad_silero.vad_silero.VadSilero
    :no-index:
