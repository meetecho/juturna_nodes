# PrompterOllama

Send the text of each message to a model served by
[Ollama](https://ollama.com) and transmit the answer sentence by sentence,
while the model writes it, so a speech synthesizer downstream can start
speaking before the answer is complete. Every message is a new question: the
node keeps no conversation history. It talks to the Ollama REST
API (`POST /api/chat`) with `requests`, so it needs no extra.

- **Role:** processing
- **Node type:** `PrompterOllama`
- **Input:** `ObjectPayload`
- **Output:** `ObjectPayload`
- **Extra:** none (needs a running Ollama server)

Install Ollama and pull a model before starting the pipeline, for example:

```console
ollama pull qwen2.5:1.5b
```

On warmup the node sends an empty chat to load the model, so the first
question is not slowed down; warmup fails if the server is not reachable.

## Choosing a model

Any model served by Ollama works: pull it and set `model_name`, nothing else
changes in the pipeline. Larger models answer more reliably and take longer
and more memory per answer. On 20 short questions, 3 runs each, on CPU:

- `qwen2.5:0.5b` answered 44 of 60 correctly, in 0.28 s (median);
- `qwen2.5:1.5b`, the default, answered 48 of 60 correctly with the plain
  voice-assistant prompt, and 55 of 60 with the default prompt, which also
  asks to write numbers as words, in 0.46 s (median).

The default prompt asks for numbers as words because the TTS lexicon has no
entries for digits: `SynthesizerSherpa` skips them. The model still writes
digits now and then (4 answers of 60 in the test above).

| `model_name`   | Download | License |
| -------------- | -------- | ------- |
| `qwen2.5:0.5b` | 398 MB   | Apache-2.0 |
| `gemma3:1b`    | 806 MB   | Gemma Terms of Use |
| `qwen2.5:1.5b` | 986 MB   | Apache-2.0 |
| `llama3.2:3b`  | 2.0 GB   | Llama 3.2 Community License |
| `qwen2.5:7b`   | 4.7 GB   | Apache-2.0 |

Sizes and licenses are those listed by the Ollama registry. Check the license
of the model you pick before shipping it in a product.

## Arguments

| Argument        | Type    | Default                    | Description |
| --------------- | ------- | -------------------------- | ----------- |
| `endpoint`      | `str`   | `"http://localhost:11434"` | Base address of the Ollama server |
| `model_name`    | `str`   | `"qwen2.5:1.5b"`           | Model to chat with, as listed by `ollama list` |
| `system_prompt` | `str`   | short voice-assistant prompt | System message sent before every question; empty for none |
| `keep_alive`    | `str`   | `"5m"`                     | How long Ollama keeps the model loaded after a request (`"-1"` for ever, `"0"` to unload at once) |
| `think`         | `bool`  | `false`                    | Let models that support it reason before answering |
| `timeout`       | `float` | `60.0`                     | Seconds to wait for the connection and between two pieces of the answer, the first one included; it does not bound the whole answer |
| `stream`        | `bool`  | `true`                     | Transmit the answer one sentence at a time; if `false`, transmit it whole once the model is done |

## Input message

| Field | Use |
| --- | --- |
| `payload['text']` | The question, required. Leading and trailing spaces are removed; an empty or missing text is ignored |

`meta` is not read. `TranscriberSherpa` produces this format.

A new question interrupts the answer in progress. Once the question reaches
the node, no further sentence of the old answer is transmitted, the request is
closed when the next piece of the answer arrives, and the questions still
waiting are skipped. The sentences already transmitted are not called back: the nodes
downstream (for instance `SynthesizerSherpa` and `SpeakerSink`) still process
them.

## Output message

One message per sentence of the answer, or a single message with the whole
answer if `stream` is `false`.

| Field | Content |
| --- | --- |
| `payload['prompt']` | The question sent to the model |
| `payload['text']` | One sentence of the answer, trimmed |
| `meta['turn']` | The `id` of the input message, the same for every sentence of an answer |
| `meta['sequence']` | Position of the sentence in the answer, from 0 |
| `meta['final']` | `true` on the last message of the answer |
| `meta['source']` | The `creator` of the input message |

A sentence ends at `.`, `!`, `?` or `…` followed by whitespace, or at a newline;
a piece shorter than 20 characters is joined to the next one. The rest of the
answer is transmitted when the model is done, with `final` set, even if it is
empty.

Each message keeps the version and the timers of the input message, and adds
a `<node name>` timer with the seconds from the arrival of the question to
that sentence: on the first sentence it is the time to the first sentence.

If the request fails (server down, timeout, HTTP error, an error reported in
the stream, connection closed before the end), the error is logged and counted
in the node `health` under `source_failures`. The sentences already
transmitted stay, the unfinished one is dropped, and no message is marked
`final`. An answer interrupted by a new question or by stopping the node has
no `final` message either. Stopping the node also drops the questions still
waiting: they are not answered after a restart.

## License

- **Runtime:** [Ollama](https://github.com/ollama/ollama), MIT. The node
  only calls its HTTP API.
- **Weights:** the license depends on the model you pull and set in
  `model_name`. The default `qwen2.5:1.5b` is Apache-2.0: the license layer
  of that tag in the Ollama registry is the Apache License 2.0 text, the
  [Ollama library page](https://ollama.com/library/qwen2.5) says all sizes
  except 3B and 72B are Apache 2.0 (those two are under the Qwen license),
  and the
  [Qwen/Qwen2.5-1.5B-Instruct](https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct)
  model card declares `apache-2.0` with an Apache 2.0 `LICENSE` file.
- **requests:** Apache-2.0 (the license of requests on PyPI),
  to call the Ollama API.

## Example

```json
{
  "name": "llm",
  "type": "PrompterOllama",
  "configuration": { "model_name": "qwen2.5:1.5b" }
}
```
