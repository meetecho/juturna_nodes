.. _node-json-http:

``JsonHTTP``
============

:bdg-primary:`source`

HTTP JSON source node.  Accepts POST /<endpoint> with JSON body. This is a
sourceless node, in the sense that the source function itself only spawns the
server handler and listens forever for incoming requests, while the handler
writes on the node queue whenever a message is received.

:Node type: ``JsonHTTP``
:Input: --
:Output: ``ObjectPayload``
:Extra: --

.. code-block:: console

    $ pip install juturna-nodes

Configuration
-------------

Default node arguments, as defined in the node ``config.toml`` file. Any of
them can be overridden in the node ``configuration`` of a pipeline.

.. literalinclude:: ../../../src/juturna/nodes/_json_http/config.toml
    :language: toml

Pipeline usage
--------------

.. code-block:: json

    {
      "name": "json_http",
      "type": "JsonHTTP",
      "configuration": {}
    }

Reference
---------

.. autoclass:: juturna.nodes._json_http.json_http.JsonHTTP
    :no-index:
