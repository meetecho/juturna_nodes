.. _node-notifier-http:

``NotifierHTTP``
================

:bdg-primary:`sink`

Transmit message to a HTTP endpoint.

:Node type: ``NotifierHTTP``
:Input: ``ObjectPayload``
:Output: --
:Extra: --

.. code-block:: console

    $ pip install juturna-nodes

Configuration
-------------

Default node arguments, as defined in the node ``config.toml`` file. Any of
them can be overridden in the node ``configuration`` of a pipeline.

.. literalinclude:: ../../../src/juturna/nodes/_notifier_http/config.toml
    :language: toml

Pipeline usage
--------------

.. code-block:: json

    {
      "name": "notifier_http",
      "type": "NotifierHTTP",
      "configuration": {}
    }

Reference
---------

.. autoclass:: juturna.nodes._notifier_http.notifier_http.NotifierHTTP
    :no-index:
