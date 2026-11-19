.. _node-detector-yolox:

``DetectorYolox``
=================

:bdg-primary:`processing` :bdg-secondary-line:`extra: onnx`

Detect objects in frames with a YOLOX model exported to ONNX, on ONNX Runtime,
and attach them to the frame as plain data.

:Node type: ``DetectorYolox``
:Input: ``ImagePayload``
:Output: ``ImagePayload`` with ``meta['detections']``
:Extra: ``onnx``

.. code-block:: console

    $ pip install "juturna-nodes[onnx]"

The node README describes the models and where they are downloaded, the
output message, and the limits of the node.

Configuration
-------------

Default node arguments, as defined in the node ``config.toml`` file. Any of
them can be overridden in the node ``configuration`` of a pipeline.

.. literalinclude:: ../../../src/juturna/nodes/_detector_yolox/config.toml
    :language: toml

Pipeline usage
--------------

.. code-block:: json

    {
      "name": "detector",
      "type": "DetectorYolox",
      "configuration": { "model": "yolox_nano", "targets": ["person", "car"] }
    }

Reference
---------

.. autoclass:: juturna.nodes._detector_yolox.detector_yolox.DetectorYolox
    :no-index:
