.. _install:

Install
=======

juturna-nodes requires Python 3.12 or newer, and installs the Juturna core
library as a dependency. We assume you are working in a virtual environment:

.. code-block:: console

    $ python3 -m venv .venv
    $ source .venv/bin/activate
    (.venv) $ pip install juturna-nodes

You can also fetch the source code from the
`GitHub repository <https://github.com/meetecho/juturna_nodes>`_ and install it
manually:

.. code-block:: console

    (.venv) $ git clone https://github.com/meetecho/juturna_nodes
    (.venv) $ pip install ./juturna_nodes

Extras
------

The base installation includes all the nodes with lightweight dependencies.
Each node that needs heavy dependencies (media libraries, machine learning
models) has its own optional extra, named after the node folder with dashes:

.. list-table::
    :header-rows: 1

    * - Extra
      - Dependencies
      - Node
    * - ``audio-file``
      - ``av``
      - :ref:`AudioFile <node-audio-file>`
    * - ``audio-rtp``
      - ``av``
      - :ref:`AudioRtp <node-audio-rtp>`
    * - ``video-rtp``
      - ``av``
      - :ref:`VideoRtp <node-video-rtp>`
    * - ``video-capture``
      - ``av``
      - :ref:`VideoCapture <node-video-capture>`
    * - ``mic-source``
      - ``sounddevice``
      - :ref:`MicSource <node-mic-source>`
    * - ``speaker-sink``
      - ``sounddevice``
      - :ref:`SpeakerSink <node-speaker-sink>`
    * - ``transcriber-sherpa``
      - ``sherpa-onnx``
      - :ref:`TranscriberSherpa <node-transcriber-sherpa>`
    * - ``synthesizer-sherpa``
      - ``sherpa-onnx``
      - :ref:`SynthesizerSherpa <node-synthesizer-sherpa>`
    * - ``transcriber-whisper``
      - ``faster-whisper``
      - :ref:`TranscriberWhisper <node-transcriber-whisper>`
    * - ``vad-silero``
      - ``silero-vad``
      - :ref:`VadSilero <node-vad-silero>`
    * - ``detector-yolo``
      - ``ultralytics``
      - :ref:`DetectorYolo <node-detector-yolo>`
    * - ``detector-yolox``
      - ``onnxruntime``
      - :ref:`DetectorYolox <node-detector-yolox>`
    * - ``warp``
      - ``juturna[warp]``
      - :ref:`Warp <node-warp>`

Three groups install several extras at once:

- ``audio``: ``audio-file``, ``audio-rtp``, ``mic-source``, ``speaker-sink``,
  ``transcriber-sherpa``, ``synthesizer-sherpa``, ``transcriber-whisper`` and
  ``vad-silero``
- ``video``: ``video-rtp``, ``video-capture``, ``detector-yolo`` and
  ``detector-yolox``
- ``all``: ``audio``, ``video`` and ``warp``

.. code-block:: console

    (.venv) $ pip install "juturna-nodes[audio-rtp,transcriber-whisper]"
    (.venv) $ pip install "juturna-nodes[all]"

Nodes are imported lazily, so a node with missing dependencies only fails when
it is used, without affecting the others.

The machine learning nodes can use a GPU, when available, through the
``device`` argument.

Development extras
------------------

A number of extra groups are available to manage the development dependencies:

- ``doc``: Sphinx and its extensions, to build this documentation
- ``dev``: pre-commit hooks, bandit and commit message validation
- ``lint``: ruff
- ``test``: pytest and coverage
- ``dev_full``: all of the above

To build the documentation:

.. code-block:: console

    (.venv) $ pip install -e ".[all,doc]"
    (.venv) $ make -C docs html
