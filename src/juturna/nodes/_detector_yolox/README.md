# DetectorYolox

Detect objects in frames with a YOLOX model exported to ONNX, on ONNX Runtime,
and attach them to the frame as plain data.

- **Role:** processing
- **Node type:** `DetectorYolox`
- **Input:** `ImagePayload`, RGB
- **Output:** `ImagePayload`, the same frame, with `meta['detections']`
- **Extra:** `detector-yolox` (`pip install "juturna-nodes[detector-yolox]"`)

## How it works

On warmup the node loads the model and runs it once. `yolox_nano`,
`yolox_tiny` and `yolox_s` are downloaded on first use from the
[YOLOX releases](https://github.com/Megvii-BaseDetection/YOLOX/releases/tag/0.1.1rc0),
checked against a fixed size and sha256, and kept in
`$XDG_CACHE_HOME/juturna/models/` (`~/.cache/juturna/models/` by default).
Any other value of `model` is the path of a YOLOX `.onnx` file, exported
with a fixed square input (not `--dynamic`) and the 80 COCO classes.

For every frame, the image is scaled to the model input (416 px for nano and
tiny, 640 px for s) keeping its ratio, padded with grey, and converted to BGR.
The boxes are mapped back to the pixels of the original frame. Overlapping
boxes are merged whatever their class, as in the YOLOX demo.

Times on a laptop CPU, with onnxruntime 1.32:

| Model        | Input  | Download | Time per frame |
| ------------ | ------ | -------- | -------------- |
| `yolox_nano` | 416 px | 3.7 MB   | ~10 ms         |
| `yolox_tiny` | 416 px | 20 MB    | ~22 ms         |
| `yolox_s`    | 640 px | 36 MB    | ~70-100 ms     |

When the frames come faster than the model, they queue up: limit them at the
source (for example with the `fps` argument of `VideoCapture`).

## Arguments

| Argument     | Type    | Default        | Description |
| ------------ | ------- | -------------- | ----------- |
| `model`      | `str`   | `"yolox_nano"` | `yolox_nano`, `yolox_tiny`, `yolox_s`, or the path of a YOLOX `.onnx` file |
| `targets`    | `list`  | `[]`           | COCO class names to keep (`"person"`, `"car"`, ...); empty keeps all 80. An unknown name fails the build |
| `confidence` | `float` | `0.3`          | Minimum score of a detection |
| `nms`        | `float` | `0.45`         | Overlap (IoU) above which two boxes are merged |
| `device`     | `str`   | `"cpu"`        | `cpu`, or `cuda` with the `onnxruntime-gpu` package installed instead of `onnxruntime` |

## Input message

| Field | Use |
| --- | --- |
| `payload.image` | `uint8` RGB array of shape `(height, width, 3)`, as produced by `VideoCapture` and `VideoRtp` |

## Output message

The same payload, `version` and timers as the input, and:

| Field | Content |
| --- | --- |
| `meta['detections']` | List of `{"label": str, "confidence": float, "bbox": [x1, y1, x2, y2]}`, with the box in pixels of the frame. Empty when nothing is found |

`DetectionEvents` turns this list into JSON events.

## Limits

- The 80 COCO classes only. The boxes are not drawn on the frame.
- The resize uses the nearest pixel instead of the linear interpolation of
  the original YOLOX code: small objects may get slightly lower scores.

## License

- **Code:** the pre and post-processing of this node are ported from the
  YOLOX ONNXRuntime demo, in the
  [YOLOX repository](https://github.com/Megvii-BaseDetection/YOLOX), which
  Megvii releases under Apache-2.0 (its `LICENSE` file).
- **Weights:** `yolox_nano.onnx`, `yolox_tiny.onnx` and `yolox_s.onnx` are
  assets of the
  [0.1.1rc0 release](https://github.com/Megvii-BaseDetection/YOLOX/releases/tag/0.1.1rc0)
  of the same repository. Neither the release notes nor the repository
  README give them a separate license, so the Apache-2.0 of the repository
  is the only one stated. The models are trained on COCO.
- **requests:** Apache-2.0 (the license of requests on PyPI),
  to download the default models.
- **Runtime:** ONNX Runtime (`onnxruntime` on PyPI) is MIT licensed.

Unlike `DetectorYolo` (ultralytics, AGPL-3.0), none of these licenses is
copyleft.

## Example

```json
{
  "name": "detector",
  "type": "DetectorYolox",
  "configuration": { "model": "yolox_nano", "targets": ["person", "car"] }
}
```
