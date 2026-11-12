# NotifierHTTP

Send every received message to an HTTP endpoint, with a `POST` request.

- **Role:** sink
- **Node type:** `NotifierHTTP`
- **Input:** `ObjectPayload`
- **Output:** none
- **Extra:** none

## How it works

Messages are serialised and queued, and a dedicated worker sends them one at a
time, so a slow endpoint does not block the pipeline. The pipeline id is added
to the message as `meta['pipe_id']`.

Failed requests are logged and the message is dropped: there are no retries.
When the node stops, the worker is given a few seconds to drain the queue.

The `endpoint` can be changed at runtime through `set_on_config`.

## Arguments

| Argument       | Type  | Default                 | Description                                         |
| -------------- | ----- | ----------------------- | --------------------------------------------------- |
| `endpoint`     | `str` | `http://localhost:8080` | Destination URL, including the port                 |
| `timeout`      | `int` | `20`                    | Request timeout, in seconds                         |
| `content_type` | `str` | `application/json`      | `application/json` (message as a JSON object) or `text/plain` (message as a JSON string) |

## Example

```json
{
  "name": "3_dst",
  "type": "NotifierHTTP",
  "configuration": { "endpoint": "http://localhost:8080/transcripts" }
}
```
