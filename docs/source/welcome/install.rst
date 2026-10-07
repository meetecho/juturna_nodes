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
Nodes that need heavy dependencies (media libraries, machine learning models)
are enabled by optional extras:

.. list-table::
    :header-rows: 1

    * - Extra
      - Dependencies
      - Nodes
    * - ``av``
      - ``av``
      - :ref:`AudioFile <node-audio-file>`, :ref:`AudioRtp <node-audio-rtp>`,
        :ref:`VideoRtp <node-video-rtp>`
    * - ``audio-ml``
      - ``faster-whisper``, ``silero-vad``
      - :ref:`TranscriberWhisper <node-transcriber-whisper>`,
        :ref:`VadSilero <node-vad-silero>`
    * - ``vision``
      - ``ultralytics``
      - :ref:`DetectorYolo <node-detector-yolo>`
    * - ``warp``
      - ``juturna[warp]``
      - :ref:`Warp <node-warp>`
    * - ``all``
      - all of the above
      - all nodes

.. code-block:: console

    (.venv) $ pip install "juturna-nodes[av,audio-ml]"
    (.venv) $ pip install "juturna-nodes[all]"

Nodes are imported lazily, so a node with missing dependencies only fails when
it is used, without affecting the others.

Some nodes need system packages as well: the ``av`` nodes rely on the FFmpeg
libraries, and the machine learning nodes can use a GPU, when available,
through the ``device`` argument.

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
