.. _node-speaker-sink:

``SpeakerSink``
===============

:bdg-primary:`sink` :bdg-secondary-line:`extra: speaker-sink`

Play the audio of every received message on a speaker, one message after the other.

:Node type: ``SpeakerSink``
:Input: ``AudioPayload``
:Output: --
:Extra: ``speaker-sink``

.. code-block:: console

    $ pip install "juturna-nodes[speaker-sink]"

The node README describes the system requirements, the messages and the
licenses of the node.

Configuration
-------------

Default node arguments, as defined in the node ``config.toml`` file. Any of
them can be overridden in the node ``configuration`` of a pipeline.

.. literalinclude:: ../../../src/juturna/nodes/_speaker_sink/config.toml
    :language: toml

Reference
---------

.. autoclass:: juturna.nodes._speaker_sink.speaker_sink.SpeakerSink
    :no-index:
