# NotifierConsole

Print every received message on the standard output, one line per message.
Use it to see what a pipeline produces while you try it out, for example the
text coming out of a transcriber.

- **Role:** sink
- **Node type:** `NotifierConsole`
- **Input:** any payload
- **Output:** none
- **Extra:** none

## Arguments

The node takes no arguments.

## Input message

Each line starts with the name of the node that sent the message
(`message.creator`) in square brackets. The rest depends on the payload:

| Payload | What is printed |
| --- | --- |
| `ObjectPayload` with a `transcript` list | The `word` fields of the list joined into one line, as sent by `TranscriberWhisper`, `TranscriberKroko` and `TranscriberSherpa`. An empty list prints nothing. |
| `ObjectPayload` with a `text` string | The text, trimmed, as sent by `PrompterOllama`. |
| Any other `ObjectPayload` | The payload as compact JSON; values that are not JSON types are converted with `str()`. |
| Any other payload | The payload type, for example `<AudioPayload>`. |

`meta` is not read.

## Output message

The node does not transmit messages.

## Example

```json
{
  "name": "console",
  "type": "NotifierConsole",
  "configuration": {}
}
```

Linked after a transcriber, it prints lines like:

```
[whisper] Juturna is a Python library for real-time pipelines.
```
