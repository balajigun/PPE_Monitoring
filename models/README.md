# Model Weights

This directory is reserved for the trained YOLO model weights used by the PPE Monitoring System.

## Required Model

The application expects the trained model to be available at:

```text
models/best.pt
```

The model is used for detecting:

- `Person`
- `Hardhat`
- `NO-Hardhat`
- `Safety Vest`
- `NO-Safety Vest`
- `Mask`
- `NO-Mask`

## Model Weights Not Included

The trained model weights are **not included in this GitHub repository**.

The following model files are intentionally excluded:

```text
*.pt
*.onnx
*.engine
```

This keeps the repository lightweight and prevents large binary model files from being committed.

## Setup

After cloning the repository, place the trained YOLO model in this directory:

```text
ppe-monitoring/
│
├── models/
│   ├── README.md
│   └── best.pt
```

The application can then load the model using the path configured in:

```text
src/config.py
```

Example:

```python
MODEL_PATH = "models/best.pt"
```

## Important

Do not commit model weights to the repository unless you have the appropriate rights to redistribute them.

The model weights should also not be uploaded if they contain proprietary or restricted training assets.