Tracker with YOLO
=================

## License note

This node needs the `vision` extra, which installs
[ultralytics](https://github.com/ultralytics/ultralytics). Ultralytics is
distributed under the AGPL-3.0 license, unlike juturna-nodes (MIT): check that
its terms are compatible with your use before installing it.

## Arguments

| Argument     | Type    | Default        | Description |
| ------------ | ------- | -------------- | ----------- |
| `model`      | `str`   | `"yolo11n.pt"` | Ultralytics model name or path |
| `device`     | `str`   | `"cpu"`        | `cpu`, or `cuda` to run on the GPU (it was the default up to juturna-nodes 0.1.1) |
| `targets`    | `list`  | `["person"]`   | Class names to detect; a name the model does not know fails the warmup |
| `confidence` | `float` | `0.25`         | Minimum score of a detection |
| `half`       | `bool`  | `true`         | Half precision |

## Input message

| Field | Use |
| --- | --- |
| `payload.image` | RGB `uint8` array of shape `(height, width, 3)`, as produced by `VideoCapture` and `VideoRtp`; it is passed to the model as BGR |

## Output message

The same `version` and timers as the input, and:

| Field | Content |
| --- | --- |
| `payload.image` | The RGB frame with boxes and labels drawn by ultralytics |
| `meta['detections']` | List of `{"label": str, "confidence": float, "bbox": [x1, y1, x2, y2]}`, with the box in pixels of the frame, as `DetectorYolox` produces it. Empty when nothing is found |
| `meta['annotations']` | The ultralytics `Results` object of the frame, a Python object that cannot be serialised to JSON |
