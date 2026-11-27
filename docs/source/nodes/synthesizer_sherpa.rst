.. _node-synthesizer-sherpa:

``SynthesizerSherpa``
=====================

:bdg-primary:`processing` :bdg-secondary-line:`extra: synthesizer-sherpa`

Text to speech with sherpa-onnx, on CPU and without torch: the text of each message becomes one audio message.

:Node type: ``SynthesizerSherpa``
:Input: ``ObjectPayload``
:Output: ``AudioPayload``
:Extra: ``synthesizer-sherpa``

.. code-block:: console

    $ pip install "juturna-nodes[synthesizer-sherpa]"

The node downloads its default model on first use. The node README describes
the model cache, the input and output messages, and the limits of the node.

Configuration
-------------

Default node arguments, as defined in the node ``config.toml`` file. Any of
them can be overridden in the node ``configuration`` of a pipeline.

.. literalinclude:: ../../../src/juturna/nodes/_synthesizer_sherpa/config.toml
    :language: toml

Reference
---------

.. autoclass:: juturna.nodes._synthesizer_sherpa.synthesizer_sherpa.SynthesizerSherpa
    :no-index:
