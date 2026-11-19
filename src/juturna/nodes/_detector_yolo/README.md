# DetectorYolo

## License note

This node needs the `vision` extra, which installs
[ultralytics](https://github.com/ultralytics/ultralytics). Ultralytics is
distributed under the AGPL-3.0 license, unlike juturna-nodes (MIT): check that
its terms are compatible with your use before installing it.

The YOLO weights (such as the default `yolo11n.pt`, which ultralytics
downloads from the releases of
[ultralytics/assets](https://github.com/ultralytics/assets)) are AGPL-3.0
as well: that repository is AGPL-3.0, and the
[Ultralytics/YOLO11](https://huggingface.co/Ultralytics/YOLO11) model card
declares `agpl-3.0`. Ultralytics also sells an Enterprise License that
lifts the AGPL-3.0 terms for its software and models
([ultralytics README](https://github.com/ultralytics/ultralytics#-license)).

The `vision` extra also installs PyTorch (BSD-3-Clause, its `LICENSE`
file) and opencv-python (Apache-2.0, its license on PyPI), which
ultralytics depends on.

Detect objects in frames with an Ultralytics YOLO model, and transmit the
frame with the boxes drawn on it.

- **Role:** processing
- **Node type:** `DetectorYolo`
- **Input:** `ImagePayload`
- **Output:** `ImagePayload`, the annotated frame
- **Extra:** `vision` (`pip install "juturna-nodes[vision]"`), AGPL-3.0

## How it works

On warmup the node loads `model` with ultralytics (a name such as
`yolo11n.pt` is downloaded by ultralytics on first use), moves it to
`device`, and runs it once on a black 640x640 image, so that the first real
frame does not pay the CUDA initialisation.

For every frame, the node runs one prediction restricted to the `targets`
classes and to scores of at least `confidence`, draws the result on the frame
with ultralytics (`Results.plot()`), and transmits the drawn frame with the
detections in `meta`. There is no tracking across frames: each frame is
detected on its own.

When the upstream stream stops, the node simply receives no more frames: it
keeps no state between frames and transmits nothing on its own.

## Arguments

| Argument     | Type    | Default        | Description |
| ------------ | ------- | -------------- | ----------- |
| `model`      | `str`   | `"yolo11n.pt"` | Ultralytics model name or path |
| `device`     | `str`   | `"cpu"`        | `cpu`, or `cuda` to run on the GPU (it was the default up to juturna-nodes 0.1.1) |
| `targets`    | `list`  | `["person"]`   | Class names to detect; a name the model does not know fails the warmup |
| `confidence` | `float` | `0.25`         | Minimum score of a detection |
| `half`       | `bool`  | `true`         | Half precision (`quantize=16` on ultralytics 8.4 and later, `half` before) |

## Input message

| Field | Use |
| --- | --- |
| `payload.image` | RGB `uint8` array of shape `(height, width, 3)`, as produced by `VideoCapture` and `VideoRtp`; it is passed to the model as BGR |
| `payload.pixel_format`, `payload.timestamp` | Copied to the output |

## Output message

The same `version` and timers as the input, and:

| Field | Content |
| --- | --- |
| `payload.image` | The RGB frame with boxes and labels drawn by ultralytics |
| `payload.width`, `payload.height`, `payload.depth` | Size of the drawn frame |
| `payload.pixel_format`, `payload.timestamp` | Copied from the input |
| `meta['detections']` | List of `{"label": str, "confidence": float, "bbox": [x1, y1, x2, y2]}`, with the box in pixels of the frame, as `DetectorYolox` produces it. Empty when nothing is found |
| `meta['annotations']` | The ultralytics `Results` object of the frame, a Python object that cannot be serialised to JSON |

## Limits

- `meta['annotations']` cannot be serialised to JSON as it is.
- When frames come faster than the model, they queue up: limit them at the
  source (for example with the `fps` argument of `VideoCapture`).

## Example

```json
{
  "name": "detector",
  "type": "DetectorYolo",
  "configuration": { "targets": ["person", "car"] }
}
```
