.. _node-passthrough-identity:

``PassthroughIdentity``
=======================

:bdg-primary:`processing`

Test node: return input messages after a delay.

:Node type: ``PassthroughIdentity``
:Input: ``BasePayload``
:Output: ``BasePayload``
:Extra: --

.. code-block:: console

    $ pip install juturna-nodes

Configuration
-------------

Default node arguments, as defined in the node ``config.toml`` file. Any of
them can be overridden in the node ``configuration`` of a pipeline.

.. literalinclude:: ../../../src/juturna/nodes/_passthrough_identity/config.toml
    :language: toml

Pipeline usage
--------------

.. code-block:: json

    {
      "name": "passthrough_identity",
      "type": "PassthroughIdentity",
      "configuration": {}
    }

Reference
---------

.. autoclass:: juturna.nodes._passthrough_identity.passthrough_identity.PassthroughIdentity
    :no-index:
