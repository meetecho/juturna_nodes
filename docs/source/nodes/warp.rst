.. _node-warp:

``Warp``
========

:bdg-primary:`processing` :bdg-secondary-line:`extra: warp`

Generic gRPC remote node using Juturna's protobuf messaging.

:Node type: ``Warp``
:Input: any (same as the remote node)
:Output: any (same as the remote node)
:Extra: ``warp``

.. code-block:: console

    $ pip install "juturna-nodes[warp]"

Configuration
-------------

Default node arguments, as defined in the node ``config.toml`` file. Any of
them can be overridden in the node ``configuration`` of a pipeline.

.. literalinclude:: ../../../src/juturna/nodes/_warp/config.toml
    :language: toml

Pipeline usage
--------------

.. code-block:: json

    {
      "name": "warp",
      "type": "Warp",
      "configuration": {}
    }

Reference
---------

.. autoclass:: juturna.nodes._warp.warp.Warp
    :no-index:
