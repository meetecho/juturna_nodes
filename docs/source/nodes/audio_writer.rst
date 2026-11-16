.. _node-audio-writer:

``AudioWriter``
===============

:bdg-primary:`sink`

Append the audio of every received message to one 16-bit mono WAV file in the node folder.

:Node type: ``AudioWriter``
:Input: ``AudioPayload``
:Output: --
:Extra: --

.. code-block:: console

    $ pip install juturna-nodes

The node README describes the model to download, the input and output
messages, and the limits of the node.

Configuration
-------------

Default node arguments, as defined in the node ``config.toml`` file. Any of
them can be overridden in the node ``configuration`` of a pipeline.

.. literalinclude:: ../../../src/juturna/nodes/_audio_writer/config.toml
    :language: toml

Reference
---------

.. autoclass:: juturna.nodes._audio_writer.audio_writer.AudioWriter
    :no-index:
