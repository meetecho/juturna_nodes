# PrompterOllama

Send the text of each message to a model served by
[Ollama](https://ollama.com) and transmit the answer. Every message is a new
question: the node keeps no conversation history. It talks to the Ollama REST
API (`POST /api/chat`) with `requests`, so it needs no extra.

- **Role:** processing
- **Node type:** `PrompterOllama`
- **Input:** `ObjectPayload`
- **Output:** `ObjectPayload`
- **Extra:** none (needs a running Ollama server)

Install Ollama and pull a model before starting the pipeline, for example:

```console
ollama pull qwen2.5:0.5b
```

On warmup the node sends an empty chat to load the model, so the first
question is not slowed down; warmup fails if the server is not reachable.

## Arguments

| Argument        | Type    | Default                    | Description |
| --------------- | ------- | -------------------------- | ----------- |
| `endpoint`      | `str`   | `"http://localhost:11434"` | Base address of the Ollama server |
| `model_name`    | `str`   | `"qwen2.5:0.5b"`           | Model to chat with, as listed by `ollama list` |
| `system_prompt` | `str`   | short voice-assistant prompt | System message sent before every question; empty for none |
| `keep_alive`    | `str`   | `"5m"`                     | How long Ollama keeps the model loaded after a request (`"-1"` for ever, `"0"` to unload at once) |
| `think`         | `bool`  | `false`                    | Let models that support it reason before answering |
| `timeout`       | `float` | `60.0`                     | Seconds to wait for each answer |

## Input message

| Field | Use |
| --- | --- |
| `payload['text']` | The question, required. Leading and trailing spaces are removed; an empty or missing text is ignored |

`meta` is not read. `TranscriberSherpa` produces this format.

## Output message

| Field | Content |
| --- | --- |
| `payload['prompt']` | The question sent to the model |
| `payload['text']` | The answer of the model, trimmed |

The message keeps the version and the timers of the input message, and adds
a `<node name>` timer with the duration of the request. `meta` is empty. If
the request fails (server down, timeout, HTTP error), the error is logged and
nothing is transmitted.

## Example

```json
{
  "name": "llm",
  "type": "PrompterOllama",
  "configuration": { "model_name": "qwen2.5:0.5b" }
}
```
