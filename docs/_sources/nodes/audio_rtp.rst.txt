.. _node-audio-rtp:

``AudioRtp``
============

:bdg-primary:`source` :bdg-secondary-line:`extra: av`

Consume RTP audio streams using PyAv.

:Node type: ``AudioRtp``
:Input: --
:Output: ``AudioPayload``
:Extra: ``av``

.. code-block:: console

    $ pip install "juturna-nodes[av]"

Configuration
-------------

Default node arguments, as defined in the node ``config.toml`` file. Any of
them can be overridden in the node ``configuration`` of a pipeline.

.. literalinclude:: ../../../src/juturna/nodes/_audio_rtp/config.toml
    :language: toml

Pipeline usage
--------------

.. code-block:: json

    {
      "name": "audio_rtp",
      "type": "AudioRtp",
      "configuration": {}
    }

Reference
---------

.. autoclass:: juturna.nodes._audio_rtp.audio_rtp.AudioRtp
    :no-index:
