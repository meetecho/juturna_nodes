.. _new-node:

Write a new node
================

Nodes in this collection live in the ``juturna.nodes`` namespace, one folder
per node:

.. code-block:: text

    src/juturna/nodes/
      __init__.py                 # node registry
      _my_node/
        my_node.py                # node class
        config.toml               # default arguments
        README.md                 # node documentation

In short, a new node needs:

1. a class subclassing ``juturna.components.Node``, typed with its input and
   output payloads;
2. a ``config.toml`` file declaring the default value of every argument the
   node accepts (undeclared arguments are ignored);
3. an entry in the ``_AVAILABLE_PLUGINS`` mapping of
   ``src/juturna/nodes/__init__.py``, with the class name as key and the
   relative module path (``._my_node.my_node``) as value;
4. its third-party dependencies, declared in ``pyproject.toml``;
5. a documentation page in ``docs/source/nodes/``, added to the toctree of its
   role and to the :ref:`overview <nodes-overview>`.

The complete guide, with a node template, the lifecycle rules and the pull
request checklist, is in the
`contributing guidelines <https://github.com/meetecho/juturna_nodes/blob/main/CONTRIBUTING.md>`_.

If you are writing nodes for your own project, you do not need to contribute
them here: package them under ``juturna.contrib.<author>.nodes`` in your own
repository, and use them in a pipeline as ``contrib.<author>.nodes.MyNode``.
``juturna stub`` creates the skeleton of such a node for you.
