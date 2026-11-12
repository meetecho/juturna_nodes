.. _node-detector-yolo:

``DetectorYolo``
================

:bdg-primary:`processing` :bdg-secondary-line:`extra: vision`

Annotate frames using YOLO models.
For more info about the models, see here: https://github.com/ultralytics/ultralytics

.. note::

    The ``vision`` extra installs ``ultralytics``, which is distributed under
    the AGPL-3.0 license, unlike juturna-nodes (MIT). Check that its terms are
    compatible with your use before installing it.

:Node type: ``DetectorYolo``
:Input: ``ImagePayload``
:Output: ``ImagePayload``
:Extra: ``vision``

.. code-block:: console

    $ pip install "juturna-nodes[vision]"

Configuration
-------------

Default node arguments, as defined in the node ``config.toml`` file. Any of
them can be overridden in the node ``configuration`` of a pipeline.

.. literalinclude:: ../../../src/juturna/nodes/_detector_yolo/config.toml
    :language: toml

Pipeline usage
--------------

.. code-block:: json

    {
      "name": "detector_yolo",
      "type": "DetectorYolo",
      "configuration": {}
    }

Reference
---------

.. autoclass:: juturna.nodes._detector_yolo.detector_yolo.DetectorYolo
    :no-index:
