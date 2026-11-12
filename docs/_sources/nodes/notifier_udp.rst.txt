.. _node-notifier-udp:

``NotifierUDP``
===============

:bdg-primary:`sink`

Transmit message to a UDP socket.

:Node type: ``NotifierUDP``
:Input: ``ObjectPayload``
:Output: --
:Extra: --

.. code-block:: console

    $ pip install juturna-nodes

Configuration
-------------

Default node arguments, as defined in the node ``config.toml`` file. Any of
them can be overridden in the node ``configuration`` of a pipeline.

.. literalinclude:: ../../../src/juturna/nodes/_notifier_udp/config.toml
    :language: toml

Pipeline usage
--------------

.. code-block:: json

    {
      "name": "notifier_udp",
      "type": "NotifierUDP",
      "configuration": {}
    }

Reference
---------

.. autoclass:: juturna.nodes._notifier_udp.notifier_udp.NotifierUDP
    :no-index:
