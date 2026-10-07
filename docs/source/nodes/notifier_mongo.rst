.. _node-notifier-mongo:

``NotifierMongo``
=================

:bdg-primary:`sink`

Transmit messages to a Mongo endpoint.

:Node type: ``NotifierMongo``
:Input: ``ObjectPayload``
:Output: --
:Extra: --

.. code-block:: console

    $ pip install juturna-nodes

Configuration
-------------

Default node arguments, as defined in the node ``config.toml`` file. Any of
them can be overridden in the node ``configuration`` of a pipeline.

.. literalinclude:: ../../../src/juturna/nodes/_notifier_mongo/config.toml
    :language: toml

Pipeline usage
--------------

.. code-block:: json

    {
      "name": "notifier_mongo",
      "type": "NotifierMongo",
      "configuration": {}
    }

Reference
---------

.. autoclass:: juturna.nodes._notifier_mongo.notifier_mongo.NotifierMongo
    :no-index:
