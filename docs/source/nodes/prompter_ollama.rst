.. _node-prompter-ollama:

``PrompterOllama``
==================

:bdg-primary:`processing`

Send the text of each message to a model served by Ollama, and transmit the answer sentence by sentence while the model writes it. Needs a running Ollama server.

:Node type: ``PrompterOllama``
:Input: ``ObjectPayload``
:Output: ``ObjectPayload``
:Extra: --

.. code-block:: console

    $ pip install juturna-nodes

The node README describes the model to download, the input and output
messages, and the limits of the node.

Configuration
-------------

Default node arguments, as defined in the node ``config.toml`` file. Any of
them can be overridden in the node ``configuration`` of a pipeline.

.. literalinclude:: ../../../src/juturna/nodes/_prompter_ollama/config.toml
    :language: toml

Reference
---------

.. autoclass:: juturna.nodes._prompter_ollama.prompter_ollama.PrompterOllama
    :no-index:
