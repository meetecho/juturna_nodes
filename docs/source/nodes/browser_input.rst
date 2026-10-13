.. _node-browser-input:

``BrowserInput``
================

:bdg-primary:`source`

Receive the messages that the web page hosting the pipeline hands over.

:Node type: ``BrowserInput``
:Input: --
:Output: ``AudioPayload``, ``ImagePayload``, ``BytesPayload`` or ``ObjectPayload``
:Extra: --

.. code-block:: console

    $ pip install juturna-nodes

The node runs only in a Pyodide Worker, with the browser transport of juturna.
The host calls ``feed()`` with a message in the wire format of
``juturna.transport.browser._io`` (a JS object ``{kind, payload, meta}``), and
the node puts the decoded message on its own queue. ``feed()`` blocks when the
queue is full, so it must be invoked through ``.callPromising()``.

Configuration
-------------

Default node arguments, as defined in the node ``config.toml`` file. Any of
them can be overridden in the node ``configuration`` of a pipeline.

.. literalinclude:: ../../../src/juturna/nodes/_browser_input/config.toml
    :language: toml

Pipeline usage
--------------

.. code-block:: json

    {
      "name": "browser_input",
      "type": "BrowserInput",
      "configuration": {}
    }

Reference
---------

.. autoclass:: juturna.nodes._browser_input.browser_input.BrowserInput
    :no-index:
