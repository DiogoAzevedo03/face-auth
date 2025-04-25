# FaceAuth - Test Scripts

## Overview

This folder contains **testing scripts** used for local testing, validation, and debugging during development of the FaceAuth system. These scripts are particularly useful when working directly on a **Raspberry Pi** to ensure facial recognition components are functioning correctly.

---

## Scripts Included

### `test_camera.py`
- **Purpose:** Checks if the Raspberry Pi camera is properly connected and streams video.
- **How to run:**  
  ```bash
  python3 tests/test_camera.py
  ```
### generate_multiple_embeddings.py
Purpose: Captures face embeddings from a live camera feed using MobileFaceNet (TFLite).

Allows the user to append or wipe existing embeddings.

Saves embeddings to embeddings/<username>/ as .pkl files.

How to run:
```bash
python3 tests/generate_multiple_embeddings.py
```
### recognize.py
Purpose: Detects and identifies faces in real-time using previously captured embeddings.

Loads embeddings from embeddings/ and matches live faces to known users.

How to run:

```bash
python3 tests/recognize.py
```

### Requirements
All scripts rely on the following dependencies listed in the project's requirements.txt:

```bash
opencv-python
mediapipe
numpy
tflite-runtime
picamera2
Pillow
To install them:
```


```bash

pip install -r requirements.txt
```

### Note: These scripts require a connected camera and are intended to be run directly on a Raspberry Pi device.

### How It Works
Uses MediaPipe for face detection.

Uses MobileFaceNet (TFLite) to extract face embeddings.

Embeddings are stored using Pickle.

Real-time identification is based on distance threshold matching.