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

A pipeline does not list ``Warp`` itself: a node with ``"warped": true`` is
replaced by a ``Warp`` built from its ``warp_configuration``. The ``sticky``
key of the warped node (default ``true``) tells whether the remote service
keeps the node state (``true``), or the state travels with every request so
that ``grpc_host`` can point to a load balancer in front of several replicas
(``false``).

.. code-block:: json

    {
      "name": "transcriber",
      "type": "TranscriberWhisper",
      "configuration": { "model_name": "large-v3" },
      "warped": true,
      "sticky": false,
      "warp_configuration": {
        "grpc_host": "transcribers.internal",
        "grpc_port": 45000,
        "timeout": 10
      }
    }

Reference
---------

.. autoclass:: juturna.nodes._warp.warp.Warp
    :no-index:
