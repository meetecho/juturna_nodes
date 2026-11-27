.. _node-mic-source:

``MicSource``
=============

:bdg-primary:`source` :bdg-secondary-line:`extra: mic-source`

Capture mono audio from a microphone, optionally only between two presses of Enter (push-to-talk).

:Node type: ``MicSource``
:Input: --
:Output: ``AudioPayload``
:Extra: ``mic-source``

.. code-block:: console

    $ pip install "juturna-nodes[mic-source]"

The node README describes the system requirements, the messages and the
limits of the node.

Configuration
-------------

Default node arguments, as defined in the node ``config.toml`` file. Any of
them can be overridden in the node ``configuration`` of a pipeline.

.. literalinclude:: ../../../src/juturna/nodes/_mic_source/config.toml
    :language: toml

Reference
---------

.. autoclass:: juturna.nodes._mic_source.mic_source.MicSource
    :no-index:
