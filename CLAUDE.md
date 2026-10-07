# CLAUDE.md

This repository is **juturna-nodes**, the collection of officially maintained
nodes for [juturna](https://github.com/meetecho/juturna). Juturna is a Python
library for building real-time data pipelines (audio, video, JSON, ...) as DAGs
of nodes. This package contains node implementations only. Pipelines, the node
builder and the CLI live in the juturna core library (`juturna>=3.0.0`).

## Namespaces and packaging

Juturna loads nodes **only** from three namespaces:

| Namespace                       | Maintained by          | Node type in a pipeline        |
| ------------------------------- | ---------------------- | ------------------------------ |
| `juturna.nodes`                 | us (this repository)   | `AudioRtp`, `sub.MyNode`       |
| `juturna.extensions`            | external               | `extensions.nodes.MyNode`      |
| `juturna.contrib.<author>`      | external, per author   | `contrib.<author>.nodes.MyNode`|

- The core's `juturna/__init__.py` extends its `__path__`
  (`pkgutil.extend_path`), so other installed distributions can provide
  subpackages of `juturna`.
- This repository ships **only** `juturna/nodes`. Never add
  `src/juturna/__init__.py`: it would shadow the core package.
  - The hatch wheel config enforces this: `only-include = ["src/juturna/nodes"]`
    with `sources = ["src"]`.
- Subpackages are supported. For example, `src/juturna/nodes/nextip/` is used
  with type `nextip.MyNode` and imported with
  `from juturna.nodes.nextip import MyNode`.
  - A subpackage needs its own `__init__.py` with the same lazy-loader pattern.
- Python namespaces are not protected. Any installed distribution can provide
  these modules, so restricting the namespaces is a convention, not a security
  boundary.

## Repository layout

```
src/juturna/nodes/
  __init__.py              # registry: _AVAILABLE_PLUGINS + lazy loaders
  _<node_name>/            # one folder per node, underscore-prefixed
    <node_name>.py         # node class
    config.toml            # default arguments (required)
    README.md              # node documentation
    requirements.txt       # legacy, optional; real deps go in pyproject extras
    *.template             # optional files compiled at runtime (e.g. SDP)
```

### Node registry (`__init__.py`)

```python
# noqa: D104
from juturna.components._node_builder._utils import _lazy_node_loaders


_AVAILABLE_PLUGINS: dict[str, str] = {
    'AudioRtp': '._audio_rtp.audio_rtp',
    # 'ClassName': '._<node_name>.<node_name>',
}


__getattr__, __dir__ = _lazy_node_loaders(__name__, _AVAILABLE_PLUGINS)
__all__ = list(_AVAILABLE_PLUGINS.keys())
```

- The **key must match the class name exactly**. The loader calls
  `getattr(module, key)`.
- Module paths are **relative and start with a dot**. They are resolved with
  `importlib.import_module(path, package=__name__)`.
- Nodes are imported lazily, on first attribute access. This keeps heavy
  optional dependencies (av, pymongo, grpc, ...) from loading until a node that
  needs them is used.
- `juturna create` lists the nodes from `__all__`. It finds each node's
  `config.toml` through `_AVAILABLE_PLUGINS` and `importlib.util.find_spec`,
  without importing the node module.

## How a node is built

For a node entry `{"name": ..., "type": ..., "configuration": {...}}` in a
pipeline, the builder in core (`juturna.components._node_builder._builder`):

1. **Resolves the type.**
   - `AudioRtp` → `juturna.nodes.AudioRtp`
   - `sub.X` → `juturna.nodes.sub.X`
   - `extensions...` / `contrib...` → `juturna.<type>`
2. **Reads `config.toml`** next to the node module, through
   `importlib.resources.files(cls.__module__)`.
   - The file is mandatory and must have an `[arguments]` table.
   - A `[meta]` table is conventionally present, and may be empty.
3. **Merges the configuration.** Every key of `[arguments]` is taken from the
   pipeline `configuration` when present, otherwise from the default.
   - **Keys not declared in `config.toml` are silently dropped.** Every
     argument a node accepts must be declared there.
4. **Resolves environment variables.** String values starting with `$JT_ENV_`
   (for example `"$JT_ENV_MONGO_URI"`) are read from the environment variable
   with that name, without the prefix. The build fails if the variable is
   unset.
5. **Instantiates the class.**
   `cls(**arguments, node_name=..., pipe_name=..., synchroniser=..., transport=...)`
6. **Calls `node.configure()`.**

## Writing a node

```python
from juturna.components import Node, Message
from juturna.payloads import ObjectPayload


class MyNode(Node[ObjectPayload, ObjectPayload]):  # Node[T_Input, T_Output]
    """One-line description"""

    def __init__(self, threshold: float, **kwargs):
        """
        Parameters
        ----------
        threshold : float
            ...
        kwargs : dict
            Superclass arguments.

        """
        super().__init__(**kwargs)  # always forward kwargs

        self._threshold = threshold

    def update(self, message: Message[ObjectPayload], **kwargs):
        """Receive a message, transmit a message"""
        state = kwargs.get('state')  # per-node persistent state (dict-like)

        out = Message[ObjectPayload](
            creator=self.name,
            version=message.version,
            timers_from=message,
            payload=message.payload,
        )

        self.transmit(out)
```

### Lifecycle hooks

All of these are optional to override.

| Hook | When it is called |
| --- | --- |
| `__init__(**args, **kwargs)` | at build time; the arguments come from `config.toml` |
| `configure()` | at build time, right after `__init__`; e.g. claim ports with `rb.get('port')` when `port == 'auto'` |
| `warmup()` | on `pipeline.warmup()`; open sockets, spawn (not start) workers, prepare templates |
| `start()` | on `pipeline.start()`; **must call `super().start()`** |
| `update(message, **kwargs)` | for each batch delivered by the node's buffer; `kwargs['state']` is the node state |
| `set_on_config(prop, value)` | hot-swap a property at runtime |
| `stop()` | on `pipeline.stop()`; **must call `super().stop()`**, usually before stopping its own workers |
| `destroy()` | on `pipeline.destroy()`; release resources |
| `configuration` (property) | extend `super().configuration` to expose node config |
| `next_batch(sources) -> dict[str, list[int]]` | optional custom synchroniser for multi-input nodes; `sources` maps an origin to its buffered messages, and the return value maps an origin to the indices to deliver |

### Data flow

- **Internal workers.** `start()` spawns a worker that moves the input queue
  into the buffer, and an update worker that calls `update()` with the batches
  selected by the synchroniser.
  - The default synchroniser is `passthrough`, which delivers every message.
  - A pipeline node can set `"sync": "passthrough" | "local"`; `local` means
    `next_batch` is used.
- **Output.** `self.transmit(message)` freezes the message and puts it into
  every destination's queue. A message is immutable once transmitted.
- **Source nodes** produce data without upstream links. There are two
  patterns:
  - `self.set_source(callable, by=seconds, mode='pre'|'post')`: the callable
    returns a `Message`, or `None` to skip. It is called in a loop, and its
    result is put into the node's own queue, so it reaches `update()`.
  - Feed the queue directly from your own worker, server handler or socket
    reader with `self.put(message)`, as `JsonHttp`, `AudioRtp` and
    `VideoRtp` do.
- **Concurrency.** Never use `threading` directly. Use the node transport:
  - `self._transport.spawn(target=..., name=..., daemon=True)` returns a
    `WorkerHandle`
  - `self._transport.new_queue(maxsize=...)` and `self._transport.new_event()`
  - The types come from `juturna.transport` (`Queue`, `Event`, `Empty`,
    `WorkerHandle`).
- **Timeouts.** Use the constants from `juturna.meta`:
  `JUTURNA_THREAD_JOIN_TIMEOUT`, `JUTURNA_DRAIN_TIMEOUT` and
  `JUTURNA_MAX_QUEUE_SIZE`.
- **Error handling.** Exceptions raised in `update()` or in source callables
  are logged and counted by the base class; they don't kill the node. Use
  `self.logger` (already named `<pipe>.<node>`).
- **Node attributes.** `self.name`, `self.pipe_name`, `self.pipe_id` and
  `self.pipe_path` (the pipeline runtime folder).
- **Node files.** `self.static_path` is the node's own folder.
  - `self.prepare_template(template_name, dest_name, args)` compiles a
    `string.Template` file from the node folder into `pipe_path`.
  - `self.dump_json(message, file_name)` writes a message to `pipe_path`.

### Messages and payloads

- **`Message[T]`.**
  - Constructor fields: `creator`, `version`, `payload`, and `timers_from`
    (copies the timers of another message).
  - Each message also gets an automatic `id` and `created_at`, and has a
    `meta` dict.
  - Timing helpers: `message.timer(...)` and `message.timeit(...)`.
  - Serialization: `to_dict()` and `to_json()`.
- **Payloads** come from `juturna.payloads` and are frozen dataclasses:

  | Payload | Fields |
  | --- | --- |
  | `AudioPayload` | `audio` (ndarray), `sampling_rate`, `audio_format`, `channels`, `start`, `end` |
  | `ImagePayload` | `image`, `width`, `height`, `depth`, `pixel_format`, `timestamp` |
  | `VideoPayload` | `video` (list of `ImagePayload`), `frames_per_second`, `codec`, `start`, `end` |
  | `BytesPayload` | `cnt` |
  | `ObjectPayload` | a dict subclass; build it with `ObjectPayload.from_dict(...)` |
  | `Batch` | `messages` (a tuple) |
  | `BasePayload` | the base class, used as a generic placeholder |

- **Building payloads.** Frozen payloads are built incrementally with
  `Draft(PayloadType, copy_from=...)`: set its attributes, then call
  `.compile()`. `payload.clone()` copies an existing one.

## Pipeline configuration (for reference and testing)

```json
{
  "version": "3.0.0",
  "pipeline": {
    "name": "my_pipeline",
    "id": "1234",
    "folder": "./running_pipelines",
    "nodes": [
      { "name": "src", "type": "AudioRtp", "configuration": { "port": "auto" } },
      { "name": "out", "type": "NotifierHTTP", "configuration": {} }
    ],
    "links": [ { "from": "src", "to": "out" } ]
  }
}
```

- **Removed keys.** The legacy keys `plugins` and `mark`, and the
  `source`/`proc`/`sink` types, no longer exist. Node roles come only from the
  graph shape.
- **Warped nodes.** A node with `"warped": true` and a `warp_configuration` is
  replaced by a `Warp` node, which runs the real node remotely over gRPC.
  `Warp` is a generic node: `Warp[T_Input, T_Output]`.
- **Core CLI commands:**
  - `juturna create`: interactive builder; lists the installed nodes of all
    three namespaces
  - `juturna validate`: checks a pipeline file (no cycles; warns about
    unlinked nodes)
  - `juturna launch`: runs a pipeline
  - `juturna serve`: HTTP service
  - `juturna remotize`: serves a single node over gRPC
  - `juturna stub`: generates a contrib node skeleton in
    `src/juturna/contrib/<pkg>/nodes/`. For this repository, create the node
    folder under `src/juturna/nodes/` instead, and register it by hand.

## Adding a node: checklist

1. Create `src/juturna/nodes/_<node_name>/<node_name>.py` with a class
   subclassing `Node[In, Out]`.
2. Add `config.toml` with **every** constructor argument under `[arguments]`,
   plus an empty `[meta]` table.
3. Register the node in `_AVAILABLE_PLUGINS`. The key must match the class name
   exactly, and the path is relative with a leading dot.
4. Declare third-party dependencies as an optional extra in `pyproject.toml`
   (`[project.optional-dependencies]`), and include it in `all`.
   - The core only depends on `numpy`. Nothing else (`av`, `requests`,
     `websockets`, `pymongo`, ...) is provided transitively.
5. Write a `README.md` in the node folder covering what the node does, its
   arguments, its input and output payloads, and the extra it needs.
6. Check that `from juturna.nodes import <Class>` works after installing.

## Development

- **Python:** `requires-python >= 3.12`. Generic class syntax
  (`class Node[T_Input, T_Output]`) is used throughout.
- **Local juturna:** until juturna 3.0.0 is published, `[tool.uv.sources]`
  points `juturna` at the local checkout (`../juturna_private`, editable).
  uv ignores this when building the package.
- **Install:** `uv sync --all-extras`, or `pip install -e ".[all]"`.
- **Style:** follow the core's ruff config.
  - 80-character lines and single quotes.
  - NumPy-style docstrings with `Parameters` sections, and the summary on the
    line after the opening quotes for multi-line docstrings.
  - A module docstring header with `@ Author` / `@ Email`.
  - A blank line after `return` / `continue` blocks, as in the existing nodes.
- **Commits:** conventional commits (`feat:`, `fix:`, `refactor:`, `test:`,
  `chore:`, ...).
