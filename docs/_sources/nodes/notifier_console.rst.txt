.. _node-notifier-console:

``NotifierConsole``
===================

:bdg-primary:`sink`

Print every received message on the standard output, one line per message.
A transcript is printed as text, any other ``ObjectPayload`` as compact JSON,
any other payload as its type name.

:Node type: ``NotifierConsole``
:Input: any payload
:Output: --
:Extra: --

.. code-block:: console

    $ pip install juturna-nodes

Configuration
-------------

The node takes no arguments.

Pipeline usage
--------------

.. code-block:: json

    {
      "name": "console",
      "type": "NotifierConsole",
      "configuration": {}
    }

Reference
---------

.. autoclass:: juturna.nodes._notifier_console.notifier_console.NotifierConsole
    :no-index:
