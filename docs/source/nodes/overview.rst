.. _nodes-overview:

Overview
========

Nodes are grouped by their role in a pipeline: sources produce data, processing
nodes transform it, and sinks deliver it. Each node page lists its input and
output payloads, its default arguments, and the extra required to install it.

Sources
-------

.. list-table::
    :header-rows: 1
    :widths: 25 55 20

    * - Node
      - Description
      - Extra
    * - :ref:`AudioFile <node-audio-file>`
      - Read an audio file, and chunk it into audio messages
      - ``av``
    * - :ref:`AudioRtp <node-audio-rtp>`
      - Consume an RTP audio stream
      - ``av``
    * - :ref:`VideoRtp <node-video-rtp>`
      - Consume an RTP video stream
      - ``av``
    * - :ref:`FileWatcher <node-file-watcher>`
      - Watch a filesystem location, and emit filesystem events
      - --
    * - :ref:`JsonHTTP <node-json-http>`
      - Receive JSON content from ``POST`` requests on an HTTP server
      - --
    * - :ref:`JsonWebsocket <node-json-websocket>`
      - Expose a websocket server, and receive data from it
      - --

Processing
----------

.. list-table::
    :header-rows: 1
    :widths: 25 55 20

    * - Node
      - Description
      - Extra
    * - :ref:`VadSilero <node-vad-silero>`
      - Voice activity detection with the Silero VAD model
      - ``audio-ml``
    * - :ref:`TranscriberWhisper <node-transcriber-whisper>`
      - Transcribe audio with Whisper models
      - ``audio-ml``
    * - :ref:`TranscriberKroko <node-transcriber-kroko>`
      - Transcribe audio with a Kroko server (WIP)
      - --
    * - :ref:`DetectorYolo <node-detector-yolo>`
      - Detect and annotate objects in frames with YOLO
      - ``vision``
    * - :ref:`PassthroughIdentity <node-passthrough-identity>`
      - Forward input messages after a delay (for testing)
      - --
    * - :ref:`Warp <node-warp>`
      - Run a node remotely, over gRPC
      - ``warp``

Sinks
-----

.. list-table::
    :header-rows: 1
    :widths: 25 55 20

    * - Node
      - Description
      - Extra
    * - :ref:`NotifierHTTP <node-notifier-http>`
      - Send messages to an HTTP endpoint
      - --
    * - :ref:`NotifierMongo <node-notifier-mongo>`
      - Store messages in a MongoDB collection
      - --
    * - :ref:`NotifierUDP <node-notifier-udp>`
      - Send messages to a UDP socket
      - --
