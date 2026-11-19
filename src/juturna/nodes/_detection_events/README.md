# DetectionEvents

Turn the detections attached to frames into small JSON events, with at most
one event per class every `interval` seconds.

- **Role:** processing
- **Node type:** `DetectionEvents`
- **Input:** `ImagePayload` with `meta['detections']`
- **Output:** `ObjectPayload`
- **Extra:** none

## How it works

The detections of a frame are grouped by label. A label produces an event
when its last event is at least `interval` seconds older, measured on the
`payload.timestamp` of the frames. Frames without detections produce nothing.
The time of the last event of each label is kept in the node state.

## Arguments

| Argument   | Type    | Default | Description |
| ---------- | ------- | ------- | ----------- |
| `interval` | `float` | `1.0`   | Minimum seconds between two events of the same label; `0` emits an event for every frame with the label |

## Input message

| Field | Use |
| --- | --- |
| `meta['detections']` | List of `{"label": str, "confidence": float, "bbox": [x1, y1, x2, y2]}`, in pixels. `DetectorYolox` produces it |
| `payload.timestamp` | Time of the frame, used for `interval` |
| `payload.width`, `payload.height` | Copied into the event |
| `version` | Copied into the event as `frame` |

The image itself is not read.

## Output message

One message per label that passes the interval, with the `version` of the
frame:

```json
{
  "event": "detection",
  "label": "person",
  "count": 2,
  "objects": [
    {"confidence": 0.87, "bbox": [12, 40, 210, 400]},
    {"confidence": 0.55, "bbox": [300, 52, 410, 380]}
  ],
  "frame": 152,
  "timestamp": 1763312345.12,
  "width": 640,
  "height": 480
}
```

## Limits

- Events are per label, not per object: there is no tracking.
- `DetectorYolo` keeps its ultralytics results in `meta['annotations']`,
  which this node does not read.

## License

- **Code:** this node is part of juturna-nodes, MIT (its `LICENSE` file).
- **Third-party runtime:** none beyond the juturna core (MIT); the node
  uses the Python standard library.

## Example

```json
{
  "name": "events",
  "type": "DetectionEvents",
  "configuration": { "interval": 2.0 }
}
```
