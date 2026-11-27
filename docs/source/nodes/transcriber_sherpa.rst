.. _node-transcriber-sherpa:

``TranscriberSherpa``
=====================

:bdg-primary:`processing` :bdg-secondary-line:`extra: transcriber-sherpa`

Streaming speech recognition with sherpa-onnx, on CPU and without torch. One message is transmitted for each sentence, when the speaker stops talking.

:Node type: ``TranscriberSherpa``
:Input: ``AudioPayload``
:Output: ``ObjectPayload``
:Extra: ``transcriber-sherpa``

.. code-block:: console

    $ pip install "juturna-nodes[transcriber-sherpa]"

The node downloads its default model on first use. The node README describes
the model cache, the input and output messages, and the licenses of the code
and the weights.

Configuration
-------------

Default node arguments, as defined in the node ``config.toml`` file. Any of
them can be overridden in the node ``configuration`` of a pipeline.

.. literalinclude:: ../../../src/juturna/nodes/_transcriber_sherpa/config.toml
    :language: toml

Reference
---------

.. autoclass:: juturna.nodes._transcriber_sherpa.transcriber_sherpa.TranscriberSherpa
    :no-index:
