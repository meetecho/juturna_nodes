.. _node-video-rtp:

``VideoRtp``
============

:bdg-primary:`source` :bdg-secondary-line:`extra: av`

Consume RTP video streams using PyAv.

:Node type: ``VideoRtp``
:Input: --
:Output: ``ImagePayload``
:Extra: ``av``

.. code-block:: console

    $ pip install "juturna-nodes[av]"

Configuration
-------------

Default node arguments, as defined in the node ``config.toml`` file. Any of
them can be overridden in the node ``configuration`` of a pipeline.

.. literalinclude:: ../../../src/juturna/nodes/_video_rtp/config.toml
    :language: toml

Pipeline usage
--------------

.. code-block:: json

    {
      "name": "video_rtp",
      "type": "VideoRtp",
      "configuration": {}
    }

Reference
---------

.. autoclass:: juturna.nodes._video_rtp.video_rtp.VideoRtp
    :no-index:
