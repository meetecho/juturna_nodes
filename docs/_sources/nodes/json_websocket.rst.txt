.. _node-json-websocket:

``JsonWebsocket``
=================

:bdg-primary:`source`

Expose a websocket server and fetch input data from it.

:Node type: ``JsonWebsocket``
:Input: --
:Output: ``ObjectPayload``
:Extra: --

.. code-block:: console

    $ pip install juturna-nodes

Configuration
-------------

Default node arguments, as defined in the node ``config.toml`` file. Any of
them can be overridden in the node ``configuration`` of a pipeline.

.. literalinclude:: ../../../src/juturna/nodes/_json_websocket/config.toml
    :language: toml

Pipeline usage
--------------

.. code-block:: json

    {
      "name": "json_websocket",
      "type": "JsonWebsocket",
      "configuration": {}
    }

Reference
---------

.. autoclass:: juturna.nodes._json_websocket.json_websocket.JsonWebsocket
    :no-index:
