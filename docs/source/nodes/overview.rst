.. _nodes-overview:

Overview
========

Nodes are grouped by their role in a pipeline: sources produce data, processing
nodes transform it, and sinks deliver it. Each node page lists its input and
output payloads, its default arguments, and the extra required to install it.
The last column lists the licenses of the third-party runtimes and models a
node pulls in beyond the juturna core and NumPy (``--`` when there are none);
the node code is MIT, and each node page has the details and sources.

Sources
-------

.. list-table::
    :header-rows: 1
    :widths: 20 40 12 28

    * - Node
      - Description
      - Extra
      - Third-party licenses
    * - :ref:`AudioFile <node-audio-file>`
      - Read an audio file, and chunk it into audio messages
      - ``audio-file``
      - GPL (bundled FFmpeg built with x264/x265); PyAV BSD-3-Clause
    * - :ref:`AudioRtp <node-audio-rtp>`
      - Consume an RTP audio stream
      - ``audio-rtp``
      - GPL (bundled FFmpeg built with x264/x265); PyAV BSD-3-Clause
    * - :ref:`VideoRtp <node-video-rtp>`
      - Consume an RTP video stream
      - ``video-rtp``
      - GPL (bundled FFmpeg built with x264/x265); PyAV BSD-3-Clause
    * - :ref:`VideoCapture <node-video-capture>`
      - Read video from a file or a webcam
      - ``video-capture``
      - GPL (bundled FFmpeg built with x264/x265); PyAV BSD-3-Clause
    * - :ref:`FileWatcher <node-file-watcher>`
      - Watch a filesystem location, and emit filesystem events
      - --
      - Apache-2.0
    * - :ref:`JsonHTTP <node-json-http>`
      - Receive JSON content from ``POST`` requests on an HTTP server
      - --
      - --
    * - :ref:`JsonWebsocket <node-json-websocket>`
      - Expose a websocket server, and receive data from it
      - --
      - BSD-3-Clause
    * - :ref:`BrowserInput <node-browser-input>`
      - Receive messages from the web page hosting a browser pipeline
      - --
      - MPL-2.0 (Pyodide)
    * - :ref:`MicSource <node-mic-source>`
      - Capture audio from a microphone, with push-to-talk
      - ``mic-source``
      - MIT

Processing
----------

.. list-table::
    :header-rows: 1
    :widths: 20 40 12 28

    * - Node
      - Description
      - Extra
      - Third-party licenses
    * - :ref:`VadSilero <node-vad-silero>`
      - Voice activity detection with the Silero VAD model
      - ``vad-silero``
      - MIT; PyTorch BSD-3-Clause
    * - :ref:`TranscriberWhisper <node-transcriber-whisper>`
      - Transcribe audio with Whisper models
      - ``transcriber-whisper``
      - MIT; PyAV with GPL FFmpeg; ONNX Runtime MIT
    * - :ref:`TranscriberKroko <node-transcriber-kroko>`
      - Transcribe audio with a Kroko server
      - --
      - Apache-2.0 server; websockets BSD-3-Clause; models CC-BY-SA (no license text)
    * - :ref:`TranscriberSherpa <node-transcriber-sherpa>`
      - Transcribe audio with sherpa-onnx streaming models
      - ``transcriber-sherpa``
      - Apache-2.0
    * - :ref:`PrompterOllama <node-prompter-ollama>`
      - Ask a model served by Ollama
      - --
      - MIT; requests Apache-2.0; model license varies (default Apache-2.0)
    * - :ref:`SynthesizerSherpa <node-synthesizer-sherpa>`
      - Synthesize speech from text with sherpa-onnx
      - ``synthesizer-sherpa``
      - Apache-2.0; default voice weights and lexicon state no license
    * - :ref:`DetectorYolo <node-detector-yolo>`
      - Detect and annotate objects in frames with YOLO
      - ``detector-yolo``
      - AGPL-3.0 (code and weights); PyTorch BSD-3-Clause; opencv-python Apache-2.0
    * - :ref:`DetectorYolox <node-detector-yolox>`
      - Detect objects in frames with YOLOX on ONNX Runtime
      - ``detector-yolox``
      - Apache-2.0 (YOLOX, requests); ONNX Runtime MIT
    * - :ref:`DetectionEvents <node-detection-events>`
      - Turn the detections of frames into JSON events
      - --
      - --
    * - :ref:`PassthroughIdentity <node-passthrough-identity>`
      - Forward input messages after a delay (for testing)
      - --
      - --
    * - :ref:`Warp <node-warp>`
      - Run a node remotely, over gRPC
      - ``warp``
      - grpcio Apache-2.0; protobuf BSD-3-Clause

Sinks
-----

.. list-table::
    :header-rows: 1
    :widths: 20 40 12 28

    * - Node
      - Description
      - Extra
      - Third-party licenses
    * - :ref:`NotifierHTTP <node-notifier-http>`
      - Send messages to an HTTP endpoint
      - --
      - Apache-2.0
    * - :ref:`NotifierMongo <node-notifier-mongo>`
      - Store messages in a MongoDB collection
      - --
      - Apache-2.0
    * - :ref:`NotifierUDP <node-notifier-udp>`
      - Send messages to a UDP socket
      - --
      - --
    * - :ref:`NotifierConsole <node-notifier-console>`
      - Print messages on the terminal
      - --
      - --
    * - :ref:`AudioWriter <node-audio-writer>`
      - Write audio messages to a WAV file
      - --
      - --
    * - :ref:`SpeakerSink <node-speaker-sink>`
      - Play audio messages on a speaker
      - ``speaker-sink``
      - MIT
    * - :ref:`BrowserOutput <node-browser-output>`
      - Send messages to the web page hosting a browser pipeline
      - --
      - MPL-2.0 (Pyodide)
