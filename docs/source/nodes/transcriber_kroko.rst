.. _node-transcriber-kroko:

``TranscriberKroko``
====================

:bdg-primary:`processing`

Transcribe audio packets using kroko-onnx (WIP)

:Node type: ``TranscriberKroko``
:Input: ``AudioPayload``
:Output: ``ObjectPayload``
:Extra: --

.. code-block:: console

    $ pip install juturna-nodes

Configuration
-------------

Default node arguments, as defined in the node ``config.toml`` file. Any of
them can be overridden in the node ``configuration`` of a pipeline.

.. literalinclude:: ../../../src/juturna/nodes/_transcriber_kroko/config.toml
    :language: toml

Pipeline usage
--------------

.. code-block:: json

    {
      "name": "transcriber_kroko",
      "type": "TranscriberKroko",
      "configuration": {}
    }

Reference
---------

.. autoclass:: juturna.nodes._transcriber_kroko.transcriber_kroko.TranscriberKroko
    :no-index:
