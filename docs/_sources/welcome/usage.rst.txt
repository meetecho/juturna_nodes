.. _usage:

Usage
=====

Installed nodes are part of the ``juturna.nodes`` namespace, and are used in a
pipeline configuration by class name.

Nodes in a pipeline
-------------------

Each node in a pipeline configuration has a ``name``, unique in the pipeline,
a ``type``, the class name of the node, and a ``configuration``, overriding
the default node arguments:

.. code-block:: json

    {
      "version": "3.0.0",
      "pipeline": {
        "name": "live_transcription",
        "id": "transcription_01",
        "folder": "./running_pipelines",
        "nodes": [
          {
            "name": "0_src",
            "type": "AudioRtp",
            "configuration": { "port": 8888 }
          },
          {
            "name": "1_vad",
            "type": "VadSilero",
            "configuration": {}
          },
          {
            "name": "2_transcriber",
            "type": "TranscriberWhisper",
            "configuration": { "model_name": "small", "language": "en" }
          },
          {
            "name": "3_dst",
            "type": "NotifierHTTP",
            "configuration": { "endpoint": "http://localhost:8080/transcripts" }
          }
        ],
        "links": [
          { "from": "0_src", "to": "1_vad" },
          { "from": "1_vad", "to": "2_transcriber" },
          { "from": "2_transcriber", "to": "3_dst" }
        ]
      }
    }

Only the arguments declared by a node can be configured: any other key in the
node ``configuration`` is ignored. String values starting with ``$JT_ENV_`` are
read from the environment, so that secrets do not need to be stored in the
configuration file:

.. code-block:: json

    {
      "name": "3_dst",
      "type": "NotifierMongo",
      "configuration": { "endpoint": "$JT_ENV_MONGO_URI" }
    }

Running a pipeline
------------------

Pipelines are validated and launched with the Juturna CLI:

.. code-block:: console

    (.venv) $ juturna validate -c live_transcription.json
    (.venv) $ juturna launch -c live_transcription.json

``juturna create`` builds a pipeline configuration interactively, listing all
the installed nodes.

Using nodes in code
-------------------

Nodes can also be imported directly, for instance to extend them:

.. code-block:: python

    from juturna.nodes import AudioRtp, NotifierHTTP
