.. _node-detection-events:

``DetectionEvents``
===================

:bdg-primary:`processing`

Turn the detections attached to frames into small JSON events, with at most
one event per class every ``interval`` seconds.

:Node type: ``DetectionEvents``
:Input: ``ImagePayload`` with ``meta['detections']``
:Output: ``ObjectPayload``
:Extra: --

.. code-block:: console

    $ pip install juturna-nodes

The node README describes the input it reads, the events it emits, and the
limits of the node.

Configuration
-------------

Default node arguments, as defined in the node ``config.toml`` file. Any of
them can be overridden in the node ``configuration`` of a pipeline.

.. literalinclude:: ../../../src/juturna/nodes/_detection_events/config.toml
    :language: toml

Pipeline usage
--------------

.. code-block:: json

    {
      "name": "events",
      "type": "DetectionEvents",
      "configuration": { "interval": 2.0 }
    }

Reference
---------

.. autoclass:: juturna.nodes._detection_events.detection_events.DetectionEvents
    :no-index:
