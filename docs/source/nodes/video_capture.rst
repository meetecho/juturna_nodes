.. _node-video-capture:

``VideoCapture``
================

:bdg-primary:`source` :bdg-secondary-line:`extra: av`

Read video from a file or from a V4L2 webcam, and transmit one RGB frame per
message.

:Node type: ``VideoCapture``
:Input: --
:Output: ``ImagePayload``
:Extra: ``av``

.. code-block:: console

    $ pip install "juturna-nodes[av]"

The node README describes how files and webcams are read, the output message,
and the limits of the node.

Configuration
-------------

Default node arguments, as defined in the node ``config.toml`` file. Any of
them can be overridden in the node ``configuration`` of a pipeline.

.. literalinclude:: ../../../src/juturna/nodes/_video_capture/config.toml
    :language: toml

Pipeline usage
--------------

.. code-block:: json

    {
      "name": "camera",
      "type": "VideoCapture",
      "configuration": { "source": "/dev/video0", "fps": 5 }
    }

Reference
---------

.. autoclass:: juturna.nodes._video_capture.video_capture.VideoCapture
    :no-index:
