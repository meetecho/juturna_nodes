# juturna-nodes

The officially supported node collection for
[Juturna](https://github.com/meetecho/juturna), the Python library for building
real-time, modular data pipelines.

Juturna pipelines are graphs of nodes: sources produce data (audio and video
streams, HTTP requests, files, ...), processing nodes transform it
(transcription, voice activity detection, object detection, ...), and sinks
deliver the results (HTTP endpoints, databases, UDP sockets, ...). This
package provides a set of ready-to-use nodes, maintained by the Juturna team,
that install into the `juturna.nodes` namespace.

## Installation

`juturna-nodes` requires Python 3.12 or newer, and installs the Juturna core
library as a dependency.

```bash
pip install juturna-nodes
```

Nodes with heavy dependencies (media libraries, machine learning models) are
available through optional extras, so that you only install what you need:

| Extra      | Dependencies                     | Nodes                                    |
| ---------- | -------------------------------- | ---------------------------------------- |
| `av`       | `av`                             | `AudioFile`, `AudioRtp`, `VideoRtp`      |
| `audio-ml` | `faster-whisper`, `silero-vad`   | `TranscriberWhisper`, `VadSilero`        |
| `vision`   | `ultralytics`                    | `DetectorYolo`                           |
| `warp`     | `juturna[warp]` (gRPC)           | `Warp`                                   |
| `all`      | all of the above                 | all nodes                                |

```bash
pip install "juturna-nodes[av,audio-ml]"
pip install "juturna-nodes[all]"
```

To install from source:

```bash
git clone https://github.com/meetecho/juturna_nodes.git
cd juturna_nodes
pip install -e ".[all]"
```

## Available nodes

### Sources

| Node            | Description                                                 | Extra |
| --------------- | ----------------------------------------------------------- | ----- |
| `AudioFile`     | Read an audio file, and chunk it into audio messages        | `av`  |
| `AudioRtp`      | Consume an RTP audio stream                                 | `av`  |
| `VideoRtp`      | Consume an RTP video stream                                 | `av`  |
| `FileWatcher`   | Watch a filesystem location, and emit filesystem events     |       |
| `JsonHTTP`      | Receive JSON content from `POST` requests on an HTTP server |       |
| `JsonWebsocket` | Expose a websocket server, and receive data from it         |       |
| `BrowserInput`  | Receive messages from the web page hosting a pipeline       |       |

### Processing

| Node                  | Description                                          | Extra      |
| --------------------- | ---------------------------------------------------- | ---------- |
| `VadSilero`           | Voice activity detection with the Silero VAD model   | `audio-ml` |
| `TranscriberWhisper`  | Transcribe audio with Whisper models                 | `audio-ml` |
| `TranscriberKroko`    | Transcribe audio with a Kroko server (WIP)           |            |
| `DetectorYolo`        | Detect and annotate objects in frames with YOLO      | `vision`   |
| `PassthroughIdentity` | Forward input messages after a delay (for testing)   |            |
| `Warp`                | Run a node remotely, over gRPC                       | `warp`     |

### Sinks

| Node            | Description                                  | Extra |
| --------------- | -------------------------------------------- | ----- |
| `NotifierHTTP`  | Send messages to an HTTP endpoint            |       |
| `NotifierMongo` | Store messages in a MongoDB collection       |       |
| `NotifierUDP`   | Send messages to a UDP socket                |       |
| `BrowserOutput` | Send messages to the web page hosting it     |       |

Every node folder in `src/juturna/nodes/` includes a `config.toml` file with
the node arguments and their default values, and a `README.md` file with
further details.

## Usage

Installed nodes are used in a pipeline configuration by class name. The node
`configuration` overrides the default arguments of the node:

```json
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
```

The pipeline can be validated and launched with the Juturna CLI:

```bash
juturna validate -c live_transcription.json
juturna launch -c live_transcription.json
```

Alternatively, `juturna create` interactively builds a pipeline configuration,
listing all the installed nodes.

Nodes can also be imported directly, for instance to use them in code or to
extend them:

```python
from juturna.nodes import AudioRtp, NotifierHTTP
```

Nodes are imported lazily, so importing a node only requires the dependencies
of that node.

## Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for the
development setup, the code quality checks, and a guide to writing and
submitting a new node.

To report a security vulnerability, please follow the process described in
[SECURITY.md](SECURITY.md), and do not open a public issue.

## License

`juturna-nodes` is released under the [MIT License](LICENSE).
Copyright © Meetecho s.r.l.
