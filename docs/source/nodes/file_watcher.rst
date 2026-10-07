.. _node-file-watcher:

``FileWatcher``
===============

:bdg-primary:`source`

Watch a location on the filesystem, and fire desired events.

This is a source node, it however does not set a source function. Internally,
the node creates event handlers for the desired events to watch, and those
handlers write directly on the node inbound queue.

:Node type: ``FileWatcher``
:Input: --
:Output: ``ObjectPayload``
:Extra: --

.. code-block:: console

    $ pip install juturna-nodes

Configuration
-------------

Default node arguments, as defined in the node ``config.toml`` file. Any of
them can be overridden in the node ``configuration`` of a pipeline.

.. literalinclude:: ../../../src/juturna/nodes/_file_watcher/config.toml
    :language: toml

Pipeline usage
--------------

.. code-block:: json

    {
      "name": "file_watcher",
      "type": "FileWatcher",
      "configuration": {}
    }

Reference
---------

.. autoclass:: juturna.nodes._file_watcher.file_watcher.FileWatcher
    :no-index:
