.. _node-browser-output:

``BrowserOutput``
=================

:bdg-primary:`sink`

Hand the messages of the pipeline over to the web page hosting it.

:Node type: ``BrowserOutput``
:Input: ``AudioPayload``, ``ImagePayload``, ``BytesPayload`` or ``ObjectPayload``
:Output: --
:Extra: --

.. code-block:: console

    $ pip install juturna-nodes

The node runs only in a Pyodide Worker, with the browser transport of juturna.
It encodes each message in the wire format of
``juturna.transport._browser_io`` and posts
``{type: 'output', node, message}`` to the page with the ``postMessage`` of the
Worker. Any other payload type is logged and counted as an update failure.

Configuration
-------------

Default node arguments, as defined in the node ``config.toml`` file. Any of
them can be overridden in the node ``configuration`` of a pipeline.

.. literalinclude:: ../../../src/juturna/nodes/_browser_output/config.toml
    :language: toml

Pipeline usage
--------------

.. code-block:: json

    {
      "name": "browser_output",
      "type": "BrowserOutput",
      "configuration": {}
    }

Reference
---------

.. autoclass:: juturna.nodes._browser_output.browser_output.BrowserOutput
    :no-index:
