.. _node-video-capture:

``VideoCapture``
================

:bdg-primary:`source` :bdg-secondary-line:`extra: video-capture`

Read video from a file or from a V4L2 webcam, and transmit one RGB frame per
message.

:Node type: ``VideoCapture``
:Input: --
:Output: ``ImagePayload``
:Extra: ``video-capture``

.. code-block:: console

    $ pip install "juturna-nodes[video-capture]"

The `node README
<https://github.com/meetecho/juturna_nodes/blob/main/src/juturna/nodes/_video_capture/README.md>`_
describes how files and webcams are read, the output message, and the limits
of the node.

When a webcam is unplugged, busy or stops delivering frames, the read fails:
the node closes the device, logs the error, counts it in
``health['source_failures']`` (with the error in ``health['last_failure']``),
and opens the device again after a wait that starts at 0.1 s and doubles at
every consecutive failure, up to ``JUTURNA_SOURCE_MAX_BACKOFF`` (5 s by
default). The wait goes back to 0.1 s after the first frame read. RTSP and
other network streams are not supported today: for RTP video use
:ref:`VideoRtp <node-video-rtp>`.

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
